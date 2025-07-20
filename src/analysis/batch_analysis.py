"""
Batch Analysis System for LIHC Platform
Handles large-scale multi-dataset analyses with job queuing
"""

import asyncio
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from src.data_processing.multi_omics_loader import MultiOmicsDataLoader, IntegrationResult
from src.analysis.closedloop_analyzer import ClosedLoopAnalyzer, ClosedLoopResult
from src.data_processing.quality_control import DataQualityController
from src.utils.logging_system import LIHCLogger
from src.utils.enhanced_config import get_analysis_config


class BatchJobStatus(Enum):
    """Batch job status enumeration"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisType(Enum):
    """Analysis type enumeration"""
    CLOSEDLOOP = "closedloop"
    INTEGRATION = "integration"
    QUALITY_CONTROL = "quality_control"
    COMPARATIVE = "comparative"
    VALIDATION = "validation"


@dataclass
class BatchJob:
    """Batch analysis job definition"""
    job_id: str
    job_name: str
    analysis_type: AnalysisType
    datasets: List[str]
    parameters: Dict[str, Any]
    priority: int = 1
    max_runtime: int = 3600  # seconds
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: BatchJobStatus = BatchJobStatus.PENDING
    progress: float = 0.0
    error_message: Optional[str] = None
    results_path: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class BatchResult:
    """Batch analysis result"""
    job_id: str
    success: bool
    results: Dict[str, Any]
    execution_time: float
    memory_usage: Optional[float] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None


class BatchAnalysisManager:
    """Manages batch analysis workflows"""
    
    def __init__(self, max_workers: int = 4, max_memory: str = "16GB"):
        self.max_workers = max_workers
        self.max_memory = max_memory
        self.logger = LIHCLogger(name="BatchAnalysis")
        self.analysis_config = get_analysis_config()
        
        # Job management
        self.job_queue: List[BatchJob] = []
        self.running_jobs: Dict[str, BatchJob] = {}
        self.completed_jobs: Dict[str, BatchJob] = {}
        self.job_results: Dict[str, BatchResult] = {}
        
        # Executors
        self.process_executor = ProcessPoolExecutor(max_workers=max_workers)
        self.thread_executor = ThreadPoolExecutor(max_workers=max_workers * 2)
        
        # Statistics
        self.total_jobs_processed = 0
        self.total_processing_time = 0.0
        
        self.logger.info(f"Batch analysis manager initialized with {max_workers} workers")
    
    def submit_batch_job(self, 
                        job_name: str,
                        analysis_type: AnalysisType,
                        datasets: List[str],
                        parameters: Dict[str, Any],
                        priority: int = 1) -> str:
        """Submit a new batch job"""
        
        job_id = str(uuid.uuid4())
        job = BatchJob(
            job_id=job_id,
            job_name=job_name,
            analysis_type=analysis_type,
            datasets=datasets,
            parameters=parameters,
            priority=priority
        )
        
        # Add to queue (sort by priority)
        self.job_queue.append(job)
        self.job_queue.sort(key=lambda x: x.priority, reverse=True)
        
        job.status = BatchJobStatus.QUEUED
        
        self.logger.info(f"Batch job submitted: {job_id} ({job_name})")
        return job_id
    
    def submit_comparative_analysis(self,
                                  dataset_groups: List[List[str]],
                                  group_names: List[str],
                                  analysis_parameters: Dict[str, Any]) -> str:
        """Submit comparative analysis across multiple dataset groups"""
        
        job_name = f"Comparative Analysis: {' vs '.join(group_names)}"
        parameters = {
            "dataset_groups": dataset_groups,
            "group_names": group_names,
            "comparison_type": "multi_group",
            **analysis_parameters
        }
        
        # Flatten all datasets
        all_datasets = [dataset for group in dataset_groups for dataset in group]
        
        return self.submit_batch_job(
            job_name=job_name,
            analysis_type=AnalysisType.COMPARATIVE,
            datasets=all_datasets,
            parameters=parameters,
            priority=2
        )
    
    def submit_validation_analysis(self,
                                 primary_datasets: List[str],
                                 validation_datasets: List[str],
                                 validation_type: str = "cross_validation") -> str:
        """Submit validation analysis"""
        
        job_name = f"Validation Analysis ({validation_type})"
        parameters = {
            "primary_datasets": primary_datasets,
            "validation_datasets": validation_datasets,
            "validation_type": validation_type,
            "cross_validation_folds": 5
        }
        
        all_datasets = primary_datasets + validation_datasets
        
        return self.submit_batch_job(
            job_name=job_name,
            analysis_type=AnalysisType.VALIDATION,
            datasets=all_datasets,
            parameters=parameters,
            priority=3
        )
    
    async def process_job_queue(self):
        """Process jobs in the queue"""
        while True:
            # Check for available worker slots
            if len(self.running_jobs) < self.max_workers and self.job_queue:
                # Get next job
                job = self.job_queue.pop(0)
                
                # Start processing
                await self._start_job_processing(job)
            
            # Check for completed jobs
            await self._check_completed_jobs()
            
            # Small delay to prevent busy waiting
            await asyncio.sleep(1)
    
    async def _start_job_processing(self, job: BatchJob):
        """Start processing a job"""
        job.status = BatchJobStatus.RUNNING
        job.started_at = datetime.now()
        self.running_jobs[job.job_id] = job
        
        self.logger.info(f"Starting job: {job.job_id} ({job.job_name})")
        
        # Submit to appropriate executor based on analysis type
        if job.analysis_type in [AnalysisType.CLOSEDLOOP, AnalysisType.COMPARATIVE]:
            # CPU-intensive jobs use process executor
            future = self.process_executor.submit(self._execute_job, job)
        else:
            # I/O-intensive jobs use thread executor
            future = self.thread_executor.submit(self._execute_job, job)
        
        # Store future for tracking
        job.future = future
    
    async def _check_completed_jobs(self):
        """Check for completed jobs and handle results"""
        completed_job_ids = []
        
        for job_id, job in self.running_jobs.items():
            if hasattr(job, 'future') and job.future.done():
                try:
                    result = job.future.result()
                    await self._handle_job_completion(job, result)
                    completed_job_ids.append(job_id)
                except Exception as e:
                    await self._handle_job_error(job, e)
                    completed_job_ids.append(job_id)
        
        # Remove completed jobs from running list
        for job_id in completed_job_ids:
            if job_id in self.running_jobs:
                job = self.running_jobs.pop(job_id)
                self.completed_jobs[job_id] = job
    
    async def _handle_job_completion(self, job: BatchJob, result: BatchResult):
        """Handle successful job completion"""
        job.status = BatchJobStatus.COMPLETED
        job.completed_at = datetime.now()
        job.progress = 1.0
        
        # Store result
        self.job_results[job.job_id] = result
        
        # Update statistics
        execution_time = (job.completed_at - job.started_at).total_seconds()
        self.total_jobs_processed += 1
        self.total_processing_time += execution_time
        
        self.logger.info(f"Job completed: {job.job_id} in {execution_time:.2f}s")
    
    async def _handle_job_error(self, job: BatchJob, error: Exception):
        """Handle job error"""
        job.retry_count += 1
        
        if job.retry_count <= job.max_retries:
            # Retry the job
            job.status = BatchJobStatus.QUEUED
            job.error_message = str(error)
            self.job_queue.insert(0, job)  # High priority for retry
            
            self.logger.warning(f"Job {job.job_id} failed, retrying ({job.retry_count}/{job.max_retries}): {error}")
        else:
            # Mark as failed
            job.status = BatchJobStatus.FAILED
            job.completed_at = datetime.now()
            job.error_message = str(error)
            
            self.logger.error(f"Job {job.job_id} failed permanently: {error}")
    
    def _execute_job(self, job: BatchJob) -> BatchResult:
        """Execute a batch job (runs in separate process/thread)"""
        start_time = datetime.now()
        
        try:
            if job.analysis_type == AnalysisType.CLOSEDLOOP:
                result = self._execute_closedloop_analysis(job)
            elif job.analysis_type == AnalysisType.INTEGRATION:
                result = self._execute_integration_analysis(job)
            elif job.analysis_type == AnalysisType.QUALITY_CONTROL:
                result = self._execute_quality_control(job)
            elif job.analysis_type == AnalysisType.COMPARATIVE:
                result = self._execute_comparative_analysis(job)
            elif job.analysis_type == AnalysisType.VALIDATION:
                result = self._execute_validation_analysis(job)
            else:
                raise ValueError(f"Unknown analysis type: {job.analysis_type}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return BatchResult(
                job_id=job.job_id,
                success=True,
                results=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return BatchResult(
                job_id=job.job_id,
                success=False,
                results={},
                execution_time=execution_time,
                error_details=str(e)
            )
    
    def _execute_closedloop_analysis(self, job: BatchJob) -> Dict[str, Any]:
        """Execute ClosedLoop analysis"""
        # Initialize analyzer
        analyzer = ClosedLoopAnalyzer(config=job.parameters.get('analyzer_config', {}))
        
        # Load and prepare data (simplified - would need proper data loading)
        # This is a placeholder implementation
        rna_data = pd.DataFrame()  # Load actual data
        clinical_data = pd.DataFrame()  # Load actual clinical data
        
        # Run analysis
        result = analyzer.analyze_causal_relationships(
            rna_data=rna_data,
            clinical_data=clinical_data,
            target_genes=job.parameters.get('target_genes')
        )
        
        # Save results
        results_dir = Path("results") / "batch_analyses" / job.job_id
        results_dir.mkdir(parents=True, exist_ok=True)
        
        with open(results_dir / "closedloop_results.json", "w") as f:
            json.dump({
                "causal_genes": [asdict(gene) for gene in result.causal_genes],
                "validation_metrics": result.validation_metrics,
                "algorithm_stats": result.algorithm_stats
            }, f, indent=2, default=str)
        
        return {
            "analysis_type": "closedloop",
            "causal_genes_count": len(result.causal_genes),
            "top_genes": [gene.gene_id for gene in result.causal_genes[:10]],
            "validation_score": result.validation_metrics.get("cross_validation_score", 0),
            "results_path": str(results_dir)
        }
    
    def _execute_integration_analysis(self, job: BatchJob) -> Dict[str, Any]:
        """Execute multi-omics integration analysis"""
        loader = MultiOmicsDataLoader()
        
        # Load datasets
        for dataset_path in job.datasets:
            # Determine data type and load accordingly
            if "rna" in dataset_path.lower():
                loader.load_rna_seq_data(dataset_path)
            elif "cnv" in dataset_path.lower():
                loader.load_cnv_data(dataset_path)
            # Add more data type handling...
        
        # Integrate datasets
        integration_result = loader.integrate_datasets(
            required_overlap=job.parameters.get('required_overlap', 0.8)
        )
        
        # Save results
        results_dir = Path("results") / "batch_analyses" / job.job_id
        results_dir.mkdir(parents=True, exist_ok=True)
        
        loader.save_integration_result(integration_result, str(results_dir))
        
        return {
            "analysis_type": "integration",
            "integrated_samples": integration_result.integration_stats['total_samples'],
            "data_types": integration_result.integration_stats['data_types'],
            "quality_metrics": {
                dt: metrics.quality_score 
                for dt, metrics in integration_result.quality_metrics.items()
            },
            "results_path": str(results_dir)
        }
    
    def _execute_quality_control(self, job: BatchJob) -> Dict[str, Any]:
        """Execute quality control analysis"""
        qc = DataQualityController(config=job.parameters.get('qc_config', {}))
        results = {}
        
        for dataset_path in job.datasets:
            # Load dataset
            data = pd.read_csv(dataset_path, index_col=0)
            
            # Perform quality assessment
            quality_report = qc.assess_data_quality(
                data, 
                dataset_name=Path(dataset_path).stem,
                generate_plots=job.parameters.get('generate_plots', True),
                output_dir=f"results/batch_analyses/{job.job_id}/qc_plots"
            )
            
            results[Path(dataset_path).stem] = {
                "quality_score": quality_report.overall_quality_score,
                "missing_rate": quality_report.missing_rate,
                "outliers": len(quality_report.outlier_samples),
                "issues": [issue.value for issue in quality_report.issues],
                "recommendations": quality_report.recommendations
            }
        
        return {
            "analysis_type": "quality_control",
            "datasets_analyzed": len(job.datasets),
            "overall_quality": np.mean([r["quality_score"] for r in results.values()]),
            "quality_results": results
        }
    
    def _execute_comparative_analysis(self, job: BatchJob) -> Dict[str, Any]:
        """Execute comparative analysis between groups"""
        # This would implement sophisticated comparative analysis
        # For now, return placeholder results
        
        dataset_groups = job.parameters["dataset_groups"]
        group_names = job.parameters["group_names"]
        
        # Placeholder comparative analysis logic
        results = {
            "analysis_type": "comparative",
            "groups_compared": len(dataset_groups),
            "group_names": group_names,
            "differential_genes": [],  # Would contain actual differential analysis
            "pathway_differences": {},  # Would contain pathway analysis
            "statistical_summary": {}  # Would contain statistical comparisons
        }
        
        return results
    
    def _execute_validation_analysis(self, job: BatchJob) -> Dict[str, Any]:
        """Execute validation analysis"""
        # This would implement cross-validation and external validation
        # For now, return placeholder results
        
        validation_type = job.parameters["validation_type"]
        
        results = {
            "analysis_type": "validation",
            "validation_type": validation_type,
            "primary_datasets": len(job.parameters["primary_datasets"]),
            "validation_datasets": len(job.parameters["validation_datasets"]),
            "validation_score": 0.85,  # Placeholder
            "consistency_metrics": {},  # Would contain actual consistency analysis
            "reproducibility_score": 0.82  # Placeholder
        }
        
        return results
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        # Check all job collections
        job = None
        if job_id in self.running_jobs:
            job = self.running_jobs[job_id]
        elif job_id in self.completed_jobs:
            job = self.completed_jobs[job_id]
        else:
            # Check queue
            for queued_job in self.job_queue:
                if queued_job.job_id == job_id:
                    job = queued_job
                    break
        
        if not job:
            return None
        
        status_info = {
            "job_id": job.job_id,
            "job_name": job.job_name,
            "analysis_type": job.analysis_type.value,
            "status": job.status.value,
            "progress": job.progress,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message
        }
        
        # Add result if available
        if job_id in self.job_results:
            result = self.job_results[job_id]
            status_info["results"] = result.results
            status_info["execution_time"] = result.execution_time
        
        return status_info
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        return {
            "queued_jobs": len(self.job_queue),
            "running_jobs": len(self.running_jobs),
            "completed_jobs": len(self.completed_jobs),
            "total_processed": self.total_jobs_processed,
            "average_processing_time": (
                self.total_processing_time / self.total_jobs_processed 
                if self.total_jobs_processed > 0 else 0
            ),
            "worker_utilization": len(self.running_jobs) / self.max_workers
        }
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        # Check if job is in queue
        for i, job in enumerate(self.job_queue):
            if job.job_id == job_id:
                job.status = BatchJobStatus.CANCELLED
                self.job_queue.pop(i)
                self.completed_jobs[job_id] = job
                return True
        
        # Check if job is running
        if job_id in self.running_jobs:
            job = self.running_jobs[job_id]
            if hasattr(job, 'future'):
                job.future.cancel()
            job.status = BatchJobStatus.CANCELLED
            job.completed_at = datetime.now()
            self.completed_jobs[job_id] = self.running_jobs.pop(job_id)
            return True
        
        return False
    
    def cleanup_old_jobs(self, days: int = 30):
        """Clean up old completed jobs"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        jobs_to_remove = []
        for job_id, job in self.completed_jobs.items():
            if job.completed_at and job.completed_at < cutoff_date:
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.completed_jobs[job_id]
            if job_id in self.job_results:
                del self.job_results[job_id]
        
        self.logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")
    
    def __del__(self):
        """Cleanup executors"""
        if hasattr(self, 'process_executor'):
            self.process_executor.shutdown(wait=True)
        if hasattr(self, 'thread_executor'):
            self.thread_executor.shutdown(wait=True)