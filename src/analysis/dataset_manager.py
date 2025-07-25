"""
Dataset Management System
数据集管理系统 - 提供全面的数据集管理功能
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import hashlib
import shutil
import os
from dataclasses import dataclass, asdict

@dataclass
class DatasetInfo:
    """Dataset information structure"""
    id: str
    name: str
    type: str  # 'demo', 'user', 'generated'
    status: str  # 'active', 'archived', 'processing', 'error'
    created_at: str
    modified_at: str
    size_mb: float
    samples: int
    genes: int
    features: Dict  # data availability flags
    metadata: Dict  # additional metadata
    analysis_history: List  # analysis runs on this dataset
    tags: List[str]  # user-defined tags
    description: str
    location: str  # file path or storage location

class DatasetManager:
    """Comprehensive dataset management system"""
    
    def __init__(self, base_dir="data"):
        self.base_dir = Path(base_dir)
        self.datasets_dir = self.base_dir / "datasets"
        self.metadata_dir = self.base_dir / "metadata"
        self.demo_dir = self.base_dir / "demo"
        self.uploads_dir = self.base_dir / "user_uploads"
        self.analysis_dir = self.base_dir / "analysis_results"
        
        # Ensure directories exist
        for dir_path in [self.datasets_dir, self.metadata_dir, self.demo_dir, 
                        self.uploads_dir, self.analysis_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize dataset registry
        self.registry_file = self.metadata_dir / "dataset_registry.json"
        self.current_dataset_id = None
        self._load_registry()
    
    def _load_registry(self):
        """Load dataset registry from file"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)
                self.datasets = {
                    dataset_id: DatasetInfo(**info) 
                    for dataset_id, info in registry_data.get('datasets', {}).items()
                }
                self.current_dataset_id = registry_data.get('current_dataset_id', 'demo')
        else:
            self.datasets = {}
            self.current_dataset_id = 'demo'
            self._initialize_demo_datasets()
    
    def _save_registry(self):
        """Save dataset registry to file"""
        registry_data = {
            'datasets': {
                dataset_id: asdict(info) 
                for dataset_id, info in self.datasets.items()
            },
            'current_dataset_id': self.current_dataset_id,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry_data, f, ensure_ascii=False, indent=2)
    
    def _initialize_demo_datasets(self):
        """Initialize demo datasets"""
        demo_datasets = [
            {
                'id': 'demo',
                'name': 'LIHC Demo Dataset',
                'type': 'demo',
                'status': 'active',
                'description': 'Liver Hepatocellular Carcinoma demonstration dataset with clinical, expression, and mutation data',
                'samples': 374,
                'genes': 20531,
                'features': {
                    'has_clinical': True,
                    'has_expression': True,
                    'has_mutation': True,
                    'has_methylation': False,
                    'has_cnv': False
                },
                'tags': ['demo', 'lihc', 'tcga'],
                'location': str(self.demo_dir)
            },
            {
                'id': 'demo_small',
                'name': 'LIHC Small Demo',
                'type': 'demo',
                'status': 'active',
                'description': 'Small subset for quick testing',
                'samples': 50,
                'genes': 1000,
                'features': {
                    'has_clinical': True,
                    'has_expression': True,
                    'has_mutation': False,
                    'has_methylation': False,
                    'has_cnv': False
                },
                'tags': ['demo', 'small', 'test'],
                'location': str(self.demo_dir / "small")
            }
        ]
        
        for ds_info in demo_datasets:
            dataset = DatasetInfo(
                created_at=datetime.now().isoformat(),
                modified_at=datetime.now().isoformat(),
                size_mb=self._calculate_dataset_size(ds_info['location']),
                metadata={
                    'source': 'TCGA',
                    'tumor_type': 'LIHC',
                    'platform': 'RNA-Seq',
                    'preprocessing': 'log2(FPKM+1)'
                },
                analysis_history=[],
                **ds_info
            )
            self.datasets[dataset.id] = dataset
        
        self._save_registry()
    
    def _calculate_dataset_size(self, location: str) -> float:
        """Calculate dataset size in MB"""
        try:
            location_path = Path(location)
            if location_path.exists():
                total_size = 0
                if location_path.is_file():
                    total_size = location_path.stat().st_size
                else:
                    for file_path in location_path.rglob('*'):
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
                return total_size / (1024 * 1024)  # Convert to MB
        except:
            pass
        return 0.0
    
    def add_dataset(self, name: str, dataset_type: str, location: str, 
                   description: str = "", tags: List[str] = None, 
                   metadata: Dict = None) -> str:
        """Add a new dataset to registry"""
        dataset_id = self._generate_dataset_id(name)
        
        # Analyze dataset to get features
        features = self._analyze_dataset_features(location)
        
        dataset = DatasetInfo(
            id=dataset_id,
            name=name,
            type=dataset_type,
            status='active',
            created_at=datetime.now().isoformat(),
            modified_at=datetime.now().isoformat(),
            size_mb=self._calculate_dataset_size(location),
            samples=features.get('samples', 0),
            genes=features.get('genes', 0),
            features=features.get('data_types', {}),
            metadata=metadata or {},
            analysis_history=[],
            tags=tags or [],
            description=description,
            location=location
        )
        
        self.datasets[dataset_id] = dataset
        self._save_registry()
        
        return dataset_id
    
    def _generate_dataset_id(self, name: str) -> str:
        """Generate unique dataset ID"""
        base_id = name.lower().replace(' ', '_').replace('-', '_')
        base_id = ''.join(c for c in base_id if c.isalnum() or c == '_')
        
        # Ensure uniqueness
        if base_id not in self.datasets:
            return base_id
        
        counter = 1
        while f"{base_id}_{counter}" in self.datasets:
            counter += 1
        return f"{base_id}_{counter}"
    
    def _analyze_dataset_features(self, location: str) -> Dict:
        """Analyze dataset to extract features"""
        features = {
            'samples': 0,
            'genes': 0,
            'data_types': {
                'has_clinical': False,
                'has_expression': False,
                'has_mutation': False,
                'has_methylation': False,
                'has_cnv': False
            }
        }
        
        try:
            location_path = Path(location)
            if not location_path.exists():
                return features
            
            # Check for data files
            for file_path in location_path.rglob('*'):
                if file_path.is_file():
                    filename = file_path.name.lower()
                    
                    if 'clinical' in filename:
                        features['data_types']['has_clinical'] = True
                        # Try to count samples from clinical file
                        try:
                            df = pd.read_csv(file_path)
                            features['samples'] = max(features['samples'], len(df))
                        except:
                            pass
                    
                    elif 'expression' in filename or 'expr' in filename:
                        features['data_types']['has_expression'] = True
                        # Try to count genes and samples from expression file
                        try:
                            df = pd.read_csv(file_path, index_col=0)
                            features['genes'] = max(features['genes'], len(df))
                            features['samples'] = max(features['samples'], len(df.columns))
                        except:
                            pass
                    
                    elif 'mutation' in filename or 'mut' in filename:
                        features['data_types']['has_mutation'] = True
                    
                    elif 'methylation' in filename or 'meth' in filename:
                        features['data_types']['has_methylation'] = True
                    
                    elif 'cnv' in filename or 'copy' in filename:
                        features['data_types']['has_cnv'] = True
        
        except Exception as e:
            print(f"Error analyzing dataset features: {e}")
        
        return features
    
    def get_dataset(self, dataset_id: str) -> Optional[DatasetInfo]:
        """Get dataset by ID"""
        return self.datasets.get(dataset_id)
    
    def list_datasets(self, dataset_type: str = None, status: str = None, 
                     tags: List[str] = None) -> List[DatasetInfo]:
        """List datasets with optional filters"""
        datasets = list(self.datasets.values())
        
        if dataset_type:
            datasets = [ds for ds in datasets if ds.type == dataset_type]
        
        if status:
            datasets = [ds for ds in datasets if ds.status == status]
        
        if tags:
            datasets = [ds for ds in datasets 
                       if any(tag in ds.tags for tag in tags)]
        
        # Sort by modified date (newest first)
        datasets.sort(key=lambda x: x.modified_at, reverse=True)
        
        return datasets
    
    def update_dataset(self, dataset_id: str, **kwargs) -> bool:
        """Update dataset information"""
        if dataset_id not in self.datasets:
            return False
        
        dataset = self.datasets[dataset_id]
        
        # Update allowed fields
        updateable_fields = ['name', 'description', 'tags', 'status', 'metadata']
        for field, value in kwargs.items():
            if field in updateable_fields:
                setattr(dataset, field, value)
        
        dataset.modified_at = datetime.now().isoformat()
        self._save_registry()
        return True
    
    def delete_dataset(self, dataset_id: str, remove_files: bool = False) -> bool:
        """Delete dataset from registry"""
        if dataset_id not in self.datasets:
            return False
        
        dataset = self.datasets[dataset_id]
        
        # Don't allow deletion of demo datasets
        if dataset.type == 'demo':
            return False
        
        # Remove files if requested
        if remove_files and dataset.location:
            try:
                location_path = Path(dataset.location)
                if location_path.exists():
                    if location_path.is_file():
                        location_path.unlink()
                    else:
                        shutil.rmtree(location_path)
            except Exception as e:
                print(f"Error removing dataset files: {e}")
        
        # Remove from registry
        del self.datasets[dataset_id]
        
        # Update current dataset if needed
        if self.current_dataset_id == dataset_id:
            self.current_dataset_id = 'demo'
        
        self._save_registry()
        return True
    
    def set_current_dataset(self, dataset_id: str) -> bool:
        """Set current active dataset"""
        if dataset_id in self.datasets:
            self.current_dataset_id = dataset_id
            self._save_registry()
            return True
        return False
    
    def get_current_dataset(self) -> Optional[DatasetInfo]:
        """Get current active dataset"""
        return self.datasets.get(self.current_dataset_id)
    
    def add_analysis_record(self, dataset_id: str, analysis_info: Dict) -> bool:
        """Add analysis record to dataset history"""
        if dataset_id not in self.datasets:
            return False
        
        analysis_record = {
            'analysis_id': analysis_info.get('analysis_id', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'modules': analysis_info.get('modules', []),
            'status': analysis_info.get('status', 'completed'),
            'results_path': analysis_info.get('results_path', ''),
            'duration': analysis_info.get('duration', 0)
        }
        
        self.datasets[dataset_id].analysis_history.append(analysis_record)
        self.datasets[dataset_id].modified_at = datetime.now().isoformat()
        self._save_registry()
        return True
    
    def get_dataset_statistics(self) -> Dict:
        """Get overall dataset statistics"""
        total_datasets = len(self.datasets)
        demo_count = len([ds for ds in self.datasets.values() if ds.type == 'demo'])
        user_count = len([ds for ds in self.datasets.values() if ds.type == 'user'])
        generated_count = len([ds for ds in self.datasets.values() if ds.type == 'generated'])
        
        total_size = sum(ds.size_mb for ds in self.datasets.values())
        
        status_counts = {}
        for ds in self.datasets.values():
            status_counts[ds.status] = status_counts.get(ds.status, 0) + 1
        
        return {
            'total_datasets': total_datasets,
            'demo_datasets': demo_count,
            'user_datasets': user_count,
            'generated_datasets': generated_count,
            'total_size_mb': total_size,
            'status_distribution': status_counts,
            'last_updated': datetime.now().isoformat()
        }
    
    def export_dataset_info(self, dataset_id: str, format: str = 'json') -> Optional[str]:
        """Export dataset information"""
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            return None
        
        export_data = asdict(dataset)
        
        if format == 'json':
            return json.dumps(export_data, ensure_ascii=False, indent=2)
        elif format == 'csv':
            # Flatten the data for CSV
            flat_data = {}
            for key, value in export_data.items():
                if isinstance(value, (dict, list)):
                    flat_data[key] = json.dumps(value)
                else:
                    flat_data[key] = value
            
            df = pd.DataFrame([flat_data])
            return df.to_csv(index=False)
        
        return None
    
    def search_datasets(self, query: str) -> List[DatasetInfo]:
        """Search datasets by name, description, or tags"""
        query = query.lower()
        results = []
        
        for dataset in self.datasets.values():
            if (query in dataset.name.lower() or 
                query in dataset.description.lower() or
                any(query in tag.lower() for tag in dataset.tags)):
                results.append(dataset)
        
        return results
    
    def duplicate_dataset(self, dataset_id: str, new_name: str) -> Optional[str]:
        """Create a copy of an existing dataset"""
        source_dataset = self.get_dataset(dataset_id)
        if not source_dataset:
            return None
        
        # Create new dataset ID
        new_id = self._generate_dataset_id(new_name)
        
        # Copy dataset info
        new_dataset = DatasetInfo(
            id=new_id,
            name=new_name,
            type='user',  # Duplicated datasets are always user type
            status='active',
            created_at=datetime.now().isoformat(),
            modified_at=datetime.now().isoformat(),
            size_mb=source_dataset.size_mb,
            samples=source_dataset.samples,
            genes=source_dataset.genes,
            features=source_dataset.features.copy(),
            metadata=source_dataset.metadata.copy(),
            analysis_history=[],  # Start with empty history
            tags=source_dataset.tags.copy() + ['duplicated'],
            description=f"Duplicated from {source_dataset.name}",
            location=source_dataset.location  # Initially same location
        )
        
        self.datasets[new_id] = new_dataset
        self._save_registry()
        
        return new_id

# Global dataset manager instance
dataset_manager = DatasetManager()