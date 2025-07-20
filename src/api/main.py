"""
RESTful API for LIHC Multi-omics Analysis Platform
FastAPI-based API with authentication, data management, and analysis endpoints
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np
import json
import uuid
from datetime import datetime, timedelta
import asyncio
from pathlib import Path
import tempfile
import os
from contextlib import asynccontextmanager

# Import our analysis modules
from src.data_processing.multi_omics_loader import MultiOmicsDataLoader, IntegrationResult
from src.data_processing.quality_control import DataQualityController, QualityReport
from src.analysis.closedloop_analyzer import ClosedLoopAnalyzer, ClosedLoopResult
from src.utils.logging_system import LIHCLogger
from src.utils.enhanced_config import get_system_config, get_analysis_config
from src.auth.jwt_auth import jwt_auth

# Initialize logger
logger = LIHCLogger(name="LIHC_API")

# Pydantic models for API requests/responses
class AnalysisRequest(BaseModel):
    """Analysis request model"""
    analysis_type: str = Field(..., description="Type of analysis to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Analysis parameters")
    target_genes: Optional[List[str]] = Field(None, description="Target genes for analysis")
    notification_email: Optional[str] = Field(None, description="Email for completion notification")

class AnalysisResponse(BaseModel):
    """Analysis response model"""
    analysis_id: str = Field(..., description="Unique analysis ID")
    status: str = Field(..., description="Analysis status")
    created_at: datetime = Field(..., description="Analysis creation time")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    progress: float = Field(0.0, description="Analysis progress (0-1)")
    message: str = Field("", description="Status message")

class DatasetInfo(BaseModel):
    """Dataset information model"""
    dataset_id: str = Field(..., description="Unique dataset ID")
    name: str = Field(..., description="Dataset name")
    data_type: str = Field(..., description="Type of omics data")
    samples: int = Field(..., description="Number of samples")
    features: int = Field(..., description="Number of features")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    quality_score: float = Field(..., description="Quality score (0-1)")
    status: str = Field(..., description="Dataset status")

class IntegrationRequest(BaseModel):
    """Multi-omics integration request"""
    dataset_ids: List[str] = Field(..., description="List of dataset IDs to integrate")
    integration_method: str = Field("standard", description="Integration method")
    quality_threshold: float = Field(0.8, description="Quality threshold for integration")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Integration parameters")

class UserModel(BaseModel):
    """User model"""
    user_id: str = Field(..., description="Unique user ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    role: str = Field("user", description="User role")
    created_at: datetime = Field(..., description="Account creation time")
    last_login: Optional[datetime] = Field(None, description="Last login time")

# Global storage for demo purposes (in production, use a proper database)
analysis_storage = {}
dataset_storage = {}
user_storage = {}

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token"""
    token = credentials.credentials
    
    # Get environment mode
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "development":
        # Allow demo token in development mode
        if token == "demo_token":
            return {"user_id": "demo_user", "username": "demo", "role": "admin"}
    
    # Production mode: use JWT authentication
    try:
        user_data = jwt_auth.get_user_from_token(token)
        return user_data
    except HTTPException:
        # Re-raise HTTP exceptions from JWT validation
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401, 
            detail="Authentication failed"
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("LIHC API starting up...")
    
    # Initialize storage directories
    Path("uploads").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    Path("temp").mkdir(exist_ok=True)
    
    # Initialize demo user
    user_storage["demo_user"] = UserModel(
        user_id="demo_user",
        username="demo",
        email="demo@lihc.ai",
        role="admin",
        created_at=datetime.now()
    )
    
    yield
    
    logger.info("LIHC API shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="LIHC Multi-omics Analysis Platform API",
    description="RESTful API for multi-omics cancer analysis with ClosedLoop causal inference",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
system_config = get_system_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=system_config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
from src.api.auth_endpoints import router as auth_router
app.include_router(auth_router)

# Root endpoint
@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LIHC Multi-omics Analysis Platform API",
        "version": "2.0.0",
        "features": [
            "Multi-omics data integration",
            "ClosedLoop causal inference",
            "Quality control analysis",
            "Real-time progress tracking"
        ],
        "endpoints": {
            "datasets": "/api/v1/datasets",
            "analysis": "/api/v1/analysis",
            "users": "/api/v1/users",
            "health": "/health"
        }
    }

# Health check endpoint
@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "uptime": "unknown"  # In production, track actual uptime
    }

# Dataset management endpoints
@app.post("/api/v1/datasets/upload", response_model=DatasetInfo, tags=["Data Management"])
async def upload_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    data_type: str = Form(...),
    description: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    """Upload a new dataset"""
    try:
        # Input validation
        if not name or len(name.strip()) == 0:
            raise HTTPException(status_code=400, detail="Dataset name is required")
        
        if len(name) > 200:
            raise HTTPException(status_code=400, detail="Dataset name too long (max 200 characters)")
        
        if not data_type or data_type not in ['rna_seq', 'cnv', 'mutation', 'methylation', 'clinical']:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size (10MB limit for demo)
        max_size = 10 * 1024 * 1024  # 10MB
        if hasattr(file, 'size') and file.size > max_size:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        # Validate file format
        allowed_extensions = ['.csv', '.tsv', '.xlsx', '.txt']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="Unsupported file format. Allowed: .csv, .tsv, .xlsx, .txt")
        
        # Sanitize filename
        import re
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
        
        # Generate unique dataset ID
        dataset_id = str(uuid.uuid4())
        
        # Save uploaded file with sanitized name
        upload_path = Path("uploads") / f"{dataset_id}_{safe_filename}"
        
        # Read file content with size limit
        content = await file.read(max_size)
        if len(content) == max_size:
            raise HTTPException(status_code=400, detail="File too large")
        
        with open(upload_path, "wb") as f:
            f.write(content)
        
        # Create dataset info
        dataset_info = DatasetInfo(
            dataset_id=dataset_id,
            name=name,
            data_type=data_type,
            samples=0,  # Will be updated after processing
            features=0,  # Will be updated after processing
            uploaded_at=datetime.now(),
            quality_score=0.0,  # Will be updated after quality check
            status="uploaded"
        )
        
        # Store dataset info
        dataset_storage[dataset_id] = {
            "info": dataset_info,
            "file_path": str(upload_path),
            "description": description,
            "owner": current_user["user_id"]
        }
        
        # Schedule background processing
        background_tasks.add_task(process_dataset, dataset_id)
        
        logger.info(f"Dataset uploaded: {dataset_id} by user {current_user['user_id']}")
        
        return dataset_info
        
    except Exception as e:
        logger.error(f"Dataset upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/v1/datasets", response_model=List[DatasetInfo], tags=["Data Management"])
async def list_datasets(
    data_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all datasets for the current user"""
    try:
        user_datasets = []
        for dataset_id, dataset_data in dataset_storage.items():
            if dataset_data["owner"] == current_user["user_id"]:
                dataset_info = dataset_data["info"]
                if data_type is None or dataset_info.data_type == data_type:
                    user_datasets.append(dataset_info)
        
        return user_datasets
        
    except Exception as e:
        logger.error(f"Failed to list datasets: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve datasets")

@app.get("/api/v1/datasets/{dataset_id}", response_model=DatasetInfo, tags=["Data Management"])
async def get_dataset(
    dataset_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific dataset information"""
    if dataset_id not in dataset_storage:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset_data = dataset_storage[dataset_id]
    if dataset_data["owner"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return dataset_data["info"]

@app.delete("/api/v1/datasets/{dataset_id}", tags=["Data Management"])
async def delete_dataset(
    dataset_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a dataset"""
    if dataset_id not in dataset_storage:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset_data = dataset_storage[dataset_id]
    if dataset_data["owner"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Delete file
        file_path = Path(dataset_data["file_path"])
        if file_path.exists():
            file_path.unlink()
        
        # Remove from storage
        del dataset_storage[dataset_id]
        
        logger.info(f"Dataset deleted: {dataset_id}")
        
        return {"message": "Dataset deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete dataset: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete dataset")

# Multi-omics integration endpoints
@app.post("/api/v1/integration", response_model=AnalysisResponse, tags=["Analysis"])
async def create_integration(
    request: IntegrationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create multi-omics integration analysis"""
    try:
        # Validate dataset IDs
        for dataset_id in request.dataset_ids:
            if dataset_id not in dataset_storage:
                raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
            
            dataset_data = dataset_storage[dataset_id]
            if dataset_data["owner"] != current_user["user_id"]:
                raise HTTPException(status_code=403, detail="Access denied to dataset")
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Create analysis record
        analysis_record = AnalysisResponse(
            analysis_id=analysis_id,
            status="queued",
            created_at=datetime.now(),
            estimated_completion=datetime.now() + timedelta(minutes=10),
            progress=0.0,
            message="Analysis queued for processing"
        )
        
        # Store analysis info
        analysis_storage[analysis_id] = {
            "response": analysis_record,
            "request": request,
            "owner": current_user["user_id"],
            "type": "integration"
        }
        
        # Schedule background processing
        background_tasks.add_task(run_integration_analysis, analysis_id)
        
        logger.info(f"Integration analysis created: {analysis_id}")
        
        return analysis_record
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create integration: {e}")
        raise HTTPException(status_code=500, detail="Failed to create integration")

# ClosedLoop analysis endpoints
@app.post("/api/v1/analysis/closedloop", response_model=AnalysisResponse, tags=["Analysis"])
async def create_closedloop_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create ClosedLoop causal inference analysis"""
    try:
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Create analysis record
        analysis_record = AnalysisResponse(
            analysis_id=analysis_id,
            status="queued",
            created_at=datetime.now(),
            estimated_completion=datetime.now() + timedelta(minutes=15),
            progress=0.0,
            message="ClosedLoop analysis queued for processing"
        )
        
        # Store analysis info
        analysis_storage[analysis_id] = {
            "response": analysis_record,
            "request": request,
            "owner": current_user["user_id"],
            "type": "closedloop"
        }
        
        # Schedule background processing
        background_tasks.add_task(run_closedloop_analysis, analysis_id)
        
        logger.info(f"ClosedLoop analysis created: {analysis_id}")
        
        return analysis_record
        
    except Exception as e:
        logger.error(f"Failed to create ClosedLoop analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to create analysis")

@app.get("/api/v1/analysis", response_model=List[AnalysisResponse], tags=["Analysis"])
async def list_analyses(
    status: Optional[str] = None,
    analysis_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all analyses for the current user"""
    try:
        user_analyses = []
        for analysis_id, analysis_data in analysis_storage.items():
            if analysis_data["owner"] == current_user["user_id"]:
                analysis_response = analysis_data["response"]
                
                # Filter by status if specified
                if status and analysis_response.status != status:
                    continue
                
                # Filter by type if specified
                if analysis_type and analysis_data["type"] != analysis_type:
                    continue
                
                user_analyses.append(analysis_response)
        
        return user_analyses
        
    except Exception as e:
        logger.error(f"Failed to list analyses: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analyses")

@app.get("/api/v1/analysis/{analysis_id}", response_model=AnalysisResponse, tags=["Analysis"])
async def get_analysis_status(
    analysis_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get analysis status and progress"""
    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis_data = analysis_storage[analysis_id]
    if analysis_data["owner"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return analysis_data["response"]

@app.get("/api/v1/analysis/{analysis_id}/results", tags=["Analysis"])
async def get_analysis_results(
    analysis_id: str,
    format: str = "json",
    current_user: dict = Depends(get_current_user)
):
    """Get analysis results"""
    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis_data = analysis_storage[analysis_id]
    if analysis_data["owner"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if analysis_data["response"].status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    try:
        # Load results from file
        results_path = Path("results") / f"{analysis_id}_results.json"
        if not results_path.exists():
            raise HTTPException(status_code=404, detail="Results not found")
        
        if format == "json":
            with open(results_path, "r") as f:
                results = json.load(f)
            return results
        elif format == "csv":
            # Convert to CSV and return as file
            csv_path = Path("results") / f"{analysis_id}_results.csv"
            if csv_path.exists():
                return FileResponse(csv_path, media_type="text/csv", filename=f"analysis_{analysis_id}.csv")
            else:
                raise HTTPException(status_code=404, detail="CSV results not available")
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve results: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve results")

@app.delete("/api/v1/analysis/{analysis_id}", tags=["Analysis"])
async def delete_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an analysis"""
    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis_data = analysis_storage[analysis_id]
    if analysis_data["owner"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Delete results files
        results_path = Path("results") / f"{analysis_id}_results.json"
        if results_path.exists():
            results_path.unlink()
        
        csv_path = Path("results") / f"{analysis_id}_results.csv"
        if csv_path.exists():
            csv_path.unlink()
        
        # Remove from storage
        del analysis_storage[analysis_id]
        
        logger.info(f"Analysis deleted: {analysis_id}")
        
        return {"message": "Analysis deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete analysis")

# User management endpoints
@app.get("/api/v1/users/profile", response_model=UserModel, tags=["User Management"])
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    user_id = current_user["user_id"]
    if user_id not in user_storage:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_storage[user_id]

@app.put("/api/v1/users/profile", response_model=UserModel, tags=["User Management"])
async def update_user_profile(
    username: str = Form(...),
    email: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    user_id = current_user["user_id"]
    if user_id not in user_storage:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        user = user_storage[user_id]
        user.username = username
        user.email = email
        
        logger.info(f"User profile updated: {user_id}")
        
        return user
        
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

# Background task functions
async def process_dataset(dataset_id: str):
    """Process uploaded dataset in background"""
    try:
        dataset_data = dataset_storage[dataset_id]
        file_path = dataset_data["file_path"]
        
        # Load and analyze dataset
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, index_col=0)
        elif file_path.endswith('.tsv'):
            df = pd.read_csv(file_path, sep='\t', index_col=0)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path, index_col=0)
        
        # Update dataset info
        dataset_data["info"].samples = df.shape[0]
        dataset_data["info"].features = df.shape[1]
        dataset_data["info"].status = "processing"
        
        # Perform quality check
        qc = DataQualityController()
        quality_report = qc.assess_data_quality(df, dataset_data["info"].name)
        
        # Update quality score
        dataset_data["info"].quality_score = quality_report.overall_quality_score
        dataset_data["info"].status = "ready"
        
        logger.info(f"Dataset processed: {dataset_id}")
        
    except Exception as e:
        logger.error(f"Dataset processing failed: {e}")
        dataset_storage[dataset_id]["info"].status = "error"

async def run_integration_analysis(analysis_id: str):
    """Run multi-omics integration analysis in background"""
    try:
        analysis_data = analysis_storage[analysis_id]
        analysis_data["response"].status = "running"
        analysis_data["response"].progress = 0.1
        analysis_data["response"].message = "Loading datasets..."
        
        # Simulate analysis progress
        await asyncio.sleep(2)
        analysis_data["response"].progress = 0.3
        analysis_data["response"].message = "Integrating datasets..."
        
        await asyncio.sleep(3)
        analysis_data["response"].progress = 0.6
        analysis_data["response"].message = "Performing quality checks..."
        
        await asyncio.sleep(2)
        analysis_data["response"].progress = 0.9
        analysis_data["response"].message = "Generating results..."
        
        # Generate mock results
        results = {
            "analysis_id": analysis_id,
            "type": "integration",
            "status": "completed",
            "results": {
                "integrated_samples": 150,
                "data_types": ["rna_seq", "cnv", "mutation", "methylation"],
                "total_features": 1950,
                "quality_metrics": {
                    "overall_quality": 0.85,
                    "data_completeness": 0.92,
                    "consistency_score": 0.88
                }
            },
            "completed_at": datetime.now().isoformat()
        }
        
        # Save results
        results_path = Path("results") / f"{analysis_id}_results.json"
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        # Update analysis status
        analysis_data["response"].status = "completed"
        analysis_data["response"].progress = 1.0
        analysis_data["response"].message = "Analysis completed successfully"
        
        logger.info(f"Integration analysis completed: {analysis_id}")
        
    except Exception as e:
        logger.error(f"Integration analysis failed: {e}")
        analysis_storage[analysis_id]["response"].status = "failed"
        analysis_storage[analysis_id]["response"].message = f"Analysis failed: {str(e)}"

async def run_closedloop_analysis(analysis_id: str):
    """Run ClosedLoop causal analysis in background"""
    try:
        analysis_data = analysis_storage[analysis_id]
        analysis_data["response"].status = "running"
        analysis_data["response"].progress = 0.1
        analysis_data["response"].message = "Initializing ClosedLoop analysis..."
        
        # Simulate analysis progress
        await asyncio.sleep(2)
        analysis_data["response"].progress = 0.3
        analysis_data["response"].message = "Collecting evidence..."
        
        await asyncio.sleep(4)
        analysis_data["response"].progress = 0.6
        analysis_data["response"].message = "Calculating causal scores..."
        
        await asyncio.sleep(3)
        analysis_data["response"].progress = 0.8
        analysis_data["response"].message = "Building evidence networks..."
        
        await asyncio.sleep(2)
        analysis_data["response"].progress = 0.95
        analysis_data["response"].message = "Generating results..."
        
        # Generate mock results
        results = {
            "analysis_id": analysis_id,
            "type": "closedloop",
            "status": "completed",
            "results": {
                "causal_genes": [
                    {"gene_id": "TP53", "causal_score": 0.92, "confidence": "High"},
                    {"gene_id": "MYC", "causal_score": 0.87, "confidence": "High"},
                    {"gene_id": "EGFR", "causal_score": 0.81, "confidence": "Medium"}
                ],
                "evidence_network": {
                    "nodes": 15,
                    "edges": 28
                },
                "validation_metrics": {
                    "cross_validation_score": 0.78,
                    "bootstrap_stability": 0.82,
                    "literature_support": 0.85
                },
                "pathway_analysis": {
                    "enriched_pathways": 12,
                    "top_pathway": "p53 signaling pathway"
                }
            },
            "completed_at": datetime.now().isoformat()
        }
        
        # Save results
        results_path = Path("results") / f"{analysis_id}_results.json"
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        # Update analysis status
        analysis_data["response"].status = "completed"
        analysis_data["response"].progress = 1.0
        analysis_data["response"].message = "ClosedLoop analysis completed successfully"
        
        logger.info(f"ClosedLoop analysis completed: {analysis_id}")
        
    except Exception as e:
        logger.error(f"ClosedLoop analysis failed: {e}")
        analysis_storage[analysis_id]["response"].status = "failed"
        analysis_storage[analysis_id]["response"].message = f"Analysis failed: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    
    system_config = get_system_config()
    uvicorn.run(
        "api:app",
        host=system_config.host,
        port=system_config.port,
        reload=system_config.debug,
        log_level="info"
    )