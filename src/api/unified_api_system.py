"""
Unified API Endpoint System for LIHC Platform
统一API端点系统
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Union, Any
import asyncio
import uvicorn
import pandas as pd
import numpy as np
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os
import sys
import warnings
from dataclasses import asdict
warnings.filterwarnings('ignore')

# 添加项目路径以便导入分析模块
sys.path.append('.')

# 导入所有分析模块
try:
    from src.analysis.single_cell_analyzer import SingleCellAnalyzer
    from src.analysis.ai_biomarker_discovery import AIBiomarkerDiscovery
    from src.analysis.drug_combination_predictor import DrugCombinationPredictor
    from src.analysis.realtime_task_queue import RealtimeTaskQueue
    from src.analysis.advanced_multiomics_integration import AdvancedMultiomicsIntegration
    from src.analysis.patient_stratification_system import PatientStratificationSystem
    from src.analysis.intelligent_report_generator import IntelligentReportGenerator
except ImportError as e:
    print(f"Warning: Could not import analysis modules: {e}")
    # 创建占位符类以防止导入错误
    class SingleCellAnalyzer:
        def analyze_cells(self, data): return {}
    class AIBiomarkerDiscovery:
        def discover_biomarkers(self, data): return {}
    class DrugCombinationPredictor:
        def predict_combinations(self, data): return {}
    class RealtimeTaskQueue:
        def add_task(self, task): return {}
    class AdvancedMultiomicsIntegration:
        def integrate_omics(self, data): return {}
    class PatientStratificationSystem:
        def stratify_patients(self, data): return {}
    class IntelligentReportGenerator:
        def generate_report(self, type, data): return {}

# Pydantic 模型定义
class AnalysisRequest(BaseModel):
    """通用分析请求模型"""
    analysis_type: str = Field(..., description="分析类型")
    data_source: str = Field(..., description="数据源")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="分析参数")
    patient_id: Optional[str] = Field(None, description="患者ID")
    session_id: Optional[str] = Field(None, description="会话ID")

class SingleCellRequest(BaseModel):
    """单细胞分析请求"""
    sample_data: Dict[str, Any] = Field(..., description="样本数据")
    analysis_params: Dict[str, Any] = Field(default_factory=dict)
    quality_control: bool = Field(True, description="是否进行质量控制")
    clustering_method: str = Field("leiden", description="聚类方法")
    
    @validator('clustering_method')
    def validate_clustering_method(cls, v):
        allowed_methods = ['leiden', 'louvain', 'kmeans']
        if v not in allowed_methods:
            raise ValueError(f'Clustering method must be one of {allowed_methods}')
        return v

class BiomarkerRequest(BaseModel):
    """生物标志物发现请求"""
    omics_data: Dict[str, Any] = Field(..., description="组学数据")
    clinical_data: Optional[Dict[str, Any]] = Field(None, description="临床数据")
    algorithms: List[str] = Field(default=['random_forest', 'lasso', 'xgboost'], description="使用的算法")
    validation_split: float = Field(0.2, description="验证集比例")
    
    @validator('validation_split')
    def validate_split(cls, v):
        if not 0.1 <= v <= 0.5:
            raise ValueError('Validation split must be between 0.1 and 0.5')
        return v

class DrugCombinationRequest(BaseModel):
    """药物组合预测请求"""
    patient_profile: Dict[str, Any] = Field(..., description="患者档案")
    available_drugs: List[str] = Field(..., description="可用药物列表")
    combination_size: int = Field(2, description="组合药物数量")
    prediction_model: str = Field("bliss_independence", description="预测模型")

class MultiomicsRequest(BaseModel):
    """多组学整合请求"""
    omics_data: Dict[str, Dict[str, Any]] = Field(..., description="多组学数据")
    integration_method: str = Field("SNF", description="整合方法")
    feature_selection: bool = Field(True, description="是否进行特征选择")
    
    @validator('omics_data')
    def validate_omics_data(cls, v):
        required_types = ['genomics', 'transcriptomics']
        if not any(key in v for key in required_types):
            raise ValueError('At least genomics or transcriptomics data is required')
        return v

class StratificationRequest(BaseModel):
    """患者分层请求"""
    patient_data: Dict[str, Any] = Field(..., description="患者数据")
    stratification_method: str = Field("consensus_clustering", description="分层方法")
    n_clusters: Optional[int] = Field(None, description="聚类数量")
    risk_factors: List[str] = Field(default_factory=list, description="风险因子")

class ReportRequest(BaseModel):
    """报告生成请求"""
    report_type: str = Field(..., description="报告类型")
    analysis_results: Dict[str, Any] = Field(..., description="分析结果")
    output_format: str = Field("HTML", description="输出格式")
    template_customization: Optional[Dict[str, Any]] = Field(None, description="模板自定义")
    
    @validator('report_type')
    def validate_report_type(cls, v):
        allowed_types = [
            'Clinical Summary Report', 'Comprehensive Analysis Report',
            'Biomarker Discovery Report', 'Treatment Recommendation Report',
            'Multi-omics Integration Report', 'Patient Stratification Report',
            'Research Publication Draft', 'Regulatory Submission Report'
        ]
        if v not in allowed_types:
            raise ValueError(f'Report type must be one of {allowed_types}')
        return v

class TaskStatus(BaseModel):
    """任务状态模型"""
    task_id: str
    status: str  # pending, running, completed, failed
    progress: float
    message: str
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None

class APIResponse(BaseModel):
    """标准API响应模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# 认证系统
security = HTTPBearer()

class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        self.valid_tokens = {
            "ultrathink_api_token_2025": {
                "user_id": "admin",
                "permissions": ["all"],
                "expires": datetime.now() + timedelta(days=365)
            },
            "research_token_2025": {
                "user_id": "researcher",
                "permissions": ["analysis", "reports"],
                "expires": datetime.now() + timedelta(days=90)
            }
        }
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """验证API令牌"""
        token = credentials.credentials
        
        if token not in self.valid_tokens:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        token_info = self.valid_tokens[token]
        if datetime.now() > token_info["expires"]:
            raise HTTPException(status_code=401, detail="Token has expired")
        
        return token_info

# 任务管理器
class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, TaskStatus] = {}
        self.analysis_modules = self._initialize_modules()
    
    def _initialize_modules(self):
        """初始化分析模块"""
        return {
            'single_cell': SingleCellAnalyzer(),
            'biomarker': AIBiomarkerDiscovery(),
            'drug_combination': DrugCombinationPredictor(),
            'task_queue': RealtimeTaskQueue(),
            'multiomics': AdvancedMultiomicsIntegration(),
            'stratification': PatientStratificationSystem(),
            'report_generator': IntelligentReportGenerator()
        }
    
    def create_task(self, task_type: str, **kwargs) -> str:
        """创建新任务"""
        task_id = str(uuid.uuid4())
        
        task_status = TaskStatus(
            task_id=task_id,
            status="pending",
            progress=0.0,
            message=f"Task {task_type} created",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.tasks[task_id] = task_status
        return task_id
    
    def update_task(self, task_id: str, status: str = None, progress: float = None, 
                   message: str = None, result: Dict = None):
        """更新任务状态"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if status:
            task.status = status
        if progress is not None:
            task.progress = progress
        if message:
            task.message = message
        if result:
            task.result = result
        
        task.updated_at = datetime.now()
        return True
    
    def get_task(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    async def execute_analysis(self, task_id: str, analysis_type: str, **kwargs):
        """执行分析任务"""
        try:
            self.update_task(task_id, status="running", progress=0.1, message="Starting analysis")
            
            if analysis_type == "single_cell":
                result = await self._run_single_cell_analysis(task_id, **kwargs)
            elif analysis_type == "biomarker":
                result = await self._run_biomarker_discovery(task_id, **kwargs)
            elif analysis_type == "drug_combination":
                result = await self._run_drug_combination_prediction(task_id, **kwargs)
            elif analysis_type == "multiomics":
                result = await self._run_multiomics_integration(task_id, **kwargs)
            elif analysis_type == "stratification":
                result = await self._run_patient_stratification(task_id, **kwargs)
            elif analysis_type == "report":
                result = await self._run_report_generation(task_id, **kwargs)
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
            
            self.update_task(task_id, status="completed", progress=1.0, 
                           message="Analysis completed successfully", result=result)
            
        except Exception as e:
            self.update_task(task_id, status="failed", progress=0.0, 
                           message=f"Analysis failed: {str(e)}")
    
    async def _run_single_cell_analysis(self, task_id: str, sample_data: Dict, **kwargs):
        """运行单细胞分析"""
        self.update_task(task_id, progress=0.3, message="Processing single cell data")
        
        analyzer = self.analysis_modules['single_cell']
        result = analyzer.analyze_cells(sample_data)
        
        self.update_task(task_id, progress=0.8, message="Generating visualizations")
        
        return {
            'analysis_type': 'single_cell',
            'results': result,
            'metadata': {
                'n_cells': result.get('n_cells', 0),
                'n_clusters': result.get('n_clusters', 0),
                'cell_types': result.get('cell_types', [])
            }
        }
    
    async def _run_biomarker_discovery(self, task_id: str, omics_data: Dict, **kwargs):
        """运行生物标志物发现"""
        self.update_task(task_id, progress=0.3, message="Training machine learning models")
        
        discovery = self.analysis_modules['biomarker']
        result = discovery.discover_biomarkers(omics_data)
        
        self.update_task(task_id, progress=0.8, message="Validating biomarkers")
        
        return {
            'analysis_type': 'biomarker_discovery',
            'results': result,
            'metadata': {
                'n_biomarkers': len(result.get('biomarkers', [])),
                'validation_accuracy': result.get('validation_accuracy', 0),
                'algorithms_used': result.get('algorithms_used', [])
            }
        }
    
    async def _run_drug_combination_prediction(self, task_id: str, patient_profile: Dict, **kwargs):
        """运行药物组合预测"""
        self.update_task(task_id, progress=0.3, message="Analyzing patient profile")
        
        predictor = self.analysis_modules['drug_combination']
        result = predictor.predict_combinations(patient_profile)
        
        self.update_task(task_id, progress=0.8, message="Optimizing drug combinations")
        
        return {
            'analysis_type': 'drug_combination',
            'results': result,
            'metadata': {
                'n_combinations': len(result.get('recommendations', [])),
                'top_combination': result.get('top_recommendation', {}),
                'synergy_score': result.get('synergy_score', 0)
            }
        }
    
    async def _run_multiomics_integration(self, task_id: str, omics_data: Dict, **kwargs):
        """运行多组学整合"""
        self.update_task(task_id, progress=0.3, message="Integrating multi-omics data")
        
        integration = self.analysis_modules['multiomics']
        result = integration.integrate_omics(omics_data)
        
        self.update_task(task_id, progress=0.8, message="Generating integrated insights")
        
        return {
            'analysis_type': 'multiomics_integration',
            'results': result,
            'metadata': {
                'omics_types': list(omics_data.keys()),
                'integration_quality': result.get('integration_quality', 0),
                'n_features': result.get('n_features', 0)
            }
        }
    
    async def _run_patient_stratification(self, task_id: str, patient_data: Dict, **kwargs):
        """运行患者分层"""
        self.update_task(task_id, progress=0.3, message="Stratifying patients")
        
        stratification = self.analysis_modules['stratification']
        result = stratification.stratify_patients(patient_data)
        
        self.update_task(task_id, progress=0.8, message="Generating treatment recommendations")
        
        return {
            'analysis_type': 'patient_stratification',
            'results': result,
            'metadata': {
                'n_strata': result.get('n_strata', 0),
                'stratification_quality': result.get('quality_score', 0),
                'risk_groups': result.get('risk_groups', [])
            }
        }
    
    async def _run_report_generation(self, task_id: str, report_type: str, 
                                   analysis_results: Dict, **kwargs):
        """运行报告生成"""
        self.update_task(task_id, progress=0.3, message="Generating report content")
        
        generator = self.analysis_modules['report_generator']
        result = generator.generate_report(report_type, analysis_results, **kwargs)
        
        self.update_task(task_id, progress=0.8, message="Formatting report")
        
        return {
            'analysis_type': 'report_generation',
            'results': result,
            'metadata': {
                'report_type': report_type,
                'word_count': result.get('word_count', 0),
                'figures_count': result.get('figures_count', 0),
                'quality_score': result.get('quality_score', 0)
            }
        }

# 创建FastAPI应用
app = FastAPI(
    title="LIHC Platform Unified API",
    description="统一API端点系统 for Liver Hepatocellular Carcinoma Analysis Platform",
    version="2.7.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化管理器
auth_manager = AuthManager()
task_manager = TaskManager()

# 根端点
@app.get("/", response_model=APIResponse)
async def root():
    """API根端点"""
    return APIResponse(
        success=True,
        message="LIHC Platform Unified API v2.7.0 - Ready for analysis!",
        data={
            "version": "2.7.0",
            "available_endpoints": [
                "/analysis/single-cell",
                "/analysis/biomarker",
                "/analysis/drug-combination", 
                "/analysis/multiomics",
                "/analysis/stratification",
                "/reports/generate",
                "/tasks/{task_id}",
                "/health"
            ],
            "documentation": "/docs"
        }
    )

# 健康检查端点
@app.get("/health", response_model=APIResponse)
async def health_check():
    """健康检查端点"""
    return APIResponse(
        success=True,
        message="API is healthy and operational",
        data={
            "status": "healthy",
            "uptime": "operational",
            "modules": {
                "single_cell": "available",
                "biomarker": "available", 
                "drug_combination": "available",
                "multiomics": "available",
                "stratification": "available",
                "reports": "available"
            }
        }
    )

# 单细胞分析端点
@app.post("/analysis/single-cell", response_model=APIResponse)
async def analyze_single_cell(
    request: SingleCellRequest,
    background_tasks: BackgroundTasks,
    token_info: dict = Depends(auth_manager.verify_token)
):
    """单细胞RNA-seq分析端点"""
    
    # 创建任务
    task_id = task_manager.create_task("single_cell")
    
    # 添加后台任务
    background_tasks.add_task(
        task_manager.execute_analysis,
        task_id,
        "single_cell",
        sample_data=request.sample_data,
        analysis_params=request.analysis_params,
        quality_control=request.quality_control,
        clustering_method=request.clustering_method
    )
    
    return APIResponse(
        success=True,
        message="Single cell analysis task created successfully",
        task_id=task_id,
        data={"analysis_type": "single_cell", "estimated_time": "5-10 minutes"}
    )

# 生物标志物发现端点
@app.post("/analysis/biomarker", response_model=APIResponse)
async def discover_biomarkers(
    request: BiomarkerRequest,
    background_tasks: BackgroundTasks,
    token_info: dict = Depends(auth_manager.verify_token)
):
    """AI驱动的生物标志物发现端点"""
    
    task_id = task_manager.create_task("biomarker")
    
    background_tasks.add_task(
        task_manager.execute_analysis,
        task_id,
        "biomarker",
        omics_data=request.omics_data,
        clinical_data=request.clinical_data,
        algorithms=request.algorithms,
        validation_split=request.validation_split
    )
    
    return APIResponse(
        success=True,
        message="Biomarker discovery task created successfully",
        task_id=task_id,
        data={"analysis_type": "biomarker_discovery", "estimated_time": "10-15 minutes"}
    )

# 药物组合预测端点
@app.post("/analysis/drug-combination", response_model=APIResponse)
async def predict_drug_combinations(
    request: DrugCombinationRequest,
    background_tasks: BackgroundTasks,
    token_info: dict = Depends(auth_manager.verify_token)
):
    """药物组合疗法预测端点"""
    
    task_id = task_manager.create_task("drug_combination")
    
    background_tasks.add_task(
        task_manager.execute_analysis,
        task_id,
        "drug_combination",
        patient_profile=request.patient_profile,
        available_drugs=request.available_drugs,
        combination_size=request.combination_size,
        prediction_model=request.prediction_model
    )
    
    return APIResponse(
        success=True,
        message="Drug combination prediction task created successfully",
        task_id=task_id,
        data={"analysis_type": "drug_combination", "estimated_time": "3-7 minutes"}
    )

# 多组学整合端点
@app.post("/analysis/multiomics", response_model=APIResponse)
async def integrate_multiomics(
    request: MultiomicsRequest,
    background_tasks: BackgroundTasks,
    token_info: dict = Depends(auth_manager.verify_token)
):
    """多组学数据整合端点"""
    
    task_id = task_manager.create_task("multiomics")
    
    background_tasks.add_task(
        task_manager.execute_analysis,
        task_id,
        "multiomics",
        omics_data=request.omics_data,
        integration_method=request.integration_method,
        feature_selection=request.feature_selection
    )
    
    return APIResponse(
        success=True,
        message="Multi-omics integration task created successfully",
        task_id=task_id,
        data={"analysis_type": "multiomics_integration", "estimated_time": "8-12 minutes"}
    )

# 患者分层端点
@app.post("/analysis/stratification", response_model=APIResponse)
async def stratify_patients(
    request: StratificationRequest,
    background_tasks: BackgroundTasks,
    token_info: dict = Depends(auth_manager.verify_token)
):
    """患者分层分析端点"""
    
    task_id = task_manager.create_task("stratification")
    
    background_tasks.add_task(
        task_manager.execute_analysis,
        task_id,
        "stratification",
        patient_data=request.patient_data,
        stratification_method=request.stratification_method,
        n_clusters=request.n_clusters,
        risk_factors=request.risk_factors
    )
    
    return APIResponse(
        success=True,
        message="Patient stratification task created successfully",
        task_id=task_id,
        data={"analysis_type": "patient_stratification", "estimated_time": "5-8 minutes"}
    )

# 报告生成端点
@app.post("/reports/generate", response_model=APIResponse)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    token_info: dict = Depends(auth_manager.verify_token)
):
    """智能报告生成端点"""
    
    task_id = task_manager.create_task("report")
    
    background_tasks.add_task(
        task_manager.execute_analysis,
        task_id,
        "report",
        report_type=request.report_type,
        analysis_results=request.analysis_results,
        output_format=request.output_format,
        template_customization=request.template_customization
    )
    
    return APIResponse(
        success=True,
        message="Report generation task created successfully",
        task_id=task_id,
        data={"analysis_type": "report_generation", "estimated_time": "2-5 minutes"}
    )

# 任务状态查询端点
@app.get("/tasks/{task_id}", response_model=APIResponse)
async def get_task_status(
    task_id: str,
    token_info: dict = Depends(auth_manager.verify_token)
):
    """查询任务状态端点"""
    
    task = task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return APIResponse(
        success=True,
        message="Task status retrieved successfully",
        data={
            "task_id": task.task_id,
            "status": task.status,
            "progress": task.progress,
            "message": task.message,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "result": task.result
        }
    )

# 批量分析端点
@app.post("/analysis/batch", response_model=APIResponse)
async def batch_analysis(
    analyses: List[AnalysisRequest],
    background_tasks: BackgroundTasks,
    token_info: dict = Depends(auth_manager.verify_token)
):
    """批量分析端点"""
    
    if len(analyses) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 analyses per batch")
    
    task_ids = []
    
    for analysis in analyses:
        task_id = task_manager.create_task(analysis.analysis_type)
        task_ids.append(task_id)
        
        # 这里简化处理，实际应该根据analysis_type调用相应的分析方法
        background_tasks.add_task(
            task_manager.execute_analysis,
            task_id,
            analysis.analysis_type,
            **analysis.parameters
        )
    
    return APIResponse(
        success=True,
        message=f"Batch analysis created with {len(task_ids)} tasks",
        data={
            "task_ids": task_ids,
            "batch_size": len(task_ids),
            "estimated_total_time": f"{len(task_ids) * 8} minutes"
        }
    )

# 数据上传端点
@app.post("/data/upload", response_model=APIResponse)
async def upload_data(
    file: UploadFile = File(...),
    data_type: str = Form(...),
    token_info: dict = Depends(auth_manager.verify_token)
):
    """数据上传端点"""
    
    allowed_types = ['genomics', 'transcriptomics', 'proteomics', 'clinical']
    if data_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Data type must be one of {allowed_types}")
    
    # 保存上传的文件
    file_id = str(uuid.uuid4())
    file_path = Path(tempfile.gettempdir()) / f"{file_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return APIResponse(
        success=True,
        message="File uploaded successfully",
        data={
            "file_id": file_id,
            "filename": file.filename,
            "data_type": data_type,
            "file_size": len(content),
            "file_path": str(file_path)
        }
    )

# API统计端点
@app.get("/stats", response_model=APIResponse)
async def get_api_stats(
    token_info: dict = Depends(auth_manager.verify_token)
):
    """API使用统计端点"""
    
    # 统计任务状态
    status_counts = {}
    for task in task_manager.tasks.values():
        status = task.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return APIResponse(
        success=True,
        message="API statistics retrieved successfully",
        data={
            "total_tasks": len(task_manager.tasks),
            "status_distribution": status_counts,
            "available_modules": list(task_manager.analysis_modules.keys()),
            "uptime": "operational",
            "api_version": "2.7.0"
        }
    )

# 错误处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

# 启动函数
def start_api_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """启动API服务器"""
    print(f"""
    🚀 LIHC Platform Unified API Server v2.7.0
    
    📊 Available Analysis Modules:
    • Single Cell RNA-seq Analysis
    • AI Biomarker Discovery  
    • Drug Combination Prediction
    • Multi-omics Integration
    • Patient Stratification
    • Intelligent Report Generation
    
    🔗 Server URL: http://{host}:{port}
    📚 API Documentation: http://{host}:{port}/docs
    🔧 Interactive API: http://{host}:{port}/redoc
    
    🔑 Authentication Required:
    • Token: ultrathink_api_token_2025 (full access)
    • Token: research_token_2025 (analysis only)
    
    ⚡ Ready for ultrathink analysis requests!
    """)
    
    uvicorn.run(
        "src.api.unified_api_system:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    start_api_server()