"""
Dataset Management System
管理用户数据集和Demo数据集的选择和切换
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class DatasetManager:
    """Manage multiple datasets and current selection"""
    
    def __init__(self, base_dir="data/datasets"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.base_dir / "dataset_config.json"
        self.load_config()
        
    def load_config(self):
        """Load dataset configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            # Check and add new demo datasets if they exist
            self._add_demo_datasets_if_exist()
        else:
            # Initialize with demo datasets
            self.config = {
                'current_dataset': 'demo',
                'datasets': {
                    'demo': {
                        'name': 'TCGA-LIHC Demo数据',
                        'type': 'demo',
                        'description': '200例肝癌患者的示例数据',
                        'created': '2025-01-01',
                        'data_path': 'examples/demo_data',
                        'features': {
                            'samples': 200,
                            'genes': 500,
                            'has_clinical': True,
                            'has_expression': True,
                            'has_mutation': True,
                            'has_cnv': True,
                            'has_methylation': True
                        }
                    }
                }
            }
            # Add new demo datasets
            self._add_demo_datasets_if_exist()
            self.save_config()
    
    def save_config(self):
        """Save dataset configuration"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _add_demo_datasets_if_exist(self):
        """Add new demo datasets if they exist on disk"""
        demo_datasets_path = Path("data/demo_datasets")
        if not demo_datasets_path.exists():
            return
        
        # Check for datasets summary
        summary_file = demo_datasets_path / "datasets_summary.json"
        if summary_file.exists():
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary_data = json.load(f)
                
                for dataset_info in summary_data.get('datasets', []):
                    dataset_id = dataset_info['id']
                    
                    # Skip if already exists
                    if dataset_id in self.config['datasets']:
                        continue
                    
                    # Add to config
                    self.config['datasets'][dataset_id] = {
                        'name': dataset_info['name'],
                        'type': 'demo',
                        'description': dataset_info['description'],
                        'created': '2025-01-27',
                        'data_path': f'data/demo_datasets/{dataset_id}',
                        'features': {
                            'samples': dataset_info['n_samples'],
                            'genes': 2000,
                            'has_clinical': True,
                            'has_expression': True,
                            'has_mutation': True,
                            'has_cnv': False,
                            'has_methylation': False
                        },
                        'characteristics': dataset_info.get('characteristics', [])
                    }
            except Exception as e:
                print(f"Error loading demo datasets summary: {e}")
    
    def add_user_dataset(self, session_id: str, name: str = None, description: str = None) -> str:
        """Add a new user dataset"""
        if not name:
            name = f"用户数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        dataset_id = f"user_{session_id}"
        
        # Get dataset features by checking files
        data_path = Path(f"data/user_uploads/{session_id}")
        features = self._analyze_dataset_features(data_path)
        
        self.config['datasets'][dataset_id] = {
            'name': name,
            'type': 'user',
            'description': description or '用户上传的数据集',
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'session_id': session_id,
            'data_path': str(data_path),
            'features': features
        }
        
        self.save_config()
        return dataset_id
    
    def _analyze_dataset_features(self, data_path: Path) -> Dict:
        """Analyze dataset features"""
        features = {
            'samples': 0,
            'genes': 0,
            'has_clinical': False,
            'has_expression': False,
            'has_mutation': False,
            'has_cnv': False,
            'has_methylation': False
        }
        
        if not data_path.exists():
            return features
        
        # Check for different data types
        import pandas as pd
        
        # Clinical data
        clinical_file = data_path / "clinical_data.csv"
        if clinical_file.exists():
            try:
                df = pd.read_csv(clinical_file)
                features['has_clinical'] = True
                features['samples'] = len(df)
            except:
                pass
        
        # Expression data
        expression_file = data_path / "expression_data.csv"
        if expression_file.exists():
            try:
                df = pd.read_csv(expression_file, index_col=0)
                features['has_expression'] = True
                features['genes'] = len(df)
                if features['samples'] == 0:
                    features['samples'] = len(df.columns)
            except:
                pass
        
        # Mutation data
        mutation_file = data_path / "mutation_data.csv"
        if mutation_file.exists():
            features['has_mutation'] = True
        
        # CNV data
        cnv_file = data_path / "cnv_data.csv"
        if cnv_file.exists():
            features['has_cnv'] = True
        
        # Methylation data
        methylation_file = data_path / "methylation_data.csv"
        if methylation_file.exists():
            features['has_methylation'] = True
        
        return features
    
    def get_current_dataset(self) -> Dict:
        """Get current dataset information"""
        current_id = self.config.get('current_dataset', 'demo')
        dataset_info = self.config['datasets'].get(current_id, self.config['datasets']['demo']).copy()
        dataset_info['id'] = current_id
        return dataset_info
    
    def set_current_dataset(self, dataset_id: str) -> bool:
        """Set current dataset"""
        if dataset_id in self.config['datasets']:
            self.config['current_dataset'] = dataset_id
            self.save_config()
            return True
        return False
    
    def list_datasets(self) -> List[Dict]:
        """List all available datasets"""
        datasets = []
        for dataset_id, info in self.config['datasets'].items():
            dataset_info = info.copy()
            dataset_info['id'] = dataset_id
            dataset_info['is_current'] = (dataset_id == self.config.get('current_dataset', 'demo'))
            datasets.append(dataset_info)
        
        # Sort by creation date, demo first
        datasets.sort(key=lambda x: (x['type'] != 'demo', x.get('created', '')))
        return datasets
    
    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset (user datasets only)"""
        if dataset_id in self.config['datasets'] and dataset_id != 'demo':
            dataset = self.config['datasets'][dataset_id]
            if dataset['type'] == 'user':
                del self.config['datasets'][dataset_id]
                
                # If this was the current dataset, switch to demo
                if self.config['current_dataset'] == dataset_id:
                    self.config['current_dataset'] = 'demo'
                
                self.save_config()
                return True
        return False
    
    def rename_dataset(self, dataset_id: str, new_name: str) -> bool:
        """Rename a dataset"""
        if dataset_id in self.config['datasets']:
            self.config['datasets'][dataset_id]['name'] = new_name
            self.save_config()
            return True
        return False
    
    def get_dataset_path(self, dataset_id: str = None) -> Path:
        """Get the data path for a dataset"""
        if not dataset_id:
            dataset_id = self.config.get('current_dataset', 'demo')
        
        if dataset_id in self.config['datasets']:
            return Path(self.config['datasets'][dataset_id]['data_path'])
        return Path('examples/demo_data')  # Fallback to demo
    
    def get_dataset_summary(self) -> Dict:
        """Get summary of all datasets"""
        summary = {
            'total_datasets': len(self.config['datasets']),
            'user_datasets': sum(1 for d in self.config['datasets'].values() if d['type'] == 'user'),
            'current_dataset': self.get_current_dataset(),
            'datasets': self.list_datasets()
        }
        return summary