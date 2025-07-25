"""
History Management System for LIHC Analysis Platform
管理上传历史和分析结果的存储与检索
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import shutil

class HistoryManager:
    """Manage upload and analysis history"""
    
    def __init__(self, base_dir="data/history"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.base_dir / "history_log.json"
        self.load_history()
    
    def load_history(self):
        """Load history from file"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = {
                'uploads': [],
                'analyses': []
            }
    
    def save_history(self):
        """Save history to file"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def add_upload_record(self, session_id: str, upload_info: Dict):
        """Add a new upload record"""
        record = {
            'session_id': session_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'files': upload_info.get('files_processed', {}),
            'validation_status': 'success' if upload_info.get('success') else 'failed',
            'errors': upload_info.get('errors', []),
            'warnings': upload_info.get('warnings', [])
        }
        
        self.history['uploads'].append(record)
        self.save_history()
        
        # Create session directory
        session_dir = self.base_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        # Save upload details
        with open(session_dir / "upload_info.json", 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        
        return record
    
    def add_analysis_record(self, session_id: str, analysis_info: Dict):
        """Add a new analysis record"""
        record = {
            'session_id': session_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'modules': analysis_info.get('modules', []),
            'status': analysis_info.get('status', 'completed'),
            'results_path': str(self.base_dir / session_id / 'results'),
            'duration': analysis_info.get('duration', 'N/A')
        }
        
        self.history['analyses'].append(record)
        self.save_history()
        
        # Save analysis details
        session_dir = self.base_dir / session_id
        with open(session_dir / "analysis_info.json", 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        
        return record
    
    def get_user_history(self, limit: int = 20) -> Dict:
        """Get recent history records"""
        # Sort by timestamp descending
        uploads = sorted(
            self.history['uploads'], 
            key=lambda x: x['timestamp'], 
            reverse=True
        )[:limit]
        
        analyses = sorted(
            self.history['analyses'], 
            key=lambda x: x['timestamp'], 
            reverse=True
        )[:limit]
        
        return {
            'uploads': uploads,
            'analyses': analyses
        }
    
    def get_session_details(self, session_id: str) -> Dict:
        """Get detailed information for a specific session"""
        session_dir = self.base_dir / session_id
        
        if not session_dir.exists():
            return {'error': 'Session not found'}
        
        details = {
            'session_id': session_id,
            'upload_info': None,
            'analysis_info': None,
            'files': [],
            'results': []
        }
        
        # Load upload info
        upload_file = session_dir / "upload_info.json"
        if upload_file.exists():
            with open(upload_file, 'r', encoding='utf-8') as f:
                details['upload_info'] = json.load(f)
        
        # Load analysis info
        analysis_file = session_dir / "analysis_info.json"
        if analysis_file.exists():
            with open(analysis_file, 'r', encoding='utf-8') as f:
                details['analysis_info'] = json.load(f)
        
        # List uploaded files
        data_dir = Path(f"data/user_uploads/{session_id}")
        if data_dir.exists():
            details['files'] = [f.name for f in data_dir.glob("*.csv")]
        
        # List result files
        results_dir = session_dir / "results"
        if results_dir.exists():
            details['results'] = [f.name for f in results_dir.glob("*")]
        
        return details
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its data"""
        try:
            # Remove from history
            self.history['uploads'] = [
                u for u in self.history['uploads'] 
                if u['session_id'] != session_id
            ]
            self.history['analyses'] = [
                a for a in self.history['analyses'] 
                if a['session_id'] != session_id
            ]
            self.save_history()
            
            # Delete directories
            session_dir = self.base_dir / session_id
            if session_dir.exists():
                shutil.rmtree(session_dir)
            
            data_dir = Path(f"data/user_uploads/{session_id}")
            if data_dir.exists():
                shutil.rmtree(data_dir)
            
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def export_history(self, format: str = 'csv') -> Path:
        """Export history to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'csv':
            # Convert to DataFrame for easy export
            uploads_df = pd.DataFrame(self.history['uploads'])
            analyses_df = pd.DataFrame(self.history['analyses'])
            
            export_dir = self.base_dir / 'exports'
            export_dir.mkdir(exist_ok=True)
            
            uploads_file = export_dir / f'uploads_history_{timestamp}.csv'
            analyses_file = export_dir / f'analyses_history_{timestamp}.csv'
            
            uploads_df.to_csv(uploads_file, index=False)
            analyses_df.to_csv(analyses_file, index=False)
            
            return export_dir
        
        elif format == 'json':
            export_file = self.base_dir / f'history_export_{timestamp}.json'
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            return export_file
    
    def get_statistics(self) -> Dict:
        """Get history statistics"""
        stats = {
            'total_uploads': len(self.history['uploads']),
            'successful_uploads': sum(1 for u in self.history['uploads'] if u['validation_status'] == 'success'),
            'failed_uploads': sum(1 for u in self.history['uploads'] if u['validation_status'] == 'failed'),
            'total_analyses': len(self.history['analyses']),
            'unique_sessions': len(set(u['session_id'] for u in self.history['uploads'])),
            'recent_activity': []
        }
        
        # Get recent activity (last 7 days)
        from datetime import datetime, timedelta
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        recent_uploads = [
            u for u in self.history['uploads']
            if datetime.strptime(u['timestamp'], '%Y-%m-%d %H:%M:%S') > seven_days_ago
        ]
        
        recent_analyses = [
            a for a in self.history['analyses']
            if datetime.strptime(a['timestamp'], '%Y-%m-%d %H:%M:%S') > seven_days_ago
        ]
        
        stats['recent_uploads'] = len(recent_uploads)
        stats['recent_analyses'] = len(recent_analyses)
        
        return stats