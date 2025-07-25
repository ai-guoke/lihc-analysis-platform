"""
Task Queue Management System using Celery
任务队列管理系统 - 使用Celery实现后台任务处理
"""

from celery import Celery, Task
from celery.result import AsyncResult
from kombu import Exchange, Queue
import redis
from pathlib import Path
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)

# Create Celery app
app = Celery(
    'lihc_analysis',
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=['src.analysis.task_queue']
)

# Configure Celery
app.conf.update(
    # Task configuration
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Result backend configuration
    result_expires=3600 * 24,  # Results expire after 24 hours
    result_persistent=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    
    # Task routing
    task_routes={
        'analysis.quick': {'queue': 'quick'},
        'analysis.standard': {'queue': 'standard'},
        'analysis.heavy': {'queue': 'heavy'},
        'analysis.batch': {'queue': 'batch'}
    },
    
    # Queue configuration
    task_queues=(
        Queue('quick', Exchange('quick'), routing_key='quick'),
        Queue('standard', Exchange('standard'), routing_key='standard'),
        Queue('heavy', Exchange('heavy'), routing_key='heavy'),
        Queue('batch', Exchange('batch'), routing_key='batch'),
    ),
    
    # Task time limits
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3000,  # 50 minutes soft limit
    
    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)


class AnalysisTask(Task):
    """Base task class with progress tracking"""
    
    def __init__(self):
        self.progress_data = {}
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """Update task progress"""
        progress = min(100, int((current / total) * 100))
        self.update_state(
            state='PROGRESS',
            meta={
                'current': current,
                'total': total,
                'progress': progress,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            }
        )


@app.task(base=AnalysisTask, bind=True, name='analysis.quick')
def quick_analysis_task(self, dataset_id: str, analysis_type: str, params: dict = None):
    """Quick analysis tasks (< 5 minutes)"""
    logger.info(f"Starting quick analysis: {analysis_type} for dataset {dataset_id}")
    
    try:
        self.update_progress(0, 100, f"Starting {analysis_type} analysis")
        
        # Import analysis modules
        from src.analysis.simplified_analyzer import SimplifiedAnalyzer
        from src.analysis.progress_manager import ProgressManager
        
        # Create session
        session_id = f"celery_{self.request.id}"
        progress_manager = ProgressManager(session_id)
        analyzer = SimplifiedAnalyzer(session_id)
        
        # Update progress
        self.update_progress(20, 100, "Loading data")
        
        # Perform analysis based on type
        if analysis_type == 'differential_expression':
            result = analyzer._perform_differential_expression(progress_manager)
        elif analysis_type == 'survival':
            result = analyzer._perform_survival_analysis(progress_manager)
        elif analysis_type == 'network':
            result = analyzer._perform_network_analysis(progress_manager)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        self.update_progress(90, 100, "Finalizing results")
        
        # Return results
        return {
            'status': 'success',
            'dataset_id': dataset_id,
            'analysis_type': analysis_type,
            'session_id': session_id,
            'results': result,
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in quick analysis: {str(e)}")
        return {
            'status': 'error',
            'dataset_id': dataset_id,
            'analysis_type': analysis_type,
            'error': str(e),
            'failed_at': datetime.utcnow().isoformat()
        }


@app.task(base=AnalysisTask, bind=True, name='analysis.standard')
def standard_analysis_task(self, dataset_id: str, modules: List[str], params: dict = None):
    """Standard analysis tasks (5-30 minutes)"""
    logger.info(f"Starting standard analysis for dataset {dataset_id} with modules: {modules}")
    
    try:
        self.update_progress(0, len(modules), "Starting analysis")
        
        from src.analysis.simplified_analyzer import SimplifiedAnalyzer
        from src.analysis.progress_manager import ProgressManager
        
        session_id = f"celery_{self.request.id}"
        progress_manager = ProgressManager(session_id)
        analyzer = SimplifiedAnalyzer(session_id)
        
        # Run all analyses
        results = {}
        for idx, module in enumerate(modules):
            self.update_progress(idx, len(modules), f"Running {module}")
            
            if module == 'stage1':
                results['stage1'] = analyzer._perform_stage1_analysis(progress_manager)
            elif module == 'stage2':
                results['stage2'] = analyzer._perform_stage2_analysis(progress_manager)
            elif module == 'stage3':
                results['stage3'] = analyzer._perform_stage3_analysis(progress_manager)
            elif module == 'precision':
                results['precision'] = analyzer._perform_precision_medicine_analysis(progress_manager)
            
        self.update_progress(len(modules), len(modules), "Analysis complete")
        
        return {
            'status': 'success',
            'dataset_id': dataset_id,
            'modules': modules,
            'session_id': session_id,
            'results': results,
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in standard analysis: {str(e)}")
        return {
            'status': 'error',
            'dataset_id': dataset_id,
            'error': str(e),
            'failed_at': datetime.utcnow().isoformat()
        }


@app.task(base=AnalysisTask, bind=True, name='analysis.heavy')
def heavy_analysis_task(self, dataset_id: str, analysis_config: dict):
    """Heavy computational tasks (> 30 minutes)"""
    logger.info(f"Starting heavy analysis for dataset {dataset_id}")
    
    try:
        self.update_progress(0, 100, "Initializing heavy computation")
        
        from src.analysis.advanced_analyzer import AdvancedAnalyzer
        
        session_id = f"celery_{self.request.id}"
        analyzer = AdvancedAnalyzer(session_id)
        
        # Load data
        self.update_progress(10, 100, "Loading large dataset")
        # Simulate loading large data
        
        # Run comprehensive analysis
        self.update_progress(30, 100, "Running comprehensive analysis")
        results = analyzer.run_comprehensive_analysis(
            modules=analysis_config.get('modules', ['all']),
            params=analysis_config.get('params', {})
        )
        
        self.update_progress(90, 100, "Generating reports")
        
        return {
            'status': 'success',
            'dataset_id': dataset_id,
            'session_id': session_id,
            'results': results,
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in heavy analysis: {str(e)}")
        return {
            'status': 'error',
            'dataset_id': dataset_id,
            'error': str(e),
            'failed_at': datetime.utcnow().isoformat()
        }


@app.task(bind=True, name='analysis.batch')
def batch_analysis_task(self, batch_job_id: str, dataset_ids: List[str], modules: List[str]):
    """Batch processing of multiple datasets"""
    logger.info(f"Starting batch analysis job {batch_job_id}")
    
    try:
        from src.analysis.batch_processor import batch_processor
        
        # Use batch processor with Celery tracking
        total_datasets = len(dataset_ids)
        completed = 0
        
        # Create subtasks for each dataset
        subtasks = []
        for dataset_id in dataset_ids:
            subtask = standard_analysis_task.s(dataset_id, modules)
            subtasks.append(subtask)
        
        # Create group and execute
        from celery import group
        job = group(subtasks)
        result = job.apply_async()
        
        # Wait for completion and track progress
        while not result.ready():
            completed_count = sum(1 for r in result.results if r.ready())
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': completed_count,
                    'total': total_datasets,
                    'progress': int((completed_count / total_datasets) * 100),
                    'message': f"Processing {completed_count}/{total_datasets} datasets"
                }
            )
            # Sleep to avoid busy waiting
            import time
            time.sleep(5)
        
        # Collect results
        batch_results = {
            'job_id': batch_job_id,
            'status': 'completed',
            'datasets_processed': total_datasets,
            'results': [r.get() for r in result.results],
            'completed_at': datetime.utcnow().isoformat()
        }
        
        return batch_results
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        return {
            'status': 'error',
            'job_id': batch_job_id,
            'error': str(e),
            'failed_at': datetime.utcnow().isoformat()
        }


class TaskQueueManager:
    """Manages task submission and monitoring"""
    
    def __init__(self):
        self.redis_client = redis.from_url(REDIS_URL)
    
    def submit_analysis(self, dataset_id: str, analysis_type: str, 
                       priority: str = 'standard', **kwargs) -> str:
        """Submit an analysis task to the queue"""
        # Determine which task and queue to use
        if analysis_type in ['differential_expression', 'survival', 'network']:
            task = quick_analysis_task
            queue = 'quick'
        elif analysis_type in ['stage1', 'stage2', 'stage3', 'precision']:
            task = standard_analysis_task
            queue = 'standard'
            kwargs['modules'] = [analysis_type]
        elif analysis_type == 'comprehensive':
            task = heavy_analysis_task
            queue = 'heavy'
        elif analysis_type == 'batch':
            task = batch_analysis_task
            queue = 'batch'
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        # Submit task
        result = task.apply_async(
            args=[dataset_id],
            kwargs=kwargs,
            queue=queue,
            priority=self._get_priority_value(priority)
        )
        
        # Store task metadata
        self._store_task_metadata(result.id, dataset_id, analysis_type)
        
        return result.id
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get current status of a task"""
        result = AsyncResult(task_id, app=app)
        
        status_info = {
            'task_id': task_id,
            'state': result.state,
            'ready': result.ready(),
            'successful': result.successful() if result.ready() else None,
            'failed': result.failed() if result.ready() else None
        }
        
        # Add progress info if available
        if result.state == 'PROGRESS':
            status_info.update(result.info)
        elif result.ready():
            status_info['result'] = result.result
        
        # Add metadata
        metadata = self._get_task_metadata(task_id)
        if metadata:
            status_info.update(metadata)
        
        return status_info
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        result = AsyncResult(task_id, app=app)
        result.revoke(terminate=True)
        
        # Update metadata
        self._update_task_metadata(task_id, {'cancelled': True, 
                                            'cancelled_at': datetime.utcnow().isoformat()})
        
        return True
    
    def list_tasks(self, status: Optional[str] = None, 
                  dataset_id: Optional[str] = None) -> List[Dict]:
        """List tasks with optional filtering"""
        # Get all task keys from Redis
        task_keys = self.redis_client.keys('celery-task-meta-*')
        
        tasks = []
        for key in task_keys:
            task_id = key.decode().replace('celery-task-meta-', '')
            task_info = self.get_task_status(task_id)
            
            # Apply filters
            if status and task_info['state'] != status:
                continue
            if dataset_id and task_info.get('dataset_id') != dataset_id:
                continue
            
            tasks.append(task_info)
        
        # Sort by submission time
        tasks.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
        
        return tasks
    
    def get_queue_stats(self) -> Dict:
        """Get statistics about task queues"""
        from celery import current_app
        inspect = current_app.control.inspect()
        
        # Get active tasks
        active = inspect.active()
        scheduled = inspect.scheduled()
        reserved = inspect.reserved()
        
        # Count tasks by queue
        stats = {
            'queues': {
                'quick': {'active': 0, 'waiting': 0},
                'standard': {'active': 0, 'waiting': 0},
                'heavy': {'active': 0, 'waiting': 0},
                'batch': {'active': 0, 'waiting': 0}
            },
            'total_active': 0,
            'total_waiting': 0
        }
        
        # Count active tasks
        if active:
            for worker, tasks in active.items():
                stats['total_active'] += len(tasks)
                for task in tasks:
                    queue = task.get('delivery_info', {}).get('routing_key', 'standard')
                    if queue in stats['queues']:
                        stats['queues'][queue]['active'] += 1
        
        # Count waiting tasks
        if reserved:
            for worker, tasks in reserved.items():
                stats['total_waiting'] += len(tasks)
                for task in tasks:
                    queue = task.get('delivery_info', {}).get('routing_key', 'standard')
                    if queue in stats['queues']:
                        stats['queues'][queue]['waiting'] += 1
        
        return stats
    
    def _get_priority_value(self, priority: str) -> int:
        """Convert priority string to numeric value"""
        priority_map = {
            'low': 1,
            'standard': 5,
            'high': 9
        }
        return priority_map.get(priority, 5)
    
    def _store_task_metadata(self, task_id: str, dataset_id: str, analysis_type: str):
        """Store task metadata in Redis"""
        metadata = {
            'dataset_id': dataset_id,
            'analysis_type': analysis_type,
            'submitted_at': datetime.utcnow().isoformat()
        }
        
        self.redis_client.hset(
            f'task-metadata:{task_id}',
            mapping={k: json.dumps(v) if isinstance(v, (dict, list)) else v 
                    for k, v in metadata.items()}
        )
        
        # Expire after 7 days
        self.redis_client.expire(f'task-metadata:{task_id}', 86400 * 7)
    
    def _get_task_metadata(self, task_id: str) -> Optional[Dict]:
        """Get task metadata from Redis"""
        data = self.redis_client.hgetall(f'task-metadata:{task_id}')
        if not data:
            return None
        
        # Decode and parse
        metadata = {}
        for key, value in data.items():
            key = key.decode()
            value = value.decode()
            try:
                metadata[key] = json.loads(value)
            except:
                metadata[key] = value
        
        return metadata
    
    def _update_task_metadata(self, task_id: str, updates: Dict):
        """Update task metadata"""
        for key, value in updates.items():
            self.redis_client.hset(
                f'task-metadata:{task_id}',
                key,
                json.dumps(value) if isinstance(value, (dict, list)) else value
            )


# Create global task queue manager instance
task_queue_manager = TaskQueueManager()


# Worker health check task
@app.task(name='health.check')
def health_check():
    """Simple health check task"""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'worker': os.getpid()
    }


# Periodic task for cleanup
@app.task(name='maintenance.cleanup')
def cleanup_old_tasks():
    """Clean up old task results and metadata"""
    logger.info("Running maintenance cleanup")
    
    # Implementation would clean up old tasks
    # For now, just return status
    return {
        'status': 'cleanup_complete',
        'timestamp': datetime.utcnow().isoformat()
    }


if __name__ == '__main__':
    # Example usage
    manager = TaskQueueManager()
    
    # Submit a task
    task_id = manager.submit_analysis(
        dataset_id='demo',
        analysis_type='differential_expression'
    )
    print(f"Submitted task: {task_id}")
    
    # Check status
    status = manager.get_task_status(task_id)
    print(f"Task status: {status}")
    
    # Get queue stats
    stats = manager.get_queue_stats()
    print(f"Queue stats: {stats}")