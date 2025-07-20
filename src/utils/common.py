"""
Shared utilities for the LIHC analysis system
Common functions and classes used across modules
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import warnings
warnings.filterwarnings('ignore')

class PathManager:
    """Centralized path management for the LIHC system"""
    
    def __init__(self, base_dir: Union[str, Path] = "."):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "data"
        self.results_dir = self.base_dir / "results"
        self.config_dir = self.base_dir / "config"
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            self.data_dir / "raw",
            self.data_dir / "processed", 
            self.data_dir / "user_uploads",
            self.data_dir / "external",
            self.data_dir / "templates",
            self.results_dir / "tables",
            self.results_dir / "networks",
            self.results_dir / "linchpins",
            self.results_dir / "figures",
            self.results_dir / "user_analyses"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_data_path(self, data_type: str, filename: str = None) -> Path:
        """Get path for data files"""
        type_mapping = {
            'raw': self.data_dir / "raw",
            'processed': self.data_dir / "processed",
            'external': self.data_dir / "external",
            'templates': self.data_dir / "templates",
            'user_uploads': self.data_dir / "user_uploads"
        }
        
        base_path = type_mapping.get(data_type, self.data_dir / data_type)
        return base_path / filename if filename else base_path
    
    def get_results_path(self, result_type: str, filename: str = None) -> Path:
        """Get path for results files"""
        type_mapping = {
            'tables': self.results_dir / "tables",
            'networks': self.results_dir / "networks", 
            'linchpins': self.results_dir / "linchpins",
            'figures': self.results_dir / "figures",
            'user_analyses': self.results_dir / "user_analyses"
        }
        
        base_path = type_mapping.get(result_type, self.results_dir / result_type)
        return base_path / filename if filename else base_path
    
    def get_config_path(self, filename: str = None) -> Path:
        """Get path for config files"""
        return self.config_dir / filename if filename else self.config_dir

class DataValidator:
    """Common data validation utilities"""
    
    @staticmethod
    def validate_clinical_data(df: pd.DataFrame) -> Dict:
        """Validate clinical data format"""
        errors = []
        warnings = []
        info = {}
        
        # Required columns
        required_cols = ['sample_id', 'os_time', 'os_status']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
        
        # Data type validation
        if 'os_time' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['os_time']):
                errors.append("os_time must be numeric")
            elif df['os_time'].min() < 0:
                warnings.append("Negative survival times detected")
        
        if 'os_status' in df.columns:
            unique_status = df['os_status'].unique()
            if not set(unique_status).issubset({0, 1}):
                errors.append("os_status must contain only 0 and 1")
        
        # Sample size check
        if len(df) < 10:
            warnings.append(f"Small sample size: {len(df)} samples")
        
        info['n_samples'] = len(df)
        info['shape'] = df.shape
        info['columns'] = list(df.columns)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'info': info
        }
    
    @staticmethod
    def validate_expression_data(df: pd.DataFrame) -> Dict:
        """Validate expression data format"""
        errors = []
        warnings = []
        info = {}
        
        # Check if genes are in rows or columns
        if df.shape[0] > df.shape[1]:
            # Likely genes as rows, samples as columns
            genes_axis, samples_axis = 0, 1
        else:
            # Likely samples as rows, genes as columns
            genes_axis, samples_axis = 1, 0
            warnings.append("Expression data appears to have samples as rows - consider transposing")
        
        # Check for numeric data
        numeric_cols = df.select_dtypes(include=[np.number]).shape[1]
        if numeric_cols < df.shape[1] * 0.8:
            errors.append("Expression data should be primarily numeric")
        
        # Check for missing values
        missing_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100
        if missing_pct > 10:
            warnings.append(f"High missing data: {missing_pct:.1f}%")
        
        # Check value range
        if df.select_dtypes(include=[np.number]).min().min() < 0 and df.select_dtypes(include=[np.number]).max().max() > 30:
            warnings.append("Expression values have wide range - consider log transformation")
        
        info['n_genes'] = df.shape[genes_axis]
        info['n_samples'] = df.shape[samples_axis]
        info['shape'] = df.shape
        info['missing_pct'] = missing_pct
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'info': info
        }
    
    @staticmethod
    def validate_mutation_data(df: pd.DataFrame) -> Dict:
        """Validate mutation data format"""
        errors = []
        warnings = []
        info = {}
        
        # Required columns
        required_cols = ['sample_id', 'gene']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
        
        # Check for reasonable mutation types
        if 'mutation_type' in df.columns:
            mutation_types = df['mutation_type'].unique()
            expected_types = ['Missense_Mutation', 'Nonsense_Mutation', 'Frame_Shift_Del', 
                            'Frame_Shift_Ins', 'Splice_Site', 'Silent']
            unexpected_types = [mt for mt in mutation_types if mt not in expected_types]
            if unexpected_types:
                warnings.append(f"Unexpected mutation types: {unexpected_types}")
        
        # Sample and gene counts
        if 'sample_id' in df.columns:
            n_samples = df['sample_id'].nunique()
            info['n_samples'] = n_samples
        
        if 'gene' in df.columns:
            n_genes = df['gene'].nunique()
            info['n_genes'] = n_genes
            
            # Check for common cancer genes
            common_cancer_genes = ['TP53', 'KRAS', 'PIK3CA', 'APC', 'PTEN']
            found_cancer_genes = [g for g in common_cancer_genes if g in df['gene'].values]
            info['common_cancer_genes_found'] = found_cancer_genes
        
        info['n_mutations'] = len(df)
        info['shape'] = df.shape
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'info': info
        }

class ResultsLoader:
    """Utility class for loading analysis results"""
    
    def __init__(self, results_dir: Union[str, Path] = "results"):
        self.path_manager = PathManager()
        self.results_dir = Path(results_dir)
    
    def load_stage1_results(self) -> Dict[str, pd.DataFrame]:
        """Load Stage 1 analysis results"""
        results = {}
        dimensions = ['tumor_cells', 'immune_cells', 'stromal_cells', 'ecm', 'cytokines']
        
        for dimension in dimensions:
            file_path = self.path_manager.get_results_path('tables', f'stage1_{dimension}_results.csv')
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    results[dimension] = df
                except Exception as e:
                    print(f"Warning: Could not load {dimension} results: {e}")
        
        return results
    
    def load_stage2_results(self) -> Dict[str, pd.DataFrame]:
        """Load Stage 2 network analysis results"""
        results = {}
        
        files = {
            'centrality': 'network_centrality.csv',
            'correlation_matrix': 'correlation_matrix.csv',
            'cross_connections': 'cross_dimensional_connections.csv'
        }
        
        for key, filename in files.items():
            file_path = self.path_manager.get_results_path('networks', filename)
            if file_path.exists():
                try:
                    if key == 'correlation_matrix':
                        df = pd.read_csv(file_path, index_col=0)
                    else:
                        df = pd.read_csv(file_path)
                    results[key] = df
                except Exception as e:
                    print(f"Warning: Could not load {key}: {e}")
        
        return results
    
    def load_stage3_results(self) -> Dict[str, Union[pd.DataFrame, Dict]]:
        """Load Stage 3 linchpin analysis results"""
        results = {}
        
        # Load linchpin scores
        linchpin_file = self.path_manager.get_results_path('linchpins', 'linchpin_scores.csv')
        if linchpin_file.exists():
            try:
                results['linchpin_scores'] = pd.read_csv(linchpin_file)
            except Exception as e:
                print(f"Warning: Could not load linchpin scores: {e}")
        
        # Load druggability assessment
        drug_file = self.path_manager.get_results_path('linchpins', 'druggability_assessment.csv')
        if drug_file.exists():
            try:
                results['druggability'] = pd.read_csv(drug_file)
            except Exception as e:
                print(f"Warning: Could not load druggability assessment: {e}")
        
        # Load evidence cards
        evidence_file = self.path_manager.get_results_path('linchpins', 'evidence_cards.json')
        if evidence_file.exists():
            try:
                with open(evidence_file, 'r') as f:
                    results['evidence_cards'] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load evidence cards: {e}")
        
        return results
    
    def load_all_results(self) -> Dict:
        """Load all analysis results"""
        return {
            'stage1': self.load_stage1_results(),
            'stage2': self.load_stage2_results(),
            'stage3': self.load_stage3_results()
        }

class ExceptionHandler:
    """Centralized exception handling"""
    
    @staticmethod
    def handle_file_error(func):
        """Decorator for handling file-related errors"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                return {'error': f'File not found: {e}', 'type': 'FileNotFoundError'}
            except pd.errors.EmptyDataError as e:
                return {'error': f'Empty data file: {e}', 'type': 'EmptyDataError'}
            except pd.errors.ParserError as e:
                return {'error': f'File parsing error: {e}', 'type': 'ParserError'}
            except PermissionError as e:
                return {'error': f'Permission denied: {e}', 'type': 'PermissionError'}
            except Exception as e:
                return {'error': f'Unexpected error: {e}', 'type': 'UnexpectedError'}
        return wrapper
    
    @staticmethod
    def handle_analysis_error(func):
        """Decorator for handling analysis-related errors"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                return {'error': f'Invalid value: {e}', 'type': 'ValueError'}
            except KeyError as e:
                return {'error': f'Missing key: {e}', 'type': 'KeyError'}
            except AttributeError as e:
                return {'error': f'Attribute error: {e}', 'type': 'AttributeError'}
            except RuntimeError as e:
                return {'error': f'Runtime error: {e}', 'type': 'RuntimeError'}
            except Exception as e:
                return {'error': f'Analysis error: {e}', 'type': 'AnalysisError'}
        return wrapper

class ConfigManager:
    """Configuration management utility"""
    
    def __init__(self, config_path: Union[str, Path] = None):
        self.path_manager = PathManager()
        
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = self.path_manager.get_config_path('config.py')
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        config = {}
        
        if self.config_path.exists():
            try:
                # Read config file safely using JSON/YAML parsing instead of exec
                with open(self.config_path, 'r') as f:
                    content = f.read()
                
                # Safe config parsing - removed dangerous exec() function
                import json
                import yaml
                
                try:
                    # Try JSON first
                    if self.config_path.suffix.lower() == '.json':
                        config_data = json.loads(content)
                    elif self.config_path.suffix.lower() in ['.yml', '.yaml']:
                        config_data = yaml.safe_load(content)
                    else:
                        # For Python config files, use ast.literal_eval for simple literals only
                        import ast
                        # This only allows safe literals, not arbitrary code execution
                        config_data = ast.literal_eval(content.strip())
                except (json.JSONDecodeError, yaml.YAMLError, ValueError, SyntaxError):
                    print(f"Warning: Could not parse config file {self.config_path}. Using defaults.")
                    config_data = {}
                
                # Extract configuration variables from parsed data
                namespace = config_data if isinstance(config_data, dict) else {}
                config = {k: v for k, v in namespace.items() 
                         if k.isupper() and not k.startswith('_')}
                
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
                config = self.get_default_config()
        else:
            config = self.get_default_config()
        
        return config
    
    def get_default_config(self) -> Dict:
        """Get default configuration values"""
        return {
            'TCGA_PROJECT': 'TCGA-LIHC',
            'VALIDATION_DATASETS': ['ICGC-LIRI-JP', 'GSE14520'],
            'SURVIVAL_THRESHOLD_YEARS': 5,
            'P_VALUE_THRESHOLD': 0.05,
            'HR_THRESHOLD': 0.2,
            'CORRELATION_THRESHOLD': 0.4,
            'WGCNA_POWER': 6,
            'MIN_MODULE_SIZE': 30,
            'NETWORK_HUB_THRESHOLD': 0.8,
            'LINCHPIN_WEIGHTS': {
                'prognostic_score': 0.4,
                'network_hub_score': 0.3,
                'cross_domain_score': 0.2,
                'regulator_score': 0.1
            },
            'PLOT_STYLE': 'seaborn',
            'COLOR_PALETTE': 'Set2',
            'FIGURE_DPI': 300
        }
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def update(self, updates: Dict):
        """Update configuration values"""
        self.config.update(updates)

class DataGenerator:
    """Utility for generating synthetic demo data"""
    
    # Real LIHC-related genes and potential therapeutic targets
    REAL_LIHC_GENES = {
        # Tumor suppressor genes
        'TP53': {'type': 'tumor_suppressor', 'dimension': 'tumor_cells', 'druggable': True, 'drugs': ['APR-246', 'PRIMA-1'], 'class': 'p53 reactivator'},
        'RB1': {'type': 'tumor_suppressor', 'dimension': 'tumor_cells', 'druggable': False, 'drugs': [], 'class': 'Cell cycle regulator'},
        'PTEN': {'type': 'tumor_suppressor', 'dimension': 'tumor_cells', 'druggable': False, 'drugs': [], 'class': 'PI3K/AKT inhibitor'},
        
        # Oncogenes and kinases
        'MYC': {'type': 'oncogene', 'dimension': 'tumor_cells', 'druggable': True, 'drugs': ['Omomyc', '10058-F4'], 'class': 'Transcription factor'},
        'EGFR': {'type': 'receptor', 'dimension': 'tumor_cells', 'druggable': True, 'drugs': ['Erlotinib', 'Gefitinib', 'Cetuximab'], 'class': 'Kinase inhibitor'},
        'VEGFA': {'type': 'growth_factor', 'dimension': 'cytokines', 'druggable': True, 'drugs': ['Bevacizumab', 'Sorafenib'], 'class': 'VEGF inhibitor'},
        'PDGFRA': {'type': 'receptor', 'dimension': 'stromal_cells', 'druggable': True, 'drugs': ['Imatinib', 'Sunitinib'], 'class': 'Kinase inhibitor'},
        
        # Immune checkpoints
        'PD1': {'type': 'checkpoint', 'dimension': 'immune_cells', 'druggable': True, 'drugs': ['Pembrolizumab', 'Nivolumab'], 'class': 'Checkpoint inhibitor'},
        'PDCD1': {'type': 'checkpoint', 'dimension': 'immune_cells', 'druggable': True, 'drugs': ['Pembrolizumab', 'Nivolumab'], 'class': 'Checkpoint inhibitor'},
        'CD274': {'type': 'checkpoint', 'dimension': 'immune_cells', 'druggable': True, 'drugs': ['Atezolizumab', 'Durvalumab'], 'class': 'PD-L1 inhibitor'},
        'CTLA4': {'type': 'checkpoint', 'dimension': 'immune_cells', 'druggable': True, 'drugs': ['Ipilimumab'], 'class': 'Checkpoint inhibitor'},
        
        # Metabolic targets
        'IDH1': {'type': 'metabolic', 'dimension': 'tumor_cells', 'druggable': True, 'drugs': ['Ivosidenib'], 'class': 'IDH inhibitor'},
        'IDH2': {'type': 'metabolic', 'dimension': 'tumor_cells', 'druggable': True, 'drugs': ['Enasidenib'], 'class': 'IDH inhibitor'},
        
        # Angiogenesis
        'VEGFR2': {'type': 'receptor', 'dimension': 'cytokines', 'druggable': True, 'drugs': ['Sunitinib', 'Sorafenib', 'Regorafenib'], 'class': 'VEGFR inhibitor'},
        'FGF2': {'type': 'growth_factor', 'dimension': 'cytokines', 'druggable': True, 'drugs': ['AZD4547'], 'class': 'FGFR inhibitor'},
        
        # DNA repair
        'BRCA1': {'type': 'dna_repair', 'dimension': 'tumor_cells', 'druggable': True, 'drugs': ['Olaparib', 'Rucaparib'], 'class': 'PARP inhibitor'},
        'BRCA2': {'type': 'dna_repair', 'dimension': 'tumor_cells', 'druggable': True, 'drugs': ['Olaparib', 'Rucaparib'], 'class': 'PARP inhibitor'},
        
        # Liver-specific targets
        'AFP': {'type': 'biomarker', 'dimension': 'tumor_cells', 'druggable': False, 'drugs': [], 'class': 'Diagnostic marker'},
        'GPC3': {'type': 'surface_protein', 'dimension': 'tumor_cells', 'druggable': True, 'drugs': ['Codrituzumab'], 'class': 'Antibody therapy'},
        'ALB': {'type': 'liver_function', 'dimension': 'tumor_cells', 'druggable': False, 'drugs': [], 'class': 'Prognostic marker'},
        
        # Immune infiltration markers
        'CD8A': {'type': 'immune_marker', 'dimension': 'immune_cells', 'druggable': False, 'drugs': [], 'class': 'T cell marker'},
        'FOXP3': {'type': 'immune_marker', 'dimension': 'immune_cells', 'druggable': True, 'drugs': ['Lenalidomide'], 'class': 'Treg modulator'},
        'IL6': {'type': 'cytokine', 'dimension': 'cytokines', 'druggable': True, 'drugs': ['Tocilizumab', 'Siltuximab'], 'class': 'IL-6 inhibitor'},
        'TNF': {'type': 'cytokine', 'dimension': 'cytokines', 'druggable': True, 'drugs': ['Adalimumab', 'Infliximab'], 'class': 'TNF inhibitor'},
        
        # ECM and stromal
        'COL1A1': {'type': 'ecm_protein', 'dimension': 'ecm', 'druggable': False, 'drugs': [], 'class': 'Structural protein'},
        'MMP9': {'type': 'protease', 'dimension': 'ecm', 'druggable': True, 'drugs': ['Marimastat'], 'class': 'MMP inhibitor'},
        'TIMP1': {'type': 'protease_inhibitor', 'dimension': 'ecm', 'druggable': False, 'drugs': [], 'class': 'Endogenous inhibitor'},
        'ACTA2': {'type': 'caf_marker', 'dimension': 'stromal_cells', 'druggable': False, 'drugs': [], 'class': 'CAF marker'},
        
        # Transcription factors
        'STAT3': {'type': 'transcription_factor', 'dimension': 'tumor_cells', 'druggable': True, 'drugs': ['Ruxolitinib'], 'class': 'JAK/STAT inhibitor'},
        'NFKB1': {'type': 'transcription_factor', 'dimension': 'tumor_cells', 'druggable': True, 'drugs': ['Bortezomib'], 'class': 'NF-κB inhibitor'},
        'HIF1A': {'type': 'transcription_factor', 'dimension': 'tumor_cells', 'druggable': True, 'drugs': ['Topotecan'], 'class': 'HIF inhibitor'},
        
        # Cell cycle and apoptosis
        'CCND1': {'type': 'cell_cycle', 'dimension': 'tumor_cells', 'druggable': True, 'drugs': ['Palbociclib', 'Ribociclib'], 'class': 'CDK4/6 inhibitor'},
        'BCL2': {'type': 'apoptosis', 'dimension': 'tumor_cells', 'druggable': True, 'drugs': ['Venetoclax'], 'class': 'BCL-2 inhibitor'},
        'BAX': {'type': 'apoptosis', 'dimension': 'tumor_cells', 'druggable': False, 'drugs': [], 'class': 'Pro-apoptotic protein'}
    }
    
    @classmethod
    def generate_realistic_linchpin_data(cls, n_top: int = 20, seed: int = 42) -> pd.DataFrame:
        """Generate realistic linchpin analysis results using real LIHC genes"""
        np.random.seed(seed)
        
        # Select top genes based on clinical relevance
        genes = list(cls.REAL_LIHC_GENES.keys())
        
        # Prioritize highly druggable and clinically relevant genes
        priority_genes = [
            'TP53', 'MYC', 'EGFR', 'VEGFA', 'PD1', 'PDCD1', 'CD274', 'CTLA4',
            'VEGFR2', 'BRCA1', 'BRCA2', 'GPC3', 'IL6', 'TNF', 'MMP9', 'STAT3',
            'CCND1', 'BCL2', 'IDH1', 'PDGFRA'
        ]
        
        # Select genes for analysis
        if n_top <= len(priority_genes):
            selected_genes = priority_genes[:n_top]
        else:
            selected_genes = priority_genes + genes[:n_top - len(priority_genes)]
        
        linchpin_data = []
        for i, gene in enumerate(selected_genes[:n_top]):
            gene_info = cls.REAL_LIHC_GENES.get(gene, cls.REAL_LIHC_GENES['TP53'])  # fallback
            
            # Generate scores with some realistic weighting
            # Highly druggable genes get higher scores
            base_score = 0.9 - (i * 0.03)  # Decreasing score
            
            if gene_info['druggable']:
                prognostic_score = np.random.uniform(0.6, 0.95)
                hub_score = np.random.uniform(0.5, 0.9)
            else:
                prognostic_score = np.random.uniform(0.3, 0.7)
                hub_score = np.random.uniform(0.2, 0.6)
            
            cross_domain_score = np.random.uniform(0.4, 0.8)
            regulator_score = np.random.uniform(0.1, 0.6)
            
            # Calculate composite linchpin score
            linchpin_score = (0.4 * prognostic_score + 0.3 * hub_score + 
                            0.2 * cross_domain_score + 0.1 * regulator_score)
            
            # Determine if it's a master regulator
            is_master_regulator = gene_info['type'] in ['transcription_factor', 'oncogene'] and np.random.random() > 0.5
            
            linchpin_data.append({
                'feature': gene,
                'dimension': gene_info['dimension'],
                'linchpin_score': linchpin_score,
                'prognostic_score': prognostic_score,
                'hub_score': hub_score,
                'cross_domain_score': cross_domain_score,
                'regulator_score': regulator_score,
                'is_master_regulator': is_master_regulator,
                'gene_type': gene_info['type'],
                'druggable': gene_info['druggable'],
                'drug_class': gene_info['class']
            })
        
        df = pd.DataFrame(linchpin_data)
        return df.sort_values('linchpin_score', ascending=False)
    
    @classmethod
    def generate_realistic_druggability_data(cls, genes: list = None) -> pd.DataFrame:
        """Generate realistic druggability assessment data"""
        if genes is None:
            genes = list(cls.REAL_LIHC_GENES.keys())[:20]
        
        druggability_data = []
        for gene in genes:
            if gene in cls.REAL_LIHC_GENES:
                gene_info = cls.REAL_LIHC_GENES[gene]
                druggability_data.append({
                    'feature': gene,
                    'druggable': gene_info['druggable'],
                    'drugs': '; '.join(gene_info['drugs']) if gene_info['drugs'] else 'None',
                    'class': gene_info['class'],
                    'drug_count': len(gene_info['drugs'])
                })
        
        return pd.DataFrame(druggability_data)
    
    @classmethod
    def generate_realistic_evidence_cards(cls, genes: list = None) -> dict:
        """Generate realistic evidence cards for top linchpin genes"""
        if genes is None:
            genes = list(cls.REAL_LIHC_GENES.keys())[:10]
        
        evidence_cards = {}
        for i, gene in enumerate(genes):
            if gene in cls.REAL_LIHC_GENES:
                gene_info = cls.REAL_LIHC_GENES[gene]
                
                # Generate realistic scores
                prognostic_score = np.random.uniform(0.6, 0.95) if gene_info['druggable'] else np.random.uniform(0.3, 0.7)
                hub_score = np.random.uniform(0.5, 0.9) if gene_info['druggable'] else np.random.uniform(0.2, 0.6)
                cross_domain_score = np.random.uniform(0.4, 0.8)
                
                linchpin_score = (0.4 * prognostic_score + 0.3 * hub_score + 0.2 * cross_domain_score + 0.1 * np.random.uniform(0.1, 0.6))
                
                evidence_cards[gene] = {
                    "basic_info": {
                        "feature": gene,
                        "gene_name": gene,
                        "dimension": gene_info['dimension'],
                        "gene_type": gene_info['type'],
                        "linchpin_rank": i + 1
                    },
                    "scores": {
                        "composite_score": linchpin_score,
                        "prognostic_importance": prognostic_score,
                        "network_centrality": hub_score,
                        "cross_dimensional_impact": cross_domain_score
                    },
                    "druggability": {
                        "druggable": gene_info['druggable'],
                        "class": gene_info['class'],
                        "drugs": gene_info['drugs'],
                        "drug_count": len(gene_info['drugs'])
                    },
                    "clinical_relevance": {
                        "cancer_driver": gene_info['type'] in ['oncogene', 'tumor_suppressor'],
                        "therapeutic_target": gene_info['druggable'],
                        "biomarker_potential": gene_info['type'] in ['biomarker', 'immune_marker']
                    }
                }
        
        return evidence_cards
    
    @staticmethod
    def generate_clinical_data(n_samples: int = 100, seed: int = 42) -> pd.DataFrame:
        """Generate synthetic clinical data"""
        np.random.seed(seed)
        
        sample_ids = [f"SAMPLE_{i:03d}" for i in range(1, n_samples + 1)]
        
        # Generate survival times (exponential distribution)
        os_time = np.random.exponential(scale=365, size=n_samples)
        os_time = np.clip(os_time, 30, 2000).astype(int)  # 30 days to ~5 years
        
        # Generate survival status (30% events)
        os_status = np.random.binomial(1, 0.3, n_samples)
        
        # Optional clinical features
        age = np.random.normal(60, 12, n_samples).astype(int)
        age = np.clip(age, 25, 85)
        
        gender = np.random.choice(['Male', 'Female'], n_samples)
        stage = np.random.choice(['I', 'II', 'III', 'IV'], n_samples, p=[0.2, 0.3, 0.3, 0.2])
        
        return pd.DataFrame({
            'sample_id': sample_ids,
            'os_time': os_time,
            'os_status': os_status,
            'age': age,
            'gender': gender,
            'stage': stage
        })
    
    @staticmethod
    def generate_expression_data(n_genes: int = 1000, n_samples: int = 100, seed: int = 42) -> pd.DataFrame:
        """Generate synthetic expression data"""
        np.random.seed(seed)
        
        # Generate gene names
        gene_names = [f"GENE_{i:04d}" for i in range(1, n_genes + 1)]
        
        # Generate sample IDs
        sample_ids = [f"SAMPLE_{i:03d}" for i in range(1, n_samples + 1)]
        
        # Generate log-normal expression data
        expression_data = np.random.lognormal(mean=2, sigma=1, size=(n_genes, n_samples))
        
        # Add some noise and structure
        expression_data = np.log2(expression_data + 1)  # Log2 transform
        
        df = pd.DataFrame(expression_data, index=gene_names, columns=sample_ids)
        
        return df
    
    @staticmethod
    def generate_mutation_data(n_samples: int = 100, n_mutations: int = 200, seed: int = 42) -> pd.DataFrame:
        """Generate synthetic mutation data"""
        np.random.seed(seed)
        
        # Common cancer genes for realistic mutations
        cancer_genes = [
            'TP53', 'KRAS', 'PIK3CA', 'APC', 'PTEN', 'BRAF', 'EGFR', 'MYC',
            'RB1', 'BRCA1', 'BRCA2', 'ATM', 'CDKN2A', 'VHL', 'MLH1', 'MSH2',
            'CTNNB1', 'IDH1', 'IDH2', 'TERT', 'NFE2L2', 'KEAP1', 'AXIN1'
        ]
        
        # Generate random additional genes
        additional_genes = [f"GENE_{i:04d}" for i in range(1, 200)]
        all_genes = cancer_genes + additional_genes
        
        # Sample IDs
        sample_ids = [f"SAMPLE_{i:03d}" for i in range(1, n_samples + 1)]
        
        # Mutation types
        mutation_types = [
            'Missense_Mutation', 'Nonsense_Mutation', 'Frame_Shift_Del',
            'Frame_Shift_Ins', 'Splice_Site', 'Silent', 'In_Frame_Del', 'In_Frame_Ins'
        ]
        
        # Generate mutations
        mutations = []
        for _ in range(n_mutations):
            sample_id = np.random.choice(sample_ids)
            gene = np.random.choice(all_genes)
            mutation_type = np.random.choice(mutation_types)
            
            mutations.append({
                'sample_id': sample_id,
                'gene': gene,
                'mutation_type': mutation_type
            })
        
        return pd.DataFrame(mutations)

# Global instances for easy access
path_manager = PathManager()
config_manager = ConfigManager()
results_loader = ResultsLoader()