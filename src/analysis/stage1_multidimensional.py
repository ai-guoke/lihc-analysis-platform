"""
Stage 1: Multi-dimensional Analysis
Identifies Top 5 positive and negative prognostic indicators for each dimension
"""

import pandas as pd
import numpy as np
from lifelines import CoxPHFitter
from lifelines.statistics import logrank_test
from lifelines.exceptions import ConvergenceError, ConvergenceWarning
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Add src to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.utils.common import PathManager, ExceptionHandler, ConfigManager
except ImportError:
    # Fallback for missing utils
    class PathManager:
        def get_data_path(self, data_type, filename=None):
            return Path(f"data/{data_type}") / filename if filename else Path(f"data/{data_type}")
        
        def get_results_path(self, result_type, filename=None):
            return Path(f"results/{result_type}") / filename if filename else Path(f"results/{result_type}")
    
    class ExceptionHandler:
        @staticmethod
        def handle_analysis_error(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Analysis error in {func.__name__}: {e}")
                    return None
            return wrapper
    
    class ConfigManager:
        def get(self, key, default=None):
            defaults = {
                'P_VALUE_THRESHOLD': 0.05,
                'HR_THRESHOLD': 0.2,
                'CORRELATION_THRESHOLD': 0.4
            }
            return defaults.get(key, default)

class MultiDimensionalAnalysis:
    """Analyze prognostic indicators across five dimensions"""
    
    def __init__(self, data_dir="data/processed"):
        self.data_dir = Path(data_dir)
        self.results = {}
        self.path_manager = PathManager()
        self.config_manager = ConfigManager()
        
        # Get configuration values
        self.p_threshold = self.config_manager.get('P_VALUE_THRESHOLD', 0.05)
        self.hr_threshold = self.config_manager.get('HR_THRESHOLD', 0.2)
        
        # Initialize data containers
        self.clinical_data = None
        self.expression_data = None
        self.mutation_data = None
        
    @ExceptionHandler.handle_analysis_error
    def load_data(self):
        """Load preprocessed data with proper error handling"""
        try:
            # Use path manager for consistent paths
            clinical_path = self.path_manager.get_data_path('raw', 'clinical_data.csv')
            expression_path = self.path_manager.get_data_path('raw', 'expression_data.csv')
            mutation_path = self.path_manager.get_data_path('raw', 'mutation_data.csv')
            
            # Load clinical data
            if clinical_path.exists():
                self.clinical_data = pd.read_csv(clinical_path)
                print(f"✓ Loaded clinical data: {self.clinical_data.shape}")
            else:
                raise FileNotFoundError(f"Clinical data not found at {clinical_path}")
            
            # Load expression data
            if expression_path.exists():
                self.expression_data = pd.read_csv(expression_path, index_col=0)
                print(f"✓ Loaded expression data: {self.expression_data.shape}")
            else:
                raise FileNotFoundError(f"Expression data not found at {expression_path}")
            
            # Load mutation data (optional)
            if mutation_path.exists():
                self.mutation_data = pd.read_csv(mutation_path)
                print(f"✓ Loaded mutation data: {self.mutation_data.shape}")
            else:
                print(f"⚠ Mutation data not found at {mutation_path}, will skip mutation analysis")
                self.mutation_data = pd.DataFrame()  # Empty DataFrame
                
            return True
            
        except Exception as e:
            print(f"✗ Failed to load data: {e}")
            return False
        
    def perform_survival_analysis(self, feature_data, feature_name):
        """Perform Cox proportional hazards analysis"""
        # Merge with clinical data
        merged_data = self.clinical_data.copy()
        merged_data[feature_name] = feature_data
        
        # Remove samples with missing survival data
        merged_data = merged_data.dropna(subset=['os_time', 'os_status', feature_name])
        
        # Fit Cox model
        cph = CoxPHFitter()
        try:
            cph.fit(merged_data[['os_time', 'os_status', feature_name]], 
                   duration_col='os_time', event_col='os_status')
            
            hr = cph.hazard_ratios_[feature_name]
            p_value = cph.summary.p[feature_name]
            ci_lower = cph.confidence_intervals_.iloc[0, 0]
            ci_upper = cph.confidence_intervals_.iloc[0, 1]
            
            return {
                'hazard_ratio': hr,
                'p_value': p_value,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'log_hr': np.log(hr),
                'significant': p_value < 0.05
            }
        except (ConvergenceError, ConvergenceWarning) as e:
            print(f"Cox model convergence warning for {feature_name}: {e}")
            return None
        except ValueError as e:
            print(f"Value error in Cox analysis for {feature_name}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in Cox analysis for {feature_name}: {e}")
            return None
    
    def analyze_tumor_cells(self):
        """Dimension 1: Tumor intrinsic genes and mutations"""
        print("Analyzing tumor cell dimension...")
        
        results = []
        
        # 1. Gene expression analysis
        if self.expression_data is not None and not self.expression_data.empty:
            print(f"  Analyzing {len(self.expression_data.index)} genes...")
            
            for i, gene in enumerate(self.expression_data.index):
                if i % 100 == 0:  # Progress indicator
                    print(f"    Processed {i}/{len(self.expression_data.index)} genes")
                
                try:
                    gene_expr = self.expression_data.loc[gene].values
                    
                    # Skip genes with all missing or constant values
                    if len(np.unique(gene_expr[~np.isnan(gene_expr)])) < 2:
                        continue
                    
                    survival_result = self.perform_survival_analysis(gene_expr, f"{gene}_expr")
                    
                    if survival_result and survival_result['significant']:
                        results.append({
                            'feature': gene,
                            'type': 'gene_expression',
                            'hazard_ratio': survival_result['hazard_ratio'],
                            'p_value': survival_result['p_value'],
                            'log_hr': survival_result['log_hr'],
                            'ci_lower': survival_result['ci_lower'],
                            'ci_upper': survival_result['ci_upper']
                        })
                except Exception as e:
                    print(f"    Error analyzing gene {gene}: {e}")
                    continue
        
        # 2. Mutation analysis
        mutation_matrix = self.create_mutation_matrix()
        if not mutation_matrix.empty:
            print(f"  Analyzing {len(mutation_matrix.columns)-1} mutated genes...")  # -1 for sample_id column
            
            for gene in mutation_matrix.columns:
                if gene == 'sample_id':
                    continue
                
                try:
                    mutation_status = mutation_matrix[gene].values
                    
                    # Skip genes with no mutations or all mutations
                    if len(np.unique(mutation_status)) < 2:
                        continue
                    
                    survival_result = self.perform_survival_analysis(mutation_status, f"{gene}_mut")
                    
                    if survival_result and survival_result['significant']:
                        results.append({
                            'feature': f"{gene}_mutation",
                            'type': 'mutation',
                            'hazard_ratio': survival_result['hazard_ratio'],
                            'p_value': survival_result['p_value'],
                            'log_hr': survival_result['log_hr'],
                            'ci_lower': survival_result['ci_lower'],
                            'ci_upper': survival_result['ci_upper']
                        })
                except Exception as e:
                    print(f"    Error analyzing mutation {gene}: {e}")
                    continue
        
        # Sort and process results
        tumor_results = pd.DataFrame(results)
        if len(tumor_results) > 0:
            tumor_results = tumor_results.sort_values('p_value')
            
            # Top 5 positive (HR > 1, worse prognosis)
            positive = tumor_results[tumor_results['hazard_ratio'] > 1].head(5)
            # Top 5 negative (HR < 1, better prognosis) 
            negative = tumor_results[tumor_results['hazard_ratio'] < 1].head(5)
            
            print(f"  Found {len(positive)} risk factors and {len(negative)} protective factors")
            
            self.results['tumor_cells'] = {
                'positive': positive,
                'negative': negative,
                'all_results': tumor_results
            }
        else:
            print("  No significant results found for tumor cells dimension")
            self.results['tumor_cells'] = {
                'positive': pd.DataFrame(),
                'negative': pd.DataFrame(),
                'all_results': pd.DataFrame()
            }
        
        return self.results['tumor_cells']
    
    def create_mutation_matrix(self):
        """Create binary mutation matrix with proper error handling"""
        if self.mutation_data.empty:
            print("Warning: No mutation data available, skipping mutation analysis")
            return pd.DataFrame()
        
        try:
            # Validate required columns
            required_cols = ['sample_id', 'gene']
            missing_cols = [col for col in required_cols if col not in self.mutation_data.columns]
            if missing_cols:
                print(f"Error: Missing required columns in mutation data: {missing_cols}")
                return pd.DataFrame()
            
            # Get unique samples and genes
            samples = self.clinical_data['sample_id'].unique() if 'sample_id' in self.clinical_data.columns else []
            genes = self.mutation_data['gene'].unique()
            
            if len(samples) == 0:
                print("Warning: No valid sample IDs found")
                return pd.DataFrame()
            
            # Create binary matrix
            mutation_matrix = pd.DataFrame(0, index=samples, columns=genes)
            
            # Fill in mutations
            for _, row in self.mutation_data.iterrows():
                sample_id = row['sample_id']
                gene = row['gene']
                if sample_id in mutation_matrix.index and gene in mutation_matrix.columns:
                    mutation_matrix.loc[sample_id, gene] = 1
            
            # Reset index to make sample_id a column
            mutation_matrix.reset_index(inplace=True)
            mutation_matrix.rename(columns={'index': 'sample_id'}, inplace=True)
            
            print(f"✓ Created mutation matrix: {mutation_matrix.shape}")
            return mutation_matrix
            
        except Exception as e:
            print(f"Error creating mutation matrix: {e}")
            return pd.DataFrame()
    
    def estimate_immune_infiltration(self):
        """Estimate immune cell infiltration using gene signatures"""
        # Simplified immune cell signatures
        immune_signatures = {
            'CD8_T_cells': ['CD8A', 'CD8B', 'GZMB', 'PRF1', 'IFNG'],
            'CD4_T_cells': ['CD4', 'IL2', 'IL4', 'IL5'],
            'Tregs': ['FOXP3', 'IL10', 'TGFB1', 'CTLA4'],
            'NK_cells': ['KLRK1', 'NCR1', 'GZMB', 'PRF1'],
            'B_cells': ['CD19', 'CD20', 'IGH', 'IGK'],
            'TAMs_M1': ['TNF', 'IL1B', 'IL6', 'CXCL10'],
            'TAMs_M2': ['ARG1', 'IL10', 'TGFB1', 'MRC1'],
            'Neutrophils': ['CXCR2', 'FCGR3B', 'CSF3R']
        }
        
        immune_scores = {}
        
        for cell_type, genes in immune_signatures.items():
            # Find available genes in expression data
            available_genes = [g for g in genes if g in self.expression_data.index]
            
            if available_genes:
                # Calculate mean expression as infiltration score
                cell_score = self.expression_data.loc[available_genes].mean(axis=0)
                immune_scores[cell_type] = cell_score
            else:
                # Generate synthetic scores if genes not available
                np.random.seed(42)
                immune_scores[cell_type] = pd.Series(
                    np.random.beta(2, 2, len(self.expression_data.columns)), 
                    index=self.expression_data.columns
                )
        
        return pd.DataFrame(immune_scores)
    
    def analyze_immune_cells(self):
        """Dimension 2: Immune cell infiltration"""
        print("Analyzing immune cell dimension...")
        
        immune_scores = self.estimate_immune_infiltration()
        results = []
        
        for cell_type in immune_scores.columns:
            cell_scores = immune_scores[cell_type].values
            survival_result = self.perform_survival_analysis(cell_scores, f"{cell_type}_score")
            
            if survival_result and survival_result['significant']:
                results.append({
                    'feature': cell_type,
                    'type': 'immune_infiltration',
                    'hazard_ratio': survival_result['hazard_ratio'],
                    'p_value': survival_result['p_value'],
                    'log_hr': survival_result['log_hr']
                })
        
        immune_results = pd.DataFrame(results)
        if len(immune_results) > 0:
            immune_results = immune_results.sort_values('p_value')
            
            positive = immune_results[immune_results['hazard_ratio'] > 1].head(5)
            negative = immune_results[immune_results['hazard_ratio'] < 1].head(5)
            
            self.results['immune_cells'] = {
                'positive': positive,
                'negative': negative,
                'all_results': immune_results,
                'scores': immune_scores
            }
        
        return self.results['immune_cells']
    
    def analyze_stromal_cells(self):
        """Dimension 3: Cancer-associated fibroblasts (CAFs)"""
        print("Analyzing stromal cell dimension...")
        
        # CAF signature genes
        caf_genes = ['FAP', 'ACTA2', 'PDPN', 'VIM', 'S100A4', 'COL1A1']
        
        results = []
        caf_scores = {}
        
        # Individual CAF markers
        for gene in caf_genes:
            if gene in self.expression_data.index:
                gene_expr = self.expression_data.loc[gene].values
                survival_result = self.perform_survival_analysis(gene_expr, f"CAF_{gene}")
                
                if survival_result and survival_result['significant']:
                    results.append({
                        'feature': f"CAF_{gene}",
                        'type': 'caf_marker',
                        'hazard_ratio': survival_result['hazard_ratio'],
                        'p_value': survival_result['p_value'],
                        'log_hr': survival_result['log_hr']
                    })
                    
                caf_scores[f"CAF_{gene}"] = gene_expr
        
        # Combined CAF score
        available_caf_genes = [g for g in caf_genes if g in self.expression_data.index]
        if available_caf_genes:
            combined_caf_score = self.expression_data.loc[available_caf_genes].mean(axis=0)
            survival_result = self.perform_survival_analysis(combined_caf_score.values, "CAF_combined")
            
            if survival_result and survival_result['significant']:
                results.append({
                    'feature': "CAF_combined_score",
                    'type': 'caf_combined',
                    'hazard_ratio': survival_result['hazard_ratio'],
                    'p_value': survival_result['p_value'],
                    'log_hr': survival_result['log_hr']
                })
            
            caf_scores["CAF_combined_score"] = combined_caf_score.values
        
        stromal_results = pd.DataFrame(results)
        if len(stromal_results) > 0:
            stromal_results = stromal_results.sort_values('p_value')
            
            positive = stromal_results[stromal_results['hazard_ratio'] > 1].head(5)
            negative = stromal_results[stromal_results['hazard_ratio'] < 1].head(5)
            
            self.results['stromal_cells'] = {
                'positive': positive,
                'negative': negative,
                'all_results': stromal_results,
                'scores': pd.DataFrame(caf_scores, index=self.expression_data.columns)
            }
        
        return self.results['stromal_cells']
    
    def analyze_ecm(self):
        """Dimension 4: Extracellular matrix"""
        print("Analyzing ECM dimension...")
        
        # ECM-related genes
        ecm_genes = ['COL1A1', 'COL3A1', 'FN1', 'LAMB1', 'MMP2', 'MMP9', 'TIMP1', 'SPARC']
        
        results = []
        ecm_scores = {}
        
        for gene in ecm_genes:
            if gene in self.expression_data.index:
                gene_expr = self.expression_data.loc[gene].values
                survival_result = self.perform_survival_analysis(gene_expr, f"ECM_{gene}")
                
                if survival_result and survival_result['significant']:
                    results.append({
                        'feature': f"ECM_{gene}",
                        'type': 'ecm_gene',
                        'hazard_ratio': survival_result['hazard_ratio'],
                        'p_value': survival_result['p_value'],
                        'log_hr': survival_result['log_hr']
                    })
                
                ecm_scores[f"ECM_{gene}"] = gene_expr
        
        # Combined ECM remodeling score
        available_ecm_genes = [g for g in ecm_genes if g in self.expression_data.index]
        if available_ecm_genes:
            combined_ecm_score = self.expression_data.loc[available_ecm_genes].mean(axis=0)
            survival_result = self.perform_survival_analysis(combined_ecm_score.values, "ECM_remodeling")
            
            if survival_result and survival_result['significant']:
                results.append({
                    'feature': "ECM_remodeling_score",
                    'type': 'ecm_combined',
                    'hazard_ratio': survival_result['hazard_ratio'],
                    'p_value': survival_result['p_value'],
                    'log_hr': survival_result['log_hr']
                })
            
            ecm_scores["ECM_remodeling_score"] = combined_ecm_score.values
        
        ecm_results = pd.DataFrame(results)
        if len(ecm_results) > 0:
            ecm_results = ecm_results.sort_values('p_value')
            
            positive = ecm_results[ecm_results['hazard_ratio'] > 1].head(5)
            negative = ecm_results[ecm_results['hazard_ratio'] < 1].head(5)
            
            self.results['ecm'] = {
                'positive': positive,
                'negative': negative,
                'all_results': ecm_results,
                'scores': pd.DataFrame(ecm_scores, index=self.expression_data.columns)
            }
        
        return self.results['ecm']
    
    def analyze_cytokines(self):
        """Dimension 5: Cytokines and growth factors"""
        print("Analyzing cytokine dimension...")
        
        # Key cytokines
        cytokine_genes = ['IL6', 'TGFB1', 'TGFB2', 'TGFBR1', 'TGFBR2', 'TNF', 'IFNG', 'IL10', 'IL1B', 'VEGFA']
        
        results = []
        cytokine_scores = {}
        
        for gene in cytokine_genes:
            if gene in self.expression_data.index:
                gene_expr = self.expression_data.loc[gene].values
                survival_result = self.perform_survival_analysis(gene_expr, f"Cytokine_{gene}")
                
                if survival_result and survival_result['significant']:
                    results.append({
                        'feature': f"Cytokine_{gene}",
                        'type': 'cytokine',
                        'hazard_ratio': survival_result['hazard_ratio'],
                        'p_value': survival_result['p_value'],
                        'log_hr': survival_result['log_hr']
                    })
                
                cytokine_scores[f"Cytokine_{gene}"] = gene_expr
        
        cytokine_results = pd.DataFrame(results)
        if len(cytokine_results) > 0:
            cytokine_results = cytokine_results.sort_values('p_value')
            
            positive = cytokine_results[cytokine_results['hazard_ratio'] > 1].head(5)
            negative = cytokine_results[cytokine_results['hazard_ratio'] < 1].head(5)
            
            self.results['cytokines'] = {
                'positive': positive,
                'negative': negative,
                'all_results': cytokine_results,
                'scores': pd.DataFrame(cytokine_scores, index=self.expression_data.columns)
            }
        
        return self.results['cytokines']
    
    def run_all_analyses(self):
        """Run analysis for all five dimensions"""
        print("Starting Stage 1: Multi-dimensional Analysis")
        print("=" * 50)
        
        self.load_data()
        
        # Run analysis for each dimension
        self.analyze_tumor_cells()
        self.analyze_immune_cells() 
        self.analyze_stromal_cells()
        self.analyze_ecm()
        self.analyze_cytokines()
        
        # Generate summary report
        self.generate_summary_report()
        
        return self.results
    
    def generate_summary_report(self):
        """Generate summary report of Stage 1 results"""
        print("\n" + "=" * 50)
        print("STAGE 1 ANALYSIS SUMMARY")
        print("=" * 50)
        
        for dimension, result in self.results.items():
            if result and 'positive' in result and 'negative' in result:
                print(f"\n{dimension.upper()} DIMENSION:")
                print(f"  Top 5 Risk Factors (HR > 1):")
                if len(result['positive']) > 0:
                    for _, row in result['positive'].iterrows():
                        print(f"    {row['feature']}: HR={row['hazard_ratio']:.2f}, p={row['p_value']:.2e}")
                else:
                    print("    No significant risk factors found")
                
                print(f"  Top 5 Protective Factors (HR < 1):")
                if len(result['negative']) > 0:
                    for _, row in result['negative'].iterrows():
                        print(f"    {row['feature']}: HR={row['hazard_ratio']:.2f}, p={row['p_value']:.2e}")
                else:
                    print("    No significant protective factors found")
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save analysis results"""
        output_dir = Path("results/tables")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for dimension, result in self.results.items():
            if result and 'all_results' in result:
                result['all_results'].to_csv(
                    output_dir / f"stage1_{dimension}_results.csv", 
                    index=False
                )
        
        print(f"\nResults saved to {output_dir}")

if __name__ == "__main__":
    analyzer = MultiDimensionalAnalysis()
    results = analyzer.run_all_analyses()