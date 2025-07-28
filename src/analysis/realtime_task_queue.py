"""
Real-time Analysis Task Queue System for LIHC Platform
实时分析任务队列管理系统
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import pickle
import warnings
warnings.filterwarnings('ignore')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class AnalysisTask:
    """分析任务数据类"""
    task_id: str
    task_type: str
    task_name: str
    user_id: str
    priority: TaskPriority
    status: TaskStatus
    parameters: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    error_message: Optional[str] = None
    result_path: Optional[str] = None
    estimated_duration: Optional[int] = None  # seconds
    dependencies: List[str] = None  # dependent task IDs
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class TaskQueue:
    """任务队列管理器"""
    
    def __init__(self, max_workers: int = 4, persistence_path: str = "data/task_queue"):
        self.max_workers = max_workers
        self.persistence_path = Path(persistence_path)
        self.persistence_path.mkdir(parents=True, exist_ok=True)
        
        # 任务存储
        self.tasks: Dict[str, AnalysisTask] = {}
        self.task_queue = queue.PriorityQueue()
        self.running_tasks: Dict[str, threading.Thread] = {}
        
        # 线程池
        self.thread_executor = ThreadPoolExecutor(max_workers=max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=max(1, max_workers//2))
        
        # 控制变量
        self.is_running = False
        self.queue_thread = None
        
        # 任务处理器注册表
        self.task_processors: Dict[str, Callable] = {}
        
        # 统计信息
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'average_execution_time': 0.0
        }
        
        # 加载持久化任务
        self._load_persisted_tasks()
        
        # 注册默认任务处理器
        self._register_default_processors()
    
    def _register_default_processors(self):
        """注册默认任务处理器"""
        
        self.register_processor('differential_expression', self._process_differential_expression)
        self.register_processor('survival_analysis', self._process_survival_analysis)
        self.register_processor('pathway_enrichment', self._process_pathway_enrichment)
        self.register_processor('drug_sensitivity', self._process_drug_sensitivity)
        self.register_processor('biomarker_discovery', self._process_biomarker_discovery)
        self.register_processor('single_cell_analysis', self._process_single_cell_analysis)
        self.register_processor('multi_omics_integration', self._process_multi_omics_integration)
        self.register_processor('drug_combination_prediction', self._process_drug_combination_prediction)
    
    def register_processor(self, task_type: str, processor: Callable):
        """注册任务处理器"""
        self.task_processors[task_type] = processor
        logger.info(f"Registered processor for task type: {task_type}")
    
    def submit_task(self, task_type: str, task_name: str, user_id: str,
                   parameters: Dict[str, Any], priority: TaskPriority = TaskPriority.NORMAL,
                   dependencies: List[str] = None) -> str:
        """提交新任务"""
        
        task_id = str(uuid.uuid4())
        
        # 估算任务执行时间
        estimated_duration = self._estimate_task_duration(task_type, parameters)
        
        task = AnalysisTask(
            task_id=task_id,
            task_type=task_type,
            task_name=task_name,
            user_id=user_id,
            priority=priority,
            status=TaskStatus.PENDING,
            parameters=parameters,
            created_at=datetime.now(),
            estimated_duration=estimated_duration,
            dependencies=dependencies or []
        )
        
        self.tasks[task_id] = task
        self.stats['total_tasks'] += 1
        
        # 检查依赖关系
        if self._check_dependencies(task):
            self._enqueue_task(task)
        
        # 持久化任务
        self._persist_task(task)
        
        logger.info(f"Task submitted: {task_id} ({task_type})")
        return task_id
    
    def _check_dependencies(self, task: AnalysisTask) -> bool:
        """检查任务依赖关系"""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            if self.tasks[dep_id].status not in [TaskStatus.COMPLETED]:
                return False
        return True
    
    def _enqueue_task(self, task: AnalysisTask):
        """将任务加入队列"""
        # 使用负优先级值来实现高优先级先执行
        priority_value = -task.priority.value
        self.task_queue.put((priority_value, task.created_at, task.task_id))
    
    def start_queue_processing(self):
        """启动队列处理"""
        if self.is_running:
            return
        
        self.is_running = True
        self.queue_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.queue_thread.start()
        logger.info("Task queue processing started")
    
    def stop_queue_processing(self):
        """停止队列处理"""
        self.is_running = False
        if self.queue_thread:
            self.queue_thread.join()
        logger.info("Task queue processing stopped")
    
    def _process_queue(self):
        """队列处理主循环"""
        while self.is_running:
            try:
                # 检查是否有可用的工作线程
                if len(self.running_tasks) >= self.max_workers:
                    time.sleep(1)
                    continue
                
                # 从队列获取任务
                try:
                    priority, created_at, task_id = self.task_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                if task_id not in self.tasks:
                    continue
                
                task = self.tasks[task_id]
                
                # 再次检查依赖关系
                if not self._check_dependencies(task):
                    # 重新入队等待
                    self.task_queue.put((priority, created_at, task_id))
                    time.sleep(1)
                    continue
                
                # 启动任务执行
                self._execute_task(task)
                
            except Exception as e:
                logger.error(f"Error in queue processing: {e}")
                time.sleep(1)
    
    def _execute_task(self, task: AnalysisTask):
        """执行任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        self._persist_task(task)
        
        # 创建任务执行线程
        execution_thread = threading.Thread(
            target=self._run_task_processor,
            args=(task,),
            daemon=True
        )
        
        self.running_tasks[task.task_id] = execution_thread
        execution_thread.start()
        
        logger.info(f"Started executing task: {task.task_id}")
    
    def _run_task_processor(self, task: AnalysisTask):
        """运行任务处理器"""
        try:
            processor = self.task_processors.get(task.task_type)
            if not processor:
                raise ValueError(f"No processor found for task type: {task.task_type}")
            
            # 执行任务
            result = processor(task)
            
            # 更新任务状态
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.progress = 100.0
            task.result_path = result.get('result_path') if isinstance(result, dict) else None
            
            self.stats['completed_tasks'] += 1
            self._update_average_execution_time(task)
            
            logger.info(f"Task completed: {task.task_id}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            self.stats['failed_tasks'] += 1
            
            logger.error(f"Task failed: {task.task_id}, Error: {e}")
        
        finally:
            # 清理运行中的任务记录
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
            
            # 持久化任务状态
            self._persist_task(task)
            
            # 检查是否有依赖此任务的其他任务
            self._check_and_enqueue_dependent_tasks(task.task_id)
    
    def _check_and_enqueue_dependent_tasks(self, completed_task_id: str):
        """检查并入队依赖任务"""
        for task in self.tasks.values():
            if (task.status == TaskStatus.PENDING and 
                completed_task_id in task.dependencies and
                self._check_dependencies(task)):
                self._enqueue_task(task)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        if task.status == TaskStatus.RUNNING:
            # 对于正在运行的任务，设置取消标志
            task.status = TaskStatus.CANCELLED
            # 注意：实际中断正在运行的任务需要在处理器中实现
        elif task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
        else:
            return False
        
        task.completed_at = datetime.now()
        self._persist_task(task)
        
        logger.info(f"Task cancelled: {task_id}")
        return True
    
    def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.PAUSED
            self._persist_task(task)
            return True
        
        return False
    
    def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status == TaskStatus.PAUSED:
            task.status = TaskStatus.RUNNING
            self._persist_task(task)
            return True
        
        return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            'task_id': task.task_id,
            'task_type': task.task_type,
            'task_name': task.task_name,
            'status': task.status.value,
            'progress': task.progress,
            'created_at': task.created_at.isoformat(),
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'error_message': task.error_message,
            'estimated_duration': task.estimated_duration,
            'elapsed_time': self._calculate_elapsed_time(task)
        }
    
    def get_user_tasks(self, user_id: str, status_filter: Optional[TaskStatus] = None) -> List[Dict]:
        """获取用户任务列表"""
        user_tasks = []
        
        for task in self.tasks.values():
            if task.user_id == user_id:
                if status_filter is None or task.status == status_filter:
                    user_tasks.append(self.get_task_status(task.task_id))
        
        # 按创建时间排序
        user_tasks.sort(key=lambda x: x['created_at'], reverse=True)
        return user_tasks
    
    def get_queue_statistics(self) -> Dict:
        """获取队列统计信息"""
        pending_count = sum(1 for task in self.tasks.values() if task.status == TaskStatus.PENDING)
        running_count = sum(1 for task in self.tasks.values() if task.status == TaskStatus.RUNNING)
        
        return {
            'total_tasks': self.stats['total_tasks'],
            'completed_tasks': self.stats['completed_tasks'],
            'failed_tasks': self.stats['failed_tasks'],
            'pending_tasks': pending_count,
            'running_tasks': running_count,
            'average_execution_time': self.stats['average_execution_time'],
            'queue_size': self.task_queue.qsize(),
            'active_workers': len(self.running_tasks),
            'max_workers': self.max_workers
        }
    
    def _estimate_task_duration(self, task_type: str, parameters: Dict) -> int:
        """估算任务执行时间（秒）"""
        # 基于任务类型的预估时间
        base_durations = {
            'differential_expression': 120,  # 2分钟
            'survival_analysis': 180,        # 3分钟
            'pathway_enrichment': 300,       # 5分钟
            'drug_sensitivity': 240,         # 4分钟
            'biomarker_discovery': 600,      # 10分钟
            'single_cell_analysis': 900,     # 15分钟
            'multi_omics_integration': 1200, # 20分钟
            'drug_combination_prediction': 480  # 8分钟
        }
        
        base_duration = base_durations.get(task_type, 300)
        
        # 根据数据大小调整
        data_size_factor = parameters.get('data_size_factor', 1.0)
        estimated_duration = int(base_duration * data_size_factor)
        
        return estimated_duration
    
    def _calculate_elapsed_time(self, task: AnalysisTask) -> Optional[int]:
        """计算任务执行时间（秒）"""
        if task.started_at is None:
            return None
        
        end_time = task.completed_at if task.completed_at else datetime.now()
        elapsed = end_time - task.started_at
        return int(elapsed.total_seconds())
    
    def _update_average_execution_time(self, task: AnalysisTask):
        """更新平均执行时间"""
        if task.started_at and task.completed_at:
            execution_time = (task.completed_at - task.started_at).total_seconds()
            
            current_avg = self.stats['average_execution_time']
            completed_count = self.stats['completed_tasks']
            
            # 计算新的平均值
            new_avg = ((current_avg * (completed_count - 1)) + execution_time) / completed_count
            self.stats['average_execution_time'] = new_avg
    
    def _persist_task(self, task: AnalysisTask):
        """持久化任务状态"""
        try:
            task_file = self.persistence_path / f"task_{task.task_id}.json"
            with open(task_file, 'w') as f:
                # 转换为可序列化的字典
                task_dict = asdict(task)
                # 处理datetime和enum类型
                task_dict['created_at'] = task.created_at.isoformat()
                task_dict['started_at'] = task.started_at.isoformat() if task.started_at else None
                task_dict['completed_at'] = task.completed_at.isoformat() if task.completed_at else None
                task_dict['priority'] = task.priority.value
                task_dict['status'] = task.status.value
                
                json.dump(task_dict, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist task {task.task_id}: {e}")
    
    def _load_persisted_tasks(self):
        """加载持久化的任务"""
        try:
            for task_file in self.persistence_path.glob("task_*.json"):
                try:
                    with open(task_file, 'r') as f:
                        task_dict = json.load(f)
                    
                    # 重构任务对象
                    task = AnalysisTask(
                        task_id=task_dict['task_id'],
                        task_type=task_dict['task_type'],
                        task_name=task_dict['task_name'],
                        user_id=task_dict['user_id'],
                        priority=TaskPriority(task_dict['priority']),
                        status=TaskStatus(task_dict['status']),
                        parameters=task_dict['parameters'],
                        created_at=datetime.fromisoformat(task_dict['created_at']),
                        started_at=datetime.fromisoformat(task_dict['started_at']) if task_dict['started_at'] else None,
                        completed_at=datetime.fromisoformat(task_dict['completed_at']) if task_dict['completed_at'] else None,
                        progress=task_dict.get('progress', 0.0),
                        error_message=task_dict.get('error_message'),
                        result_path=task_dict.get('result_path'),
                        estimated_duration=task_dict.get('estimated_duration'),
                        dependencies=task_dict.get('dependencies', [])
                    )
                    
                    self.tasks[task.task_id] = task
                    
                    # 重新入队未完成的任务
                    if task.status == TaskStatus.PENDING:
                        if self._check_dependencies(task):
                            self._enqueue_task(task)
                    
                except Exception as e:
                    logger.error(f"Failed to load task from {task_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load persisted tasks: {e}")
    
    # 默认任务处理器实现
    def _process_differential_expression(self, task: AnalysisTask) -> Dict:
        """差异表达分析处理器"""
        import time
        import numpy as np
        
        params = task.parameters
        
        # 模拟分析过程
        for i in range(10):
            if task.status == TaskStatus.CANCELLED:
                break
            time.sleep(params.get('step_duration', 2))
            task.progress = (i + 1) * 10
            self._persist_task(task)
        
        # 生成结果
        result = {
            'differentially_expressed_genes': np.random.randint(500, 2000),
            'upregulated_genes': np.random.randint(200, 800),
            'downregulated_genes': np.random.randint(200, 800),
            'result_path': f"results/de_analysis_{task.task_id}.csv"
        }
        
        return result
    
    def _process_survival_analysis(self, task: AnalysisTask) -> Dict:
        """生存分析处理器"""
        import time
        
        params = task.parameters
        
        # 模拟分析过程
        for i in range(8):
            if task.status == TaskStatus.CANCELLED:
                break
            time.sleep(params.get('step_duration', 3))
            task.progress = (i + 1) * 12.5
            self._persist_task(task)
        
        result = {
            'significant_genes': np.random.randint(50, 200),
            'median_survival_difference': np.random.uniform(5, 20),
            'p_value': np.random.uniform(0.001, 0.05),
            'result_path': f"results/survival_analysis_{task.task_id}.html"
        }
        
        return result
    
    def _process_pathway_enrichment(self, task: AnalysisTask) -> Dict:
        """通路富集分析处理器"""
        import time
        
        params = task.parameters
        
        for i in range(12):
            if task.status == TaskStatus.CANCELLED:
                break
            time.sleep(params.get('step_duration', 2.5))
            task.progress = (i + 1) * 8.33
            self._persist_task(task)
        
        result = {
            'enriched_pathways': np.random.randint(20, 100),
            'significant_pathways': np.random.randint(5, 30),
            'top_pathway': 'Cancer-related pathway',
            'result_path': f"results/pathway_enrichment_{task.task_id}.json"
        }
        
        return result
    
    def _process_drug_sensitivity(self, task: AnalysisTask) -> Dict:
        """药物敏感性分析处理器"""
        import time
        
        params = task.parameters
        
        for i in range(10):
            if task.status == TaskStatus.CANCELLED:
                break
            time.sleep(params.get('step_duration', 2))
            task.progress = (i + 1) * 10
            self._persist_task(task)
        
        result = {
            'predicted_sensitive_drugs': np.random.randint(5, 20),
            'predicted_resistant_drugs': np.random.randint(3, 15),
            'top_drug_recommendation': 'Sorafenib',
            'result_path': f"results/drug_sensitivity_{task.task_id}.json"
        }
        
        return result
    
    def _process_biomarker_discovery(self, task: AnalysisTask) -> Dict:
        """生物标志物发现处理器"""
        import time
        
        params = task.parameters
        
        for i in range(20):
            if task.status == TaskStatus.CANCELLED:
                break
            time.sleep(params.get('step_duration', 3))
            task.progress = (i + 1) * 5
            self._persist_task(task)
        
        result = {
            'candidate_biomarkers': np.random.randint(10, 50),
            'validated_biomarkers': np.random.randint(3, 15),
            'top_biomarker': 'AFP',
            'auc_score': np.random.uniform(0.7, 0.95),
            'result_path': f"results/biomarker_discovery_{task.task_id}.json"
        }
        
        return result
    
    def _process_single_cell_analysis(self, task: AnalysisTask) -> Dict:
        """单细胞分析处理器"""
        import time
        
        params = task.parameters
        
        for i in range(30):
            if task.status == TaskStatus.CANCELLED:
                break
            time.sleep(params.get('step_duration', 3))
            task.progress = (i + 1) * 3.33
            self._persist_task(task)
        
        result = {
            'identified_cell_types': np.random.randint(8, 20),
            'total_cells_analyzed': np.random.randint(1000, 10000),
            'differential_genes': np.random.randint(100, 500),
            'result_path': f"results/single_cell_analysis_{task.task_id}.h5ad"
        }
        
        return result
    
    def _process_multi_omics_integration(self, task: AnalysisTask) -> Dict:
        """多组学整合分析处理器"""
        import time
        
        params = task.parameters
        
        for i in range(25):
            if task.status == TaskStatus.CANCELLED:
                break
            time.sleep(params.get('step_duration', 4))
            task.progress = (i + 1) * 4
            self._persist_task(task)
        
        result = {
            'integrated_features': np.random.randint(100, 1000),
            'omics_types_integrated': np.random.randint(3, 6),
            'consensus_clusters': np.random.randint(3, 8),
            'result_path': f"results/multi_omics_integration_{task.task_id}.json"
        }
        
        return result
    
    def _process_drug_combination_prediction(self, task: AnalysisTask) -> Dict:
        """药物组合预测处理器"""
        import time
        
        params = task.parameters
        
        for i in range(16):
            if task.status == TaskStatus.CANCELLED:
                break
            time.sleep(params.get('step_duration', 3))
            task.progress = (i + 1) * 6.25
            self._persist_task(task)
        
        result = {
            'evaluated_combinations': np.random.randint(20, 100),
            'synergistic_combinations': np.random.randint(3, 15),
            'top_combination': 'Sorafenib + Atezolizumab',
            'predicted_response_rate': np.random.uniform(0.3, 0.7),
            'result_path': f"results/drug_combination_prediction_{task.task_id}.json"
        }
        
        return result


# 队列管理接口
class TaskQueueManager:
    """任务队列管理器接口"""
    
    def __init__(self):
        self.queue = TaskQueue()
        self.queue.start_queue_processing()
    
    def submit_analysis_task(self, task_type: str, user_id: str, parameters: Dict) -> str:
        """提交分析任务"""
        task_name = f"{task_type.replace('_', ' ').title()} Analysis"
        
        # 根据任务类型设置优先级
        priority_map = {
            'differential_expression': TaskPriority.HIGH,
            'survival_analysis': TaskPriority.HIGH,
            'pathway_enrichment': TaskPriority.NORMAL,
            'drug_sensitivity': TaskPriority.HIGH,
            'biomarker_discovery': TaskPriority.URGENT,
            'single_cell_analysis': TaskPriority.NORMAL,
            'multi_omics_integration': TaskPriority.NORMAL,
            'drug_combination_prediction': TaskPriority.HIGH
        }
        
        priority = priority_map.get(task_type, TaskPriority.NORMAL)
        
        return self.queue.submit_task(
            task_type=task_type,
            task_name=task_name,
            user_id=user_id,
            parameters=parameters,
            priority=priority
        )
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        return self.queue.get_task_status(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        return self.queue.cancel_task(task_id)
    
    def get_user_tasks(self, user_id: str) -> List[Dict]:
        """获取用户任务"""
        return self.queue.get_user_tasks(user_id)
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return self.queue.get_queue_statistics()
    
    def shutdown(self):
        """关闭队列管理器"""
        self.queue.stop_queue_processing()


def demo_task_queue():
    """演示任务队列系统"""
    
    # 创建队列管理器
    manager = TaskQueueManager()
    
    print("=== 任务队列系统演示 ===")
    
    # 提交一些测试任务
    task_ids = []
    
    # 1. 差异表达分析
    task_id1 = manager.submit_analysis_task(
        task_type='differential_expression',
        user_id='user_001',
        parameters={
            'dataset': 'TCGA-LIHC',
            'comparison_groups': ['tumor', 'normal'],
            'step_duration': 1  # 加速演示
        }
    )
    task_ids.append(task_id1)
    print(f"提交差异表达分析任务: {task_id1}")
    
    # 2. 生存分析
    task_id2 = manager.submit_analysis_task(
        task_type='survival_analysis',
        user_id='user_001',
        parameters={
            'dataset': 'TCGA-LIHC',
            'gene_list': ['TP53', 'CTNNB1'],
            'step_duration': 1
        }
    )
    task_ids.append(task_id2)
    print(f"提交生存分析任务: {task_id2}")
    
    # 3. 生物标志物发现
    task_id3 = manager.submit_analysis_task(
        task_type='biomarker_discovery',
        user_id='user_002',
        parameters={
            'dataset': 'TCGA-LIHC',
            'target_endpoint': 'overall_survival',
            'step_duration': 0.5
        }
    )
    task_ids.append(task_id3)
    print(f"提交生物标志物发现任务: {task_id3}")
    
    # 监控任务进度
    print("\n监控任务进度...")
    import time
    
    for _ in range(30):  # 监控30秒
        print(f"\n--- 时间: {datetime.now().strftime('%H:%M:%S')} ---")
        
        # 显示统计信息
        stats = manager.get_statistics()
        print(f"队列统计: 总任务 {stats['total_tasks']}, "
              f"运行中 {stats['running_tasks']}, "
              f"已完成 {stats['completed_tasks']}, "
              f"失败 {stats['failed_tasks']}")
        
        # 显示各任务状态
        for task_id in task_ids:
            status = manager.get_task_status(task_id)
            if status:
                print(f"任务 {task_id[:8]}: {status['status']} - "
                      f"{status['progress']:.1f}% - "
                      f"{status['task_type']}")
        
        time.sleep(2)
        
        # 检查是否所有任务都完成
        all_completed = True
        for task_id in task_ids:
            status = manager.get_task_status(task_id)
            if status and status['status'] not in ['completed', 'failed', 'cancelled']:
                all_completed = False
                break
        
        if all_completed:
            print("\n所有任务已完成!")
            break
    
    # 显示最终结果
    print("\n=== 最终结果 ===")
    for task_id in task_ids:
        status = manager.get_task_status(task_id)
        if status:
            print(f"\n任务 {task_id}:")
            print(f"  类型: {status['task_type']}")
            print(f"  状态: {status['status']}")
            print(f"  进度: {status['progress']:.1f}%")
            if status['elapsed_time']:
                print(f"  执行时间: {status['elapsed_time']}秒")
            if status['error_message']:
                print(f"  错误信息: {status['error_message']}")
    
    # 关闭队列管理器
    manager.shutdown()
    
    return manager


if __name__ == "__main__":
    demo_task_queue()