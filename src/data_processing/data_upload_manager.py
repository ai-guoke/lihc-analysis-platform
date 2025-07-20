"""
Data Upload Management System
Handles user data uploads for LIHC multi-dimensional analysis
"""

import pandas as pd
import numpy as np
import os
import zipfile
import tempfile
from pathlib import Path
import json
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class DataUploadManager:
    """Manage user data uploads and validation"""
    
    def __init__(self, upload_dir="data/user_uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Define required data types and their specifications
        self.required_data_types = {
            'clinical': {
                'filename_pattern': '*clinical*',
                'required_columns': ['sample_id', 'os_time', 'os_status'],
                'optional_columns': ['age', 'gender', 'stage', 'grade'],
                'description': 'Clinical and survival data'
            },
            'expression': {
                'filename_pattern': '*expression*',
                'required_format': 'genes_as_rows_samples_as_columns',
                'description': 'Gene expression matrix (genes × samples)'
            },
            'mutation': {
                'filename_pattern': '*mutation*',
                'required_columns': ['sample_id', 'gene', 'mutation_type'],
                'optional_columns': ['variant_class', 'protein_change'],
                'description': 'Mutation data'
            }
        }
    
    def validate_file_format(self, file_path: Path, data_type: str) -> Dict:
        """Validate uploaded file format and content"""
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'info': {}
        }
        
        try:
            # Check file extension
            if file_path.suffix.lower() not in ['.csv', '.tsv', '.txt', '.xlsx']:
                result['errors'].append(f"Unsupported file format: {file_path.suffix}")
                return result
            
            # Read file
            if file_path.suffix.lower() == '.xlsx':
                df = pd.read_excel(file_path, index_col=0 if data_type == 'expression' else None)
            else:
                separator = '\t' if file_path.suffix.lower() in ['.tsv', '.txt'] else ','
                df = pd.read_csv(file_path, sep=separator, index_col=0 if data_type == 'expression' else None)
            
            result['info']['shape'] = df.shape
            result['info']['columns'] = list(df.columns)[:10]  # First 10 columns
            
            # Validate based on data type
            if data_type == 'clinical':
                result = self._validate_clinical_data(df, result)
            elif data_type == 'expression':
                result = self._validate_expression_data(df, result)
            elif data_type == 'mutation':
                result = self._validate_mutation_data(df, result)
            
            if len(result['errors']) == 0:
                result['valid'] = True
                result['info']['preview'] = df.head(3).to_dict()
                
        except Exception as e:
            result['errors'].append(f"Error reading file: {str(e)}")
        
        return result
    
    def _validate_clinical_data(self, df: pd.DataFrame, result: Dict) -> Dict:
        """Validate clinical data"""
        required_cols = self.required_data_types['clinical']['required_columns']
        
        # Check required columns
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            result['errors'].append(f"Missing required columns: {missing_cols}")
        
        # Check data types and ranges
        if 'os_time' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['os_time']):
                result['errors'].append("os_time must be numeric (days)")
            elif df['os_time'].min() < 0:
                result['warnings'].append("Negative survival times detected")
        
        if 'os_status' in df.columns:
            unique_status = df['os_status'].unique()
            if not all(status in [0, 1, '0', '1'] for status in unique_status):
                result['errors'].append("os_status must be 0 (alive) or 1 (dead)")
        
        # Check for duplicates
        if 'sample_id' in df.columns:
            duplicates = df['sample_id'].duplicated().sum()
            if duplicates > 0:
                result['warnings'].append(f"{duplicates} duplicate sample IDs found")
        
        result['info']['n_samples'] = len(df)
        result['info']['n_events'] = df['os_status'].sum() if 'os_status' in df.columns else 'Unknown'
        
        return result
    
    def _validate_expression_data(self, df: pd.DataFrame, result: Dict) -> Dict:
        """Validate gene expression data"""
        # Check if genes are rows and samples are columns
        if df.shape[0] > df.shape[1]:
            result['info']['format'] = 'genes_as_rows (correct)'
        else:
            result['warnings'].append("Data might have samples as rows - please verify format")
        
        # Check for missing values
        missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        if missing_pct > 10:
            result['warnings'].append(f"High percentage of missing values: {missing_pct:.1f}%")
        
        # Check value ranges (should be positive for expression data)
        if df.min().min() < 0:
            result['warnings'].append("Negative expression values detected")
        
        # Check if data looks log-transformed
        max_val = df.max().max()
        if max_val > 20:
            result['warnings'].append("Expression values seem high - consider log transformation")
        
        result['info']['n_genes'] = df.shape[0]
        result['info']['n_samples'] = df.shape[1]
        result['info']['value_range'] = f"{df.min().min():.2f} - {df.max().max():.2f}"
        
        return result
    
    def _validate_mutation_data(self, df: pd.DataFrame, result: Dict) -> Dict:
        """Validate mutation data"""
        required_cols = self.required_data_types['mutation']['required_columns']
        
        # Check required columns
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            result['errors'].append(f"Missing required columns: {missing_cols}")
        
        # Check mutation types
        if 'mutation_type' in df.columns:
            valid_types = ['Missense', 'Nonsense', 'Frame_Shift', 'Splice_Site', 'Silent', 'In_Frame']
            invalid_types = df[~df['mutation_type'].isin(valid_types)]['mutation_type'].unique()
            if len(invalid_types) > 0:
                result['warnings'].append(f"Unknown mutation types: {list(invalid_types)[:5]}")
        
        result['info']['n_mutations'] = len(df)
        result['info']['n_unique_genes'] = df['gene'].nunique() if 'gene' in df.columns else 'Unknown'
        result['info']['n_unique_samples'] = df['sample_id'].nunique() if 'sample_id' in df.columns else 'Unknown'
        
        return result
    
    def process_upload_package(self, package_path: Path, user_id: str) -> Dict:
        """Process a complete data upload package (ZIP file or directory)"""
        result = {
            'success': False,
            'user_session_id': user_id,
            'files_processed': {},
            'errors': [],
            'warnings': [],
            'next_steps': []
        }
        
        try:
            # Create user-specific directory
            user_dir = self.upload_dir / user_id
            user_dir.mkdir(exist_ok=True)
            
            # Extract if ZIP file
            if package_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(package_path, 'r') as zip_ref:
                    zip_ref.extractall(user_dir)
                file_list = list(user_dir.rglob('*'))
            else:
                file_list = [package_path]
            
            # Process each file
            for file_path in file_list:
                if file_path.is_file() and file_path.suffix.lower() in ['.csv', '.tsv', '.txt', '.xlsx']:
                    data_type = self._identify_data_type(file_path)
                    if data_type:
                        validation_result = self.validate_file_format(file_path, data_type)
                        result['files_processed'][str(file_path.name)] = {
                            'data_type': data_type,
                            'validation': validation_result
                        }
                        
                        if validation_result['valid']:
                            # Copy to standardized location
                            standard_name = f"{data_type}_data.csv"
                            standard_path = user_dir / standard_name
                            
                            # Convert to standard CSV format
                            if file_path.suffix.lower() == '.xlsx':
                                df = pd.read_excel(file_path, index_col=0 if data_type == 'expression' else None)
                            else:
                                separator = '\t' if file_path.suffix.lower() in ['.tsv', '.txt'] else ','
                                df = pd.read_csv(file_path, sep=separator, index_col=0 if data_type == 'expression' else None)
                            
                            df.to_csv(standard_path)
                            result['files_processed'][str(file_path.name)]['standard_path'] = str(standard_path)
            
            # Check completeness
            required_types = ['clinical', 'expression']  # Minimum required
            available_types = [info['data_type'] for info in result['files_processed'].values() 
                             if info['validation']['valid']]
            
            missing_types = [t for t in required_types if t not in available_types]
            if missing_types:
                result['errors'].append(f"Missing required data types: {missing_types}")
            else:
                result['success'] = True
                result['next_steps'].append("Data validation completed successfully")
                result['next_steps'].append("Ready to run multi-dimensional analysis")
                
                # Generate analysis configuration
                self._generate_analysis_config(user_dir, available_types)
        
        except Exception as e:
            result['errors'].append(f"Error processing upload package: {str(e)}")
        
        return result
    
    def _identify_data_type(self, file_path: Path) -> Optional[str]:
        """Identify data type based on filename"""
        filename_lower = file_path.name.lower()
        
        if any(keyword in filename_lower for keyword in ['clinical', 'survival', 'patient']):
            return 'clinical'
        elif any(keyword in filename_lower for keyword in ['expression', 'rnaseq', 'fpkm', 'tpm']):
            return 'expression'
        elif any(keyword in filename_lower for keyword in ['mutation', 'variant', 'snv']):
            return 'mutation'
        
        return None
    
    def _generate_analysis_config(self, user_dir: Path, available_types: List[str]):
        """Generate analysis configuration for user data"""
        config = {
            'user_data_path': str(user_dir),
            'available_data_types': available_types,
            'analysis_timestamp': pd.Timestamp.now().isoformat(),
            'data_sources': {
                data_type: str(user_dir / f"{data_type}_data.csv")
                for data_type in available_types
            }
        }
        
        config_path = user_dir / "analysis_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_upload_template(self) -> Dict:
        """Generate template files and instructions for users"""
        templates = {}
        
        # Clinical data template
        clinical_template = pd.DataFrame({
            'sample_id': [f'SAMPLE_{i:03d}' for i in range(1, 6)],
            'age': [65, 58, 72, 45, 69],
            'gender': ['Male', 'Female', 'Male', 'Female', 'Male'],
            'stage': ['Stage I', 'Stage II', 'Stage III', 'Stage I', 'Stage II'],
            'grade': ['G2', 'G3', 'G2', 'G1', 'G3'],
            'os_time': [1825, 945, 365, 2190, 1460],  # Days
            'os_status': [0, 1, 1, 0, 0]  # 0=alive, 1=dead
        })
        
        # Expression data template (genes as rows, samples as columns)
        expression_template = pd.DataFrame(
            np.random.lognormal(mean=2, sigma=1, size=(10, 5)),
            index=[f'GENE_{i}' for i in range(1, 11)],
            columns=[f'SAMPLE_{i:03d}' for i in range(1, 6)]
        )
        
        # Mutation data template
        mutation_template = pd.DataFrame({
            'sample_id': ['SAMPLE_001', 'SAMPLE_002', 'SAMPLE_003', 'SAMPLE_001', 'SAMPLE_004'],
            'gene': ['TP53', 'CTNNB1', 'KRAS', 'PIK3CA', 'EGFR'],
            'mutation_type': ['Missense', 'Nonsense', 'Missense', 'Missense', 'Frame_Shift'],
            'variant_class': ['SNP', 'SNP', 'SNP', 'SNP', 'INDEL']
        })
        
        return {
            'clinical': clinical_template,
            'expression': expression_template,
            'mutation': mutation_template,
            'instructions': {
                'clinical': "Required: sample_id, os_time (days), os_status (0/1). Optional: age, gender, stage, grade",
                'expression': "Genes as rows, samples as columns. Values should be normalized (log2-transformed recommended)",
                'mutation': "Required: sample_id, gene, mutation_type. One row per mutation event"
            }
        }

class UserDataAnalyzer:
    """Analyze user-uploaded data using the LIHC pipeline"""
    
    def __init__(self, user_session_id: str):
        self.user_session_id = user_session_id
        self.user_data_dir = Path("data/user_uploads") / user_session_id
        
    def run_analysis_pipeline(self, stages: List[str] = None) -> Dict:
        """Run the analysis pipeline on user data"""
        if stages is None:
            stages = ['stage1', 'stage2', 'stage3']
        
        results = {}
        
        try:
            # Load analysis configuration
            config_path = self.user_data_dir / "analysis_config.json"
            if not config_path.exists():
                raise Exception("Analysis configuration not found. Please upload data first.")
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Adapt the existing pipeline to use user data
            from analysis.stage1_multidimensional import MultiDimensionalAnalysis
            from analysis.stage2_network import CrossDimensionalNetwork
            from analysis.stage3_linchpin import LinchpinIdentifier
            
            # Create user-specific results directory
            user_results_dir = Path("results") / "user_analyses" / self.user_session_id
            user_results_dir.mkdir(parents=True, exist_ok=True)
            
            if 'stage1' in stages:
                analyzer = MultiDimensionalAnalysis()
                # Override data paths to use user data
                analyzer.data_dir = self.user_data_dir
                results['stage1'] = analyzer.run_all_analyses()
            
            if 'stage2' in stages and 'stage1' in results:
                network_analyzer = CrossDimensionalNetwork(results.get('stage1'))
                results['stage2'] = network_analyzer.run_all_analyses()
            
            if 'stage3' in stages and 'stage2' in results:
                linchpin_analyzer = LinchpinIdentifier(results.get('stage2'))
                results['stage3'] = linchpin_analyzer.run_linchpin_analysis()
            
            # Save user-specific results
            self._save_user_results(results, user_results_dir)
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _save_user_results(self, results: Dict, output_dir: Path):
        """Save analysis results to user-specific directory"""
        summary = {
            'user_session_id': self.user_session_id,
            'analysis_timestamp': pd.Timestamp.now().isoformat(),
            'stages_completed': list(results.keys()),
            'results_location': str(output_dir)
        }
        
        # Save summary
        with open(output_dir / "analysis_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

if __name__ == "__main__":
    # Example usage
    uploader = DataUploadManager()
    templates = uploader.get_upload_template()
    
    # Save templates for users to download
    template_dir = Path("data/templates")
    template_dir.mkdir(exist_ok=True)
    
    for data_type, template_df in templates.items():
        if data_type != 'instructions':
            template_df.to_csv(template_dir / f"{data_type}_template.csv")
    
    print("Upload system initialized and templates created!")