"""
Batch Data Processing Module
批量数据处理模块 - 支持同时处理多个数据集
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime
import concurrent.futures
import threading
from dataclasses import dataclass
import uuid

from .simplified_analyzer import SimplifiedAnalyzer
from .progress_manager import ProgressManager
from .data_loader import data_loader

@dataclass
class BatchJob:
    """Batch job configuration"""
    job_id: str
    dataset_ids: List[str]
    modules: List[str]
    status: str = 'pending'
    created_at: str = None
    completed_at: str = None
    results: Dict = None
    errors: Dict = None
    celery_task_id: str = None  # Add Celery task ID
    
    def __post_init__(self):
        if not self.job_id:
            self.job_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class BatchProcessor:
    """Process multiple datasets in parallel"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.jobs = {}
        self.job_lock = threading.Lock()
        self.results_dir = Path("data/batch_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def create_batch_job(self, dataset_ids: List[str], modules: List[str], 
                        dataset_manager=None) -> str:
        """Create a new batch processing job"""
        job = BatchJob(
            job_id=str(uuid.uuid4()),
            dataset_ids=dataset_ids,
            modules=modules
        )
        
        with self.job_lock:
            self.jobs[job.job_id] = job
        
        # Save job configuration
        job_file = self.results_dir / f"{job.job_id}_config.json"
        with open(job_file, 'w') as f:
            json.dump({
                'job_id': job.job_id,
                'dataset_ids': dataset_ids,
                'modules': modules,
                'created_at': job.created_at,
                'status': job.status
            }, f, indent=2)
        
        return job.job_id
    
    def process_batch(self, job_id: str, dataset_manager=None, 
                     progress_callback=None, use_celery=True) -> Dict:
        """Process all datasets in the batch"""
        job = self.jobs.get(job_id)
        if not job:
            return {'error': f'Job {job_id} not found'}
        
        # Update job status
        job.status = 'running'
        results = {}
        errors = {}
        
        # Create overall progress manager
        overall_progress = ProgressManager(f"batch_{job_id}")
        overall_progress.start_analysis([f"dataset_{i}" for i in range(len(job.dataset_ids))])
        
        try:
            # Check if Celery is available and should be used
            if use_celery:
                try:
                    from src.analysis.task_queue import batch_analysis_task
                    
                    # Submit to Celery
                    celery_result = batch_analysis_task.apply_async(
                        args=[job_id, job.dataset_ids, job.modules],
                        queue='batch'
                    )
                    
                    # Store Celery task ID
                    job.celery_task_id = celery_result.id
                    self._save_job_state(job)
                    
                    # Return immediately with Celery task info
                    return {
                        'job_id': job_id,
                        'status': 'submitted',
                        'celery_task_id': celery_result.id,
                        'message': 'Batch job submitted to task queue'
                    }
                    
                except ImportError:
                    # Fall back to threading if Celery not available
                    use_celery = False
            
            # Process datasets in parallel using threading
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all dataset processing tasks
                future_to_dataset = {}
                
                for idx, dataset_id in enumerate(job.dataset_ids):
                    # Get dataset info
                    if dataset_manager:
                        dataset_info = dataset_manager.get_dataset(dataset_id)
                    else:
                        dataset_info = {
                            'id': dataset_id,
                            'name': f'Dataset {dataset_id}',
                            'type': 'user' if dataset_id != 'demo' else 'demo'
                        }
                    
                    # Submit processing task
                    future = executor.submit(
                        self._process_single_dataset,
                        dataset_id,
                        dataset_info,
                        job.modules,
                        f"batch_{job_id}_dataset_{idx}"
                    )
                    future_to_dataset[future] = (dataset_id, idx)
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_dataset):
                    dataset_id, idx = future_to_dataset[future]
                    
                    try:
                        result = future.result()
                        results[dataset_id] = result
                        
                        # Update overall progress
                        overall_progress.complete_module(
                            f"dataset_{idx}", 
                            f"Completed analysis for {dataset_id}"
                        )
                        
                        if progress_callback:
                            progress_callback({
                                'job_id': job_id,
                                'completed': len(results),
                                'total': len(job.dataset_ids),
                                'current_dataset': dataset_id
                            })
                    
                    except Exception as e:
                        errors[dataset_id] = str(e)
                        overall_progress.fail_module(
                            f"dataset_{idx}",
                            f"Failed to process {dataset_id}: {str(e)}"
                        )
            
            # Generate batch summary report
            summary = self._generate_batch_summary(job, results, errors)
            
            # Update job
            job.status = 'completed' if not errors else 'completed_with_errors'
            job.completed_at = datetime.now().isoformat()
            job.results = results
            job.errors = errors
            
            # Save results
            self._save_batch_results(job, summary)
            
            overall_progress.complete_analysis()
            
            return {
                'job_id': job_id,
                'status': job.status,
                'summary': summary,
                'results': results,
                'errors': errors
            }
            
        except Exception as e:
            job.status = 'failed'
            overall_progress.fail_analysis(str(e))
            return {
                'job_id': job_id,
                'status': 'failed',
                'error': str(e)
            }
    
    def _process_single_dataset(self, dataset_id: str, dataset_info: Dict, 
                               modules: List[str], session_id: str) -> Dict:
        """Process a single dataset"""
        try:
            # Create progress manager for this dataset
            progress_manager = ProgressManager(session_id)
            
            # Use SimplifiedAnalyzer which handles both simplified and advanced analysis
            analyzer = SimplifiedAnalyzer(session_id)
            
            # Run analysis
            results = analyzer.run_all_analyses(modules, progress_manager)
            
            return {
                'dataset_id': dataset_id,
                'dataset_name': dataset_info.get('name', dataset_id),
                'status': 'success',
                'results': results
            }
            
        except Exception as e:
            return {
                'dataset_id': dataset_id,
                'dataset_name': dataset_info.get('name', dataset_id),
                'status': 'error',
                'error': str(e)
            }
    
    def _generate_batch_summary(self, job: BatchJob, results: Dict, 
                               errors: Dict) -> Dict:
        """Generate summary report for batch processing"""
        summary = {
            'job_id': job.job_id,
            'created_at': job.created_at,
            'completed_at': job.completed_at,
            'total_datasets': len(job.dataset_ids),
            'successful': len(results),
            'failed': len(errors),
            'modules_run': job.modules,
            'dataset_summaries': []
        }
        
        # Add summary for each dataset
        for dataset_id in job.dataset_ids:
            if dataset_id in results:
                result = results[dataset_id]
                dataset_summary = {
                    'dataset_id': dataset_id,
                    'dataset_name': result.get('dataset_name', dataset_id),
                    'status': 'success',
                    'modules_completed': result['results'].get('modules_completed', []),
                    'files_generated': len(result['results'].get('files_generated', [])),
                    'report_path': result['results'].get('report_path', '')
                }
            else:
                dataset_summary = {
                    'dataset_id': dataset_id,
                    'status': 'failed',
                    'error': errors.get(dataset_id, 'Unknown error')
                }
            
            summary['dataset_summaries'].append(dataset_summary)
        
        return summary
    
    def _save_batch_results(self, job: BatchJob, summary: Dict):
        """Save batch processing results"""
        # Save summary
        summary_file = self.results_dir / f"{job.job_id}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Generate HTML report
        html_report = self._generate_batch_html_report(job, summary)
        report_file = self.results_dir / f"{job.job_id}_report.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
    
    def _generate_batch_html_report(self, job: BatchJob, summary: Dict) -> str:
        """Generate HTML report for batch processing"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Batch Analysis Report - {job.job_id[:8]}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    line-height: 1.6;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{ 
                    color: #2c3e50; 
                    border-bottom: 3px solid #3498db; 
                    padding-bottom: 10px; 
                }}
                h2 {{ 
                    color: #34495e; 
                    margin-top: 30px; 
                }}
                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .summary-card {{
                    background: #ecf0f1;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    border-left: 4px solid #3498db;
                }}
                .summary-card h3 {{
                    margin: 0 0 10px 0;
                    color: #2c3e50;
                    font-size: 2rem;
                }}
                .summary-card p {{
                    margin: 0;
                    color: #7f8c8d;
                }}
                .dataset-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .dataset-table th {{
                    background: #3498db;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                .dataset-table td {{
                    padding: 12px;
                    border-bottom: 1px solid #ddd;
                }}
                .dataset-table tr:nth-child(even) {{
                    background: #f8f9fa;
                }}
                .status-success {{
                    color: #27ae60;
                    font-weight: bold;
                }}
                .status-failed {{
                    color: #e74c3c;
                    font-weight: bold;
                }}
                .modules-list {{
                    display: inline-flex;
                    gap: 8px;
                    flex-wrap: wrap;
                }}
                .module-tag {{
                    background: #3498db;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 0.85rem;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>批量分析报告</h1>
                
                <div class="summary-grid">
                    <div class="summary-card">
                        <h3>{summary['total_datasets']}</h3>
                        <p>总数据集数</p>
                    </div>
                    <div class="summary-card">
                        <h3>{summary['successful']}</h3>
                        <p>成功完成</p>
                    </div>
                    <div class="summary-card">
                        <h3>{summary['failed']}</h3>
                        <p>处理失败</p>
                    </div>
                    <div class="summary-card">
                        <h3>{len(summary['modules_run'])}</h3>
                        <p>分析模块数</p>
                    </div>
                </div>
                
                <h2>作业信息</h2>
                <p><strong>作业ID:</strong> {job.job_id}</p>
                <p><strong>创建时间:</strong> {summary['created_at']}</p>
                <p><strong>完成时间:</strong> {summary['completed_at']}</p>
                <p><strong>分析模块:</strong></p>
                <div class="modules-list">
                    {''.join([f'<span class="module-tag">{m}</span>' for m in summary['modules_run']])}
                </div>
                
                <h2>数据集处理详情</h2>
                <table class="dataset-table">
                    <thead>
                        <tr>
                            <th>数据集ID</th>
                            <th>数据集名称</th>
                            <th>状态</th>
                            <th>完成模块</th>
                            <th>生成文件数</th>
                            <th>报告路径</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for ds in summary['dataset_summaries']:
            status_class = 'status-success' if ds['status'] == 'success' else 'status-failed'
            status_text = '成功' if ds['status'] == 'success' else '失败'
            
            if ds['status'] == 'success':
                modules = ', '.join(ds.get('modules_completed', []))
                files = ds.get('files_generated', 0)
                report = ds.get('report_path', 'N/A')
            else:
                modules = 'N/A'
                files = 'N/A'
                report = ds.get('error', 'Unknown error')
            
            html_content += f"""
                        <tr>
                            <td>{ds['dataset_id']}</td>
                            <td>{ds.get('dataset_name', ds['dataset_id'])}</td>
                            <td class="{status_class}">{status_text}</td>
                            <td>{modules}</td>
                            <td>{files}</td>
                            <td>{report}</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
                
                <p style="text-align: center; margin-top: 40px; color: #7f8c8d;">
                    Generated by LIHC Analysis Platform Batch Processor
                </p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def get_job_status(self, job_id: str) -> Dict:
        """Get current status of a batch job"""
        job = self.jobs.get(job_id)
        if not job:
            # Try to load from file
            job_file = self.results_dir / f"{job_id}_summary.json"
            if job_file.exists():
                with open(job_file, 'r') as f:
                    return json.load(f)
            return {'error': f'Job {job_id} not found'}
        
        status_info = {
            'job_id': job.job_id,
            'status': job.status,
            'created_at': job.created_at,
            'completed_at': job.completed_at,
            'total_datasets': len(job.dataset_ids),
            'modules': job.modules
        }
        
        # Check Celery task status if available
        if job.celery_task_id:
            try:
                from src.analysis.task_queue import task_queue_manager
                celery_status = task_queue_manager.get_task_status(job.celery_task_id)
                status_info['celery_status'] = celery_status
                
                # Update job status based on Celery status
                if celery_status['state'] == 'SUCCESS':
                    job.status = 'completed'
                elif celery_status['state'] == 'FAILURE':
                    job.status = 'failed'
                elif celery_status['state'] == 'PROGRESS':
                    status_info['progress'] = celery_status.get('progress', 0)
                    status_info['message'] = celery_status.get('message', '')
            except:
                pass
        
        return status_info
    
    def _save_job_state(self, job: BatchJob):
        """Save job state to file"""
        job_file = self.results_dir / f"{job.job_id}_state.json"
        with open(job_file, 'w') as f:
            json.dump({
                'job_id': job.job_id,
                'dataset_ids': job.dataset_ids,
                'modules': job.modules,
                'status': job.status,
                'created_at': job.created_at,
                'completed_at': job.completed_at,
                'celery_task_id': job.celery_task_id
            }, f, indent=2)
    
    def list_jobs(self) -> List[Dict]:
        """List all batch jobs"""
        jobs = []
        
        # Get active jobs
        for job_id, job in self.jobs.items():
            jobs.append({
                'job_id': job.job_id,
                'status': job.status,
                'created_at': job.created_at,
                'datasets': len(job.dataset_ids),
                'modules': len(job.modules)
            })
        
        # Get completed jobs from files
        for summary_file in self.results_dir.glob("*_summary.json"):
            job_id = summary_file.stem.replace('_summary', '')
            if job_id not in self.jobs:
                try:
                    with open(summary_file, 'r') as f:
                        summary = json.load(f)
                        jobs.append({
                            'job_id': job_id,
                            'status': 'completed',
                            'created_at': summary.get('created_at', 'Unknown'),
                            'datasets': summary.get('total_datasets', 0),
                            'modules': len(summary.get('modules_run', []))
                        })
                except:
                    continue
        
        # Sort by creation time
        jobs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jobs


# Global batch processor instance
batch_processor = BatchProcessor()


def create_batch_processor_ui(app, dataset_manager):
    """Create UI components for batch processing"""
    from dash import dcc, html, Input, Output, State, callback_context
    import dash
    
    # Add batch processing callbacks
    @app.callback(
        [Output('batch-job-status', 'children'),
         Output('batch-job-id', 'data')],
        [Input('start-batch-analysis', 'n_clicks')],
        [State('batch-dataset-selection', 'value'),
         State('batch-modules-selection', 'value')],
        prevent_initial_call=True
    )
    def start_batch_processing(n_clicks, selected_datasets, selected_modules):
        if not n_clicks or not selected_datasets or not selected_modules:
            return dash.no_update, dash.no_update
        
        # Create batch job
        job_id = batch_processor.create_batch_job(
            selected_datasets, 
            selected_modules,
            dataset_manager
        )
        
        # Start processing in background thread
        import threading
        thread = threading.Thread(
            target=batch_processor.process_batch,
            args=(job_id, dataset_manager)
        )
        thread.start()
        
        # Return status message
        status_msg = html.Div([
            html.H4([
                html.I(className="fas fa-spinner fa-spin"),
                f" 批量处理作业已启动"
            ], style={'color': '#3498db'}),
            html.P(f"作业ID: {job_id[:8]}..."),
            html.P(f"处理 {len(selected_datasets)} 个数据集"),
            html.P(f"运行 {len(selected_modules)} 个分析模块"),
            html.Hr(),
            html.P("处理完成后可在批量结果页面查看详情。")
        ])
        
        return status_msg, job_id
    
    return app