"""
Dynamic Data Loader for Dataset Switching
动态数据加载器 - 支持数据集切换
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
import json

class DataLoader:
    """Load data dynamically based on selected dataset"""
    
    def __init__(self):
        self.cache = {}  # Cache loaded data
        self.current_dataset_id = None
    
    def load_dataset(self, dataset_id: str, dataset_info: Dict) -> Dict:
        """Load dataset based on dataset ID and info"""
        
        # Check cache first
        if dataset_id in self.cache:
            return self.cache[dataset_id]
        
        data = {}
        
        if dataset_info['type'] == 'demo':
            # Load demo data based on dataset ID
            if dataset_id in ['demo_early_stage', 'demo_advanced_stage', 'demo_mixed_cohort']:
                data = self._load_new_demo_data(dataset_id, dataset_info)
            else:
                # Load original demo data
                data = self._load_demo_data()
        else:
            # Load user data
            data_path = Path(dataset_info.get('data_path', f'data/user_uploads/{dataset_info.get("session_id", dataset_id)}'))
            data = self._load_user_data(data_path)
        
        # Cache the data
        self.cache[dataset_id] = data
        self.current_dataset_id = dataset_id
        
        return data
    
    def _load_demo_data(self) -> Dict:
        """Load demo dataset"""
        # Generate demo data
        np.random.seed(42)
        
        # Clinical data
        n_samples = 200
        clinical_data = pd.DataFrame({
            'sample_id': [f'TCGA-{i:03d}' for i in range(n_samples)],
            'age': np.random.normal(60, 10, n_samples).astype(int),
            'gender': np.random.choice(['M', 'F'], n_samples),
            'stage': np.random.choice(['I', 'II', 'III', 'IV'], n_samples, p=[0.2, 0.3, 0.3, 0.2]),
            'os_time': np.random.exponential(500, n_samples),
            'os_status': np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
        })
        
        # Expression data
        n_genes = 500
        genes = [f'Gene_{i}' for i in range(n_genes)]
        expression_data = pd.DataFrame(
            np.random.randn(n_genes, n_samples) * 2 + 10,
            index=genes,
            columns=clinical_data['sample_id']
        )
        
        # Add some patterns
        # High expression in late stage
        late_stage = clinical_data[clinical_data['stage'].isin(['III', 'IV'])]['sample_id']
        expression_data.loc['Gene_1':'Gene_10', late_stage] += 2
        
        # Low expression in early stage
        early_stage = clinical_data[clinical_data['stage'].isin(['I', 'II'])]['sample_id']
        expression_data.loc['Gene_11':'Gene_20', early_stage] -= 2
        
        # Mutation data
        mutation_data = pd.DataFrame({
            'sample_id': np.random.choice(clinical_data['sample_id'], 1000),
            'gene': np.random.choice(genes[:100], 1000),
            'variant_type': np.random.choice(['SNV', 'INS', 'DEL'], 1000, p=[0.7, 0.15, 0.15]),
            'effect': np.random.choice(['missense', 'nonsense', 'silent', 'frameshift'], 1000, 
                                     p=[0.5, 0.2, 0.2, 0.1])
        })
        
        # CNV data (Copy Number Variation)
        cnv_data = pd.DataFrame(
            np.random.choice([-2, -1, 0, 1, 2], size=(n_genes, n_samples), p=[0.1, 0.2, 0.4, 0.2, 0.1]),
            index=genes,
            columns=clinical_data['sample_id']
        )
        
        # Methylation data (beta values)
        methylation_data = pd.DataFrame(
            np.random.beta(2, 2, size=(n_genes, n_samples)),
            index=genes,
            columns=clinical_data['sample_id']
        )
        
        return {
            'clinical_data': clinical_data,
            'expression_data': expression_data,
            'mutations': mutation_data,
            'cnv': cnv_data,
            'methylation': methylation_data,
            'dataset_info': {
                'name': 'TCGA-LIHC Demo',
                'samples': n_samples,
                'genes': n_genes,
                'type': 'demo'
            }
        }
    
    def _load_new_demo_data(self, dataset_id: str, dataset_info: Dict) -> Dict:
        """Load new demo datasets (early stage, advanced stage, mixed cohort)"""
        try:
            # Get data path from dataset info
            data_path = Path(dataset_info.get('data_path', f'data/demo_datasets/{dataset_id}'))
            
            if not data_path.exists():
                # Fallback to original demo data if path doesn't exist
                return self._load_demo_data()
            
            data = {}
            
            # Load clinical data
            clinical_file = data_path / "clinical_data.csv"
            if clinical_file.exists():
                data['clinical_data'] = pd.read_csv(clinical_file)
            
            # Load expression data  
            expression_file = data_path / "expression_data.csv"
            if expression_file.exists():
                data['expression_data'] = pd.read_csv(expression_file, index_col=0)
            
            # Load mutation data
            mutation_file = data_path / "mutation_data.csv"
            if mutation_file.exists():
                mutation_df = pd.read_csv(mutation_file, index_col=0)
                # Convert to long format for compatibility
                mutations = []
                for sample in mutation_df.index:
                    for gene in mutation_df.columns:
                        if mutation_df.loc[sample, gene] == 1:
                            mutations.append({
                                'sample_id': sample,
                                'gene': gene,
                                'variant_type': 'SNV',
                                'effect': 'missense'
                            })
                data['mutations'] = pd.DataFrame(mutations) if mutations else pd.DataFrame()
            
            # Load metadata
            metadata_file = data_path / "metadata.json"
            dataset_name = dataset_info.get('name', dataset_id)
            n_samples = len(data.get('clinical_data', []))
            n_genes = len(data.get('expression_data', []))
            
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    dataset_name = metadata.get('name', dataset_name)
                    n_samples = metadata.get('statistics', {}).get('n_samples', n_samples)
                    n_genes = metadata.get('statistics', {}).get('n_genes', n_genes)
            
            # Add dataset info
            data['dataset_info'] = {
                'name': dataset_name,
                'samples': n_samples,
                'genes': n_genes,
                'type': 'demo',
                'dataset_id': dataset_id
            }
            
            # Generate missing data types if needed
            if 'clinical_data' in data and 'expression_data' in data:
                n_samples = len(data['clinical_data'])
                n_genes = len(data['expression_data'])
                
                # Generate CNV data if missing
                if 'cnv' not in data:
                    data['cnv'] = pd.DataFrame(
                        np.random.choice([-1, 0, 1], size=(n_genes, n_samples), p=[0.2, 0.6, 0.2]),
                        index=data['expression_data'].index,
                        columns=data['clinical_data']['Patient_ID']
                    )
                
                # Generate methylation data if missing
                if 'methylation' not in data:
                    data['methylation'] = pd.DataFrame(
                        np.random.beta(2, 2, size=(n_genes, n_samples)),
                        index=data['expression_data'].index,
                        columns=data['clinical_data']['Patient_ID']
                    )
            
            return data
            
        except Exception as e:
            print(f"Error loading new demo data for {dataset_id}: {str(e)}")
            # Fallback to original demo data
            return self._load_demo_data()
    
    def _load_user_data(self, data_path: Path) -> Dict:
        """Load user uploaded data"""
        data = {}
        
        # Load clinical data
        clinical_file = data_path / "clinical_data.csv"
        if clinical_file.exists():
            data['clinical_data'] = pd.read_csv(clinical_file)
            if 'sample_id' not in data['clinical_data'].columns:
                data['clinical_data']['sample_id'] = data['clinical_data'].index.astype(str)
        
        # Load expression data
        expression_file = data_path / "expression_data.csv"
        if expression_file.exists():
            data['expression_data'] = pd.read_csv(expression_file, index_col=0)
        
        # Load mutation data
        mutation_file = data_path / "mutation_data.csv"
        if mutation_file.exists():
            data['mutations'] = pd.read_csv(mutation_file)
        
        # Dataset info
        data['dataset_info'] = {
            'name': 'User Dataset',
            'samples': len(data.get('clinical_data', [])),
            'genes': len(data.get('expression_data', [])),
            'type': 'user'
        }
        
        return data
    
    def get_summary_statistics(self, dataset_id: str, dataset_info: Dict) -> Dict:
        """Get summary statistics for a dataset"""
        data = self.load_dataset(dataset_id, dataset_info)
        
        stats = {
            'samples': 0,
            'genes': 0,
            'mutations': 0,
            'survival_rate': 0,
            'median_age': 0,
            'stage_distribution': {}
        }
        
        if 'clinical_data' in data and not data['clinical_data'].empty:
            stats['samples'] = len(data['clinical_data'])
            if 'age' in data['clinical_data'].columns:
                stats['median_age'] = data['clinical_data']['age'].median()
            if 'os_status' in data['clinical_data'].columns:
                stats['survival_rate'] = 1 - data['clinical_data']['os_status'].mean()
            if 'stage' in data['clinical_data'].columns:
                stats['stage_distribution'] = data['clinical_data']['stage'].value_counts().to_dict()
        
        if 'expression_data' in data and not data['expression_data'].empty:
            stats['genes'] = len(data['expression_data'])
        
        if 'mutations' in data and not data['mutations'].empty:
            stats['mutations'] = len(data['mutations'])
        
        return stats
    
    def get_top_genes(self, dataset_id: str, dataset_info: Dict, n: int = 20) -> pd.DataFrame:
        """Get top variable genes"""
        data = self.load_dataset(dataset_id, dataset_info)
        
        if 'expression_data' not in data or data['expression_data'].empty:
            return pd.DataFrame()
        
        gene_variance = data['expression_data'].var(axis=1)
        top_genes = gene_variance.nlargest(n)
        
        return pd.DataFrame({
            'gene': top_genes.index,
            'variance': top_genes.values,
            'mean_expression': data['expression_data'].loc[top_genes.index].mean(axis=1).values
        })
    
    def get_survival_data(self, dataset_id: str, dataset_info: Dict) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        """Get survival data for analysis"""
        data = self.load_dataset(dataset_id, dataset_info)
        
        clinical = data.get('clinical_data', pd.DataFrame())
        expression = data.get('expression_data', None)
        
        # Ensure required columns
        if not clinical.empty and 'os_time' in clinical.columns and 'os_status' in clinical.columns:
            return clinical, expression
        
        return pd.DataFrame(), None
    
    def clear_cache(self, dataset_id: str = None):
        """Clear data cache"""
        if dataset_id:
            self.cache.pop(dataset_id, None)
        else:
            self.cache.clear()


# Global instance
data_loader = DataLoader()


def create_dataset_specific_content(dataset_id: str, dataset_info: Dict, 
                                  content_type: str) -> Dict:
    """Create content specific to selected dataset"""
    
    if content_type == 'overview':
        # Get summary statistics
        stats = data_loader.get_summary_statistics(dataset_id, dataset_info)
        
        return {
            'stats': stats,
            'top_genes': data_loader.get_top_genes(dataset_id, dataset_info, 10).to_dict('records')
        }
    
    elif content_type == 'expression_heatmap':
        # Get expression data for heatmap
        data = data_loader.load_dataset(dataset_id, dataset_info)
        if 'expression_data' not in data:
            return {'error': 'No expression data available'}
        
        # Get top variable genes
        top_genes = data_loader.get_top_genes(dataset_id, dataset_info, 50)
        expr_subset = data['expression_data'].loc[top_genes['gene']]
        
        return {
            'expression_matrix': expr_subset.values.tolist(),
            'genes': expr_subset.index.tolist(),
            'samples': expr_subset.columns.tolist()
        }
    
    elif content_type == 'survival_analysis':
        # Get survival data
        clinical, expression = data_loader.get_survival_data(dataset_id, dataset_info)
        
        if clinical.empty:
            return {'error': 'No survival data available'}
        
        return {
            'clinical': clinical.to_dict('records'),
            'has_expression': expression is not None
        }
    
    elif content_type == 'mutation_summary':
        # Get mutation data
        data = data_loader.load_dataset(dataset_id, dataset_info)
        
        if 'mutations' not in data or data['mutations'].empty:
            return {'error': 'No mutation data available'}
        
        # Summarize mutations
        mut_summary = data['mutations'].groupby('gene').size().sort_values(ascending=False).head(20)
        
        return {
            'top_mutated_genes': [
                {'gene': gene, 'count': int(count)}
                for gene, count in mut_summary.items()
            ],
            'total_mutations': len(data['mutations'])
        }
    
    return {}