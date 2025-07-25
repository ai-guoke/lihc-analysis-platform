"""
Analysis Progress Manager
分析进度管理器 - 实时跟踪和显示分析进度
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import threading

class ProgressManager:
    """Manage and track analysis progress"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.progress_dir = Path(f"data/history/{session_id}/progress")
        self.progress_dir.mkdir(parents=True, exist_ok=True)
        self.progress_file = self.progress_dir / "progress.json"
        
        # Initialize progress
        self.progress = {
            'session_id': session_id,
            'status': 'initializing',
            'overall_progress': 0,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'current_module': None,
            'modules': {},
            'logs': [],
            'errors': []
        }
        
        self._save_progress()
    
    def start_analysis(self, modules: List[str]):
        """Start analysis with specified modules"""
        self.progress['status'] = 'running'
        self.progress['start_time'] = datetime.now().isoformat()
        
        # Initialize module progress
        for module in modules:
            self.progress['modules'][module] = {
                'status': 'pending',
                'progress': 0,
                'start_time': None,
                'end_time': None,
                'message': 'Waiting to start'
            }
        
        self._save_progress()
        self.add_log(f"Analysis started with modules: {', '.join(modules)}")
    
    def start_module(self, module: str, message: str = None):
        """Start a specific module"""
        if module in self.progress['modules']:
            self.progress['modules'][module]['status'] = 'running'
            self.progress['modules'][module]['start_time'] = datetime.now().isoformat()
            self.progress['modules'][module]['message'] = message or f'Running {module}...'
            self.progress['current_module'] = module
            
            self._update_overall_progress()
            self._save_progress()
            self.add_log(f"Started module: {module}")
    
    def update_module_progress(self, module: str, progress: float, message: str = None):
        """Update progress for a specific module"""
        if module in self.progress['modules']:
            self.progress['modules'][module]['progress'] = min(progress, 100)
            if message:
                self.progress['modules'][module]['message'] = message
            
            self._update_overall_progress()
            self._save_progress()
    
    def complete_module(self, module: str, message: str = None):
        """Mark a module as completed"""
        if module in self.progress['modules']:
            self.progress['modules'][module]['status'] = 'completed'
            self.progress['modules'][module]['progress'] = 100
            self.progress['modules'][module]['end_time'] = datetime.now().isoformat()
            self.progress['modules'][module]['message'] = message or f'{module} completed successfully'
            
            # Check if all modules completed
            all_completed = all(
                m['status'] == 'completed' 
                for m in self.progress['modules'].values()
            )
            
            if all_completed:
                self.complete_analysis()
            else:
                self._update_overall_progress()
                self._save_progress()
            
            self.add_log(f"Completed module: {module}")
    
    def fail_module(self, module: str, error: str):
        """Mark a module as failed"""
        if module in self.progress['modules']:
            self.progress['modules'][module]['status'] = 'failed'
            self.progress['modules'][module]['end_time'] = datetime.now().isoformat()
            self.progress['modules'][module]['message'] = f'Failed: {error}'
            
            self.add_error(f"Module {module} failed: {error}")
            self._update_overall_progress()
            self._save_progress()
    
    def complete_analysis(self):
        """Mark entire analysis as completed"""
        self.progress['status'] = 'completed'
        self.progress['end_time'] = datetime.now().isoformat()
        self.progress['overall_progress'] = 100
        self.progress['current_module'] = None
        
        # Calculate duration
        start = datetime.fromisoformat(self.progress['start_time'])
        end = datetime.fromisoformat(self.progress['end_time'])
        duration = (end - start).total_seconds()
        self.progress['duration_seconds'] = duration
        
        self._save_progress()
        self.add_log(f"Analysis completed in {duration:.1f} seconds")
    
    def fail_analysis(self, error: str):
        """Mark entire analysis as failed"""
        self.progress['status'] = 'failed'
        self.progress['end_time'] = datetime.now().isoformat()
        self.progress['current_module'] = None
        
        self.add_error(f"Analysis failed: {error}")
        self._save_progress()
    
    def add_log(self, message: str):
        """Add a log message"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message
        }
        self.progress['logs'].append(log_entry)
        
        # Keep only last 100 logs
        if len(self.progress['logs']) > 100:
            self.progress['logs'] = self.progress['logs'][-100:]
        
        self._save_progress()
    
    def add_error(self, error: str):
        """Add an error message"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error': error
        }
        self.progress['errors'].append(error_entry)
        self._save_progress()
    
    def get_progress(self) -> Dict:
        """Get current progress"""
        return self.progress.copy()
    
    def _update_overall_progress(self):
        """Update overall progress based on module progress"""
        if not self.progress['modules']:
            return
        
        total_progress = sum(
            m['progress'] for m in self.progress['modules'].values()
        )
        self.progress['overall_progress'] = total_progress / len(self.progress['modules'])
    
    def _save_progress(self):
        """Save progress to file"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            print(f"Failed to save progress: {e}")
    
    @classmethod
    def load_progress(cls, session_id: str) -> Optional[Dict]:
        """Load progress for a session"""
        progress_file = Path(f"data/history/{session_id}/progress/progress.json")
        if progress_file.exists():
            try:
                with open(progress_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None


class ProgressUpdater:
    """Context manager for automatic progress updates"""
    
    def __init__(self, progress_manager: ProgressManager, module: str, 
                 total_steps: int = 100):
        self.progress_manager = progress_manager
        self.module = module
        self.total_steps = total_steps
        self.current_step = 0
    
    def __enter__(self):
        self.progress_manager.start_module(self.module)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.progress_manager.complete_module(self.module)
        else:
            self.progress_manager.fail_module(self.module, str(exc_val))
    
    def update(self, step: int = None, message: str = None):
        """Update progress"""
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
        
        progress = (self.current_step / self.total_steps) * 100
        self.progress_manager.update_module_progress(
            self.module, progress, message
        )


def create_progress_callback(app, progress_manager: ProgressManager):
    """Create Dash callback for progress updates"""
    from dash import Output, Input, State, callback_context
    import dash
    
    # @app.callback(
    #     Output('analysis-progress', 'children'),
    #     Output('analysis-progress-modal', 'style'),
    #     Input('progress-interval', 'n_intervals'),
    #     State('current-session-id', 'data'),
    #     prevent_initial_call=True
    # )
    def update_progress_display(n_intervals, session_id):
        if not session_id:
            return dash.no_update, {'display': 'none'}
        
        # Load progress
        progress = ProgressManager.load_progress(session_id)
        if not progress:
            return dash.no_update, {'display': 'none'}
        
        # Create progress display
        import dash.html as html
        import dash.dcc as dcc
        
        content = [
            html.H3("分析进度", style={'marginBottom': '20px'}),
            
            # Overall progress
            html.Div([
                html.Label(f"总体进度: {progress['overall_progress']:.1f}%"),
                html.Progress(
                    value=progress['overall_progress'],
                    max=100,
                    style={'width': '100%', 'height': '30px'}
                )
            ], style={'marginBottom': '20px'}),
            
            # Status
            html.Div([
                html.Span("状态: ", style={'fontWeight': 'bold'}),
                html.Span(
                    progress['status'],
                    style={
                        'color': {
                            'running': '#f39c12',
                            'completed': '#27ae60',
                            'failed': '#e74c3c'
                        }.get(progress['status'], '#95a5a6')
                    }
                )
            ], style={'marginBottom': '10px'}),
            
            # Current module
            html.Div([
                html.Span("当前模块: ", style={'fontWeight': 'bold'}),
                html.Span(progress.get('current_module', 'N/A'))
            ], style={'marginBottom': '20px'}),
            
            # Module details
            html.H4("模块进度:"),
            html.Div([
                html.Div([
                    html.Div([
                        html.Span(f"{module}: ", style={'fontWeight': 'bold'}),
                        html.Span(f"{info['progress']:.0f}%"),
                        html.Span(
                            f" - {info['message']}",
                            style={'fontSize': '0.9rem', 'color': '#666'}
                        )
                    ]),
                    html.Progress(
                        value=info['progress'],
                        max=100,
                        style={'width': '100%', 'height': '20px'}
                    )
                ], style={'marginBottom': '10px'})
                for module, info in progress.get('modules', {}).items()
            ]),
            
            # Recent logs
            html.H4("最近日志:", style={'marginTop': '20px'}),
            html.Div([
                html.Div(
                    f"[{log['timestamp'].split('T')[1].split('.')[0]}] {log['message']}",
                    style={'fontSize': '0.9rem', 'fontFamily': 'monospace'}
                )
                for log in progress.get('logs', [])[-5:]
            ], style={'maxHeight': '150px', 'overflowY': 'auto', 
                     'backgroundColor': '#f5f5f5', 'padding': '10px'}),
        ]
        
        # Add errors if any
        if progress.get('errors'):
            content.append(
                html.Div([
                    html.H4("错误:", style={'color': '#e74c3c'}),
                    html.Div([
                        html.Div(
                            f"[{err['timestamp'].split('T')[1].split('.')[0]}] {err['error']}",
                            style={'fontSize': '0.9rem', 'color': '#e74c3c'}
                        )
                        for err in progress['errors'][-3:]
                    ])
                ])
            )
        
        # Show/hide modal based on status
        modal_style = {
            'display': 'block' if progress['status'] == 'running' else 'none',
            'position': 'fixed',
            'top': '50%',
            'left': '50%',
            'transform': 'translate(-50%, -50%)',
            'backgroundColor': 'white',
            'padding': '30px',
            'borderRadius': '10px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
            'zIndex': '1001',
            'maxWidth': '600px',
            'width': '90%',
            'maxHeight': '80vh',
            'overflowY': 'auto'
        }
        
        return html.Div(content), modal_style
    
    return update_progress_display