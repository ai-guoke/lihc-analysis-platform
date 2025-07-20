"""
Stage 3: Linchpin Identification System
Identifies the most critical driver nodes - the "牛鼻子" (linchpin) molecules
"""

import pandas as pd
import numpy as np
import networkx as nx
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import json
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
        def get_results_path(self, result_type, filename=None):
            return Path(f"results/{result_type}") / filename if filename else Path(f"results/{result_type}")
    
    class ExceptionHandler:
        @staticmethod
        def handle_analysis_error(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Linchpin analysis error in {func.__name__}: {e}")
                    return None
            return wrapper
    
    class ConfigManager:
        def get(self, key, default=None):
            defaults = {
                'LINCHPIN_WEIGHTS': {
                    'prognostic_score': 0.4,
                    'network_hub_score': 0.3,
                    'cross_domain_score': 0.2,
                    'regulator_score': 0.1
                }
            }
            return defaults.get(key, default)

class LinchpinIdentifier:
    """Identify and rank critical driver nodes in the multi-dimensional network"""
    
    def __init__(self, stage2_results=None):
        self.stage2_results = stage2_results
        self.linchpin_scores = None
        self.master_regulators = {}
        self.druggability_info = {}
        
        # Initialize managers
        self.path_manager = PathManager()
        self.config_manager = ConfigManager()
        
        # Scoring weights (configurable)
        default_weights = {
            'prognostic_score': 0.4,
            'network_hub_score': 0.3,
            'cross_domain_score': 0.2,
            'regulator_score': 0.1
        }
        self.weights = self.config_manager.get('LINCHPIN_WEIGHTS', default_weights)
        
        # Initialize data containers
        self.centrality_measures = None
        self.correlation_matrix = None
        self.cross_dimensional_connections = None
        self.network = None
    
    @ExceptionHandler.handle_analysis_error
    def load_stage2_results(self):
        """Load Stage 2 network analysis results with proper error handling"""
        if self.stage2_results is None:
            # Load from files if not provided
            results_dir = self.path_manager.get_results_path('networks')
            
            try:
                # Try to load centrality measures
                centrality_path = results_dir / "network_centrality.csv"
                if centrality_path.exists():
                    self.centrality_measures = pd.read_csv(centrality_path)
                    print(f"✓ Loaded centrality measures: {len(self.centrality_measures)} nodes")
                else:
                    print(f"⚠ Centrality measures not found at {centrality_path}")
                
                # Try to load correlation matrix
                correlation_path = results_dir / "correlation_matrix.csv"
                if correlation_path.exists():
                    self.correlation_matrix = pd.read_csv(correlation_path, index_col=0)
                    print(f"✓ Loaded correlation matrix: {self.correlation_matrix.shape}")
                else:
                    print(f"⚠ Correlation matrix not found at {correlation_path}")
                
                # Try to load cross-dimensional connections
                connections_path = results_dir / "cross_dimensional_connections.csv"
                if connections_path.exists():
                    self.cross_dimensional_connections = pd.read_csv(connections_path)
                    print(f"✓ Loaded cross-dimensional connections: {len(self.cross_dimensional_connections)}")
                else:
                    print(f"⚠ Cross-dimensional connections not found at {connections_path}")
                
                # Try to load network (optional)
                network_path = results_dir / "cross_dimensional_network.graphml"
                if network_path.exists():
                    try:
                        self.network = nx.read_graphml(network_path)
                        print(f"✓ Loaded network: {len(self.network.nodes)} nodes, {len(self.network.edges)} edges")
                    except Exception as e:
                        print(f"⚠ Could not load network file: {e}")
                        self.network = None
                else:
                    print(f"⚠ Network file not found at {network_path}")
                    self.network = None
                    
            except Exception as e:
                print(f"Error loading Stage 2 results from files: {e}")
                return False
                
        else:
            # Use provided results
            try:
                self.centrality_measures = self.stage2_results.get('centrality_measures')
                self.correlation_matrix = self.stage2_results.get('correlation_matrix')
                self.cross_dimensional_connections = self.stage2_results.get('cross_dimensional_connections')
                self.network = self.stage2_results.get('network')
                print("✓ Loaded Stage 2 results from provided data")
            except Exception as e:
                print(f"Error loading provided Stage 2 results: {e}")
                return False
        
        # Validate that we have minimum required data
        if self.centrality_measures is None or self.centrality_measures.empty:
            print("Error: No centrality measures available for linchpin analysis")
            return False
            
        print("Loaded Stage 2 results from memory")
        return True
    
    def calculate_prognostic_scores(self):
        """Calculate prognostic importance scores"""
        print("Calculating prognostic importance scores...")
        
        # Load Stage 1 results to get prognostic significance
        stage1_results = {}
        results_dir = Path("results/tables")
        
        for dimension in ['tumor_cells', 'immune_cells', 'stromal_cells', 'ecm', 'cytokines']:
            file_path = results_dir / f"stage1_{dimension}_results.csv"
            if file_path.exists():
                stage1_results[dimension] = pd.read_csv(file_path)
        
        # Combine all prognostic results
        all_prognostic = []
        for dimension, df in stage1_results.items():
            df['dimension'] = dimension
            all_prognostic.append(df)
        
        combined_prognostic = pd.concat(all_prognostic, ignore_index=True)
        
        # Calculate prognostic scores
        prognostic_scores = {}
        
        for feature in self.centrality_measures['feature']:
            matching_rows = combined_prognostic[combined_prognostic['feature'] == feature]
            
            if len(matching_rows) > 0:
                row = matching_rows.iloc[0]
                # Score based on statistical significance and effect size
                log_p = -np.log10(max(row['p_value'], 1e-10))  # Avoid log(0)
                effect_size = abs(row['log_hr'])
                
                # Combined prognostic score
                prognostic_score = log_p * effect_size
                prognostic_scores[feature] = prognostic_score
            else:
                prognostic_scores[feature] = 0.0
        
        # Normalize scores to 0-1 scale
        if prognostic_scores:
            max_score = max(prognostic_scores.values())
            if max_score > 0:
                prognostic_scores = {k: v/max_score for k, v in prognostic_scores.items()}
        
        return prognostic_scores
    
    def calculate_network_hub_scores(self):
        """Calculate network hub importance scores"""
        print("Calculating network hub scores...")
        
        # Use precomputed hub scores from Stage 2
        hub_scores = {}
        
        for _, row in self.centrality_measures.iterrows():
            feature = row['feature']
            # Combine multiple centrality measures with emphasis on betweenness (bottleneck importance)
            hub_score = (0.4 * row['betweenness_centrality'] + 
                        0.3 * row['degree_centrality'] + 
                        0.3 * row['eigenvector_centrality'])
            hub_scores[feature] = hub_score
        
        # Normalize to 0-1 scale
        if hub_scores:
            max_score = max(hub_scores.values())
            if max_score > 0:
                hub_scores = {k: v/max_score for k, v in hub_scores.items()}
        
        return hub_scores
    
    def calculate_cross_domain_scores(self):
        """Calculate cross-dimensional connectivity scores"""
        print("Calculating cross-dimensional connectivity scores...")
        
        cross_domain_scores = {}
        
        for feature in self.centrality_measures['feature']:
            # Count connections to different dimensions
            dimensions_connected = set()
            total_cross_connections = 0
            
            if feature in self.network:
                for neighbor in self.network.neighbors(feature):
                    neighbor_dim = None
                    # Find neighbor dimension from centrality measures
                    neighbor_row = self.centrality_measures[self.centrality_measures['feature'] == neighbor]
                    if len(neighbor_row) > 0:
                        neighbor_dim = neighbor_row.iloc[0]['dimension']
                    
                    feature_dim = self.centrality_measures[
                        self.centrality_measures['feature'] == feature
                    ].iloc[0]['dimension']
                    
                    if neighbor_dim and neighbor_dim != feature_dim:
                        dimensions_connected.add(neighbor_dim)
                        total_cross_connections += 1
            
            # Score based on diversity of connections and total cross-connections
            diversity_score = len(dimensions_connected) / 4.0  # Max 4 other dimensions
            connection_score = min(total_cross_connections / 10.0, 1.0)  # Normalize
            
            cross_domain_scores[feature] = 0.6 * diversity_score + 0.4 * connection_score
        
        return cross_domain_scores
    
    def identify_master_regulators(self):
        """Identify potential master regulators"""
        print("Identifying master regulators...")
        
        # Known transcription factors and kinases (simplified database)
        known_regulators = {
            'transcription_factors': ['TP53', 'MYC', 'CTNNB1', 'JUN', 'FOS', 'STAT3', 'NF1', 'ETS1'],
            'kinases': ['PIK3CA', 'EGFR', 'MTOR', 'AKT1', 'MAPK1', 'CDK4', 'ATM'],
            'growth_factors': ['TGFB1', 'VEGFA', 'IL6', 'TNF', 'IFNG'],
            'epigenetic': ['DNMT1', 'HDAC1', 'EZH2', 'KMT2A']
        }
        
        regulator_scores = {}
        
        for feature in self.centrality_measures['feature']:
            regulator_score = 0.0
            regulator_type = None
            
            # Check if feature is a known regulator
            for reg_type, regulators in known_regulators.items():
                for reg in regulators:
                    if reg in feature:
                        regulator_score = 1.0
                        regulator_type = reg_type
                        break
                if regulator_score > 0:
                    break
            
            # Additional scoring based on network properties
            if feature in self.network:
                # High out-degree suggests regulatory potential
                out_degree = self.network.degree(feature)
                if out_degree > 5:  # Arbitrary threshold
                    regulator_score = max(regulator_score, 0.5)
            
            regulator_scores[feature] = regulator_score
            
            if regulator_score > 0:
                self.master_regulators[feature] = {
                    'score': regulator_score,
                    'type': regulator_type,
                    'evidence': 'known_regulator' if regulator_type else 'network_topology'
                }
        
        return regulator_scores
    
    def calculate_composite_linchpin_scores(self):
        """Calculate final composite linchpin scores"""
        print("Calculating composite linchpin scores...")
        
        # Get component scores
        prognostic_scores = self.calculate_prognostic_scores()
        hub_scores = self.calculate_network_hub_scores()
        cross_domain_scores = self.calculate_cross_domain_scores()
        regulator_scores = self.identify_master_regulators()
        
        # Calculate composite scores
        composite_scores = []
        
        for feature in self.centrality_measures['feature']:
            prog_score = prognostic_scores.get(feature, 0.0)
            hub_score = hub_scores.get(feature, 0.0)
            cross_score = cross_domain_scores.get(feature, 0.0)
            reg_score = regulator_scores.get(feature, 0.0)
            
            # Weighted composite score
            composite_score = (
                self.weights['prognostic_score'] * prog_score +
                self.weights['network_hub_score'] * hub_score +
                self.weights['cross_domain_score'] * cross_score +
                self.weights['regulator_score'] * reg_score
            )
            
            # Get dimension
            feature_dim = self.centrality_measures[
                self.centrality_measures['feature'] == feature
            ].iloc[0]['dimension']
            
            composite_scores.append({
                'feature': feature,
                'dimension': feature_dim,
                'linchpin_score': composite_score,
                'prognostic_score': prog_score,
                'hub_score': hub_score,
                'cross_domain_score': cross_score,
                'regulator_score': reg_score,
                'is_master_regulator': feature in self.master_regulators
            })
        
        self.linchpin_scores = pd.DataFrame(composite_scores)
        self.linchpin_scores = self.linchpin_scores.sort_values('linchpin_score', ascending=False)
        
        return self.linchpin_scores
    
    def assess_druggability(self):
        """Assess druggability of top linchpin candidates"""
        print("Assessing druggability...")
        
        # Simplified druggability database
        druggable_targets = {
            'TP53': {'druggable': True, 'drugs': ['Nutlin-3', 'PRIMA-1'], 'class': 'Tumor suppressor modulator'},
            'EGFR': {'druggable': True, 'drugs': ['Erlotinib', 'Gefitinib'], 'class': 'Kinase inhibitor'},
            'VEGFA': {'druggable': True, 'drugs': ['Bevacizumab', 'Sorafenib'], 'class': 'Angiogenesis inhibitor'},
            'TGFB1': {'druggable': True, 'drugs': ['Galunisertib', 'Fresolimumab'], 'class': 'TGF-β inhibitor'},
            'IL6': {'druggable': True, 'drugs': ['Tocilizumab', 'Siltuximab'], 'class': 'Cytokine inhibitor'},
            'PIK3CA': {'druggable': True, 'drugs': ['Alpelisib', 'Copanlisib'], 'class': 'PI3K inhibitor'},
            'MYC': {'druggable': False, 'drugs': [], 'class': 'Transcription factor (challenging)'},
            'CTNNB1': {'druggable': False, 'drugs': [], 'class': 'Protein-protein interaction'},
        }
        
        # Assess druggability for top candidates
        top_candidates = self.linchpin_scores.head(20)
        
        for _, row in top_candidates.iterrows():
            feature = row['feature']
            
            # Extract gene name from feature
            gene_name = feature.split('_')[0] if '_' in feature else feature
            
            if gene_name in druggable_targets:
                self.druggability_info[feature] = druggable_targets[gene_name]
            else:
                # Default assessment
                self.druggability_info[feature] = {
                    'druggable': None,  # Unknown
                    'drugs': [],
                    'class': 'Assessment needed'
                }
        
        return self.druggability_info
    
    def generate_evidence_cards(self):
        """Generate detailed evidence cards for top linchpin candidates"""
        print("Generating evidence cards...")
        
        top_candidates = self.linchpin_scores.head(10)
        evidence_cards = {}
        
        for _, row in top_candidates.iterrows():
            feature = row['feature']
            
            # Compile evidence
            evidence = {
                'basic_info': {
                    'feature': feature,
                    'dimension': row['dimension'],
                    'linchpin_rank': _ + 1
                },
                'scores': {
                    'composite_score': row['linchpin_score'],
                    'prognostic_importance': row['prognostic_score'],
                    'network_centrality': row['hub_score'],
                    'cross_dimensional_impact': row['cross_domain_score'],
                    'regulatory_potential': row['regulator_score']
                },
                'network_properties': {},
                'clinical_relevance': {},
                'druggability': self.druggability_info.get(feature, {'druggable': None}),
                'master_regulator_info': self.master_regulators.get(feature, None)
            }
            
            # Add network properties
            if feature in self.network:
                evidence['network_properties'] = {
                    'degree': self.network.degree(feature),
                    'neighbors': list(self.network.neighbors(feature))[:5],  # Top 5 neighbors
                    'clustering_coefficient': nx.clustering(self.network, feature)
                }
            
            evidence_cards[feature] = evidence
        
        self.evidence_cards = evidence_cards
        return evidence_cards
    
    def run_linchpin_analysis(self):
        """Run complete linchpin identification analysis"""
        print("Starting Stage 3: Linchpin Identification")
        print("=" * 50)
        
        # Load Stage 2 results
        self.load_stage2_results()
        
        # Calculate composite scores
        self.calculate_composite_linchpin_scores()
        
        # Assess druggability
        self.assess_druggability()
        
        # Generate evidence cards
        self.generate_evidence_cards()
        
        # Generate summary report
        self.generate_summary_report()
        
        # Save results
        self.save_results()
        
        return {
            'linchpin_scores': self.linchpin_scores,
            'evidence_cards': self.evidence_cards,
            'master_regulators': self.master_regulators,
            'druggability_info': self.druggability_info
        }
    
    def generate_summary_report(self):
        """Generate comprehensive linchpin analysis summary"""
        print("\n" + "=" * 50)
        print("STAGE 3 LINCHPIN ANALYSIS SUMMARY")
        print("=" * 50)
        
        print(f"\nTOP 10 LINCHPIN CANDIDATES (牛鼻子):")
        print("-" * 50)
        
        for i, (_, row) in enumerate(self.linchpin_scores.head(10).iterrows()):
            print(f"\n{i+1}. {row['feature']} ({row['dimension']})")
            print(f"   Composite Score: {row['linchpin_score']:.3f}")
            print(f"   Components: Prog={row['prognostic_score']:.2f}, "
                  f"Hub={row['hub_score']:.2f}, Cross={row['cross_domain_score']:.2f}, "
                  f"Reg={row['regulator_score']:.2f}")
            
            # Add druggability info
            feature = row['feature']
            if feature in self.druggability_info:
                drug_info = self.druggability_info[feature]
                if drug_info['druggable']:
                    print(f"   💊 DRUGGABLE: {drug_info['class']}")
                    if drug_info['drugs']:
                        print(f"   Available drugs: {', '.join(drug_info['drugs'][:2])}")
                elif drug_info['druggable'] is False:
                    print(f"   ⚠️  Challenging target: {drug_info['class']}")
                else:
                    print(f"   ❓ Druggability unknown")
            
            # Master regulator info
            if row['is_master_regulator']:
                reg_info = self.master_regulators[feature]
                print(f"   🎯 MASTER REGULATOR: {reg_info['type']}")
        
        print(f"\nKEY INSIGHTS:")
        print(f"✓ Identified {len(self.linchpin_scores)} ranked candidates")
        print(f"✓ Found {sum(self.linchpin_scores['is_master_regulator'])} master regulators")
        
        druggable_count = sum(1 for info in self.druggability_info.values() 
                             if info.get('druggable') == True)
        print(f"✓ {druggable_count} druggable targets in top candidates")
        
        # Dimension analysis
        top_10_dims = self.linchpin_scores.head(10)['dimension'].value_counts()
        print(f"✓ Top dimensions in linchpin list: {dict(top_10_dims)}")
        
        print(f"\nRECOMMENDATIONS:")
        print(f"🎯 Priority 1: Focus on top 3 druggable linchpins")
        print(f"🔬 Priority 2: Validate master regulators experimentally")
        print(f"💡 Priority 3: Investigate cross-dimensional mechanisms")
    
    def save_results(self):
        """Save all linchpin analysis results"""
        output_dir = Path("results/linchpins")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save linchpin scores
        self.linchpin_scores.to_csv(output_dir / "linchpin_scores.csv", index=False)
        
        # Save evidence cards as JSON
        import json
        with open(output_dir / "evidence_cards.json", 'w') as f:
            json.dump(self.evidence_cards, f, indent=2, default=str)
        
        # Save master regulators
        master_reg_df = pd.DataFrame([
            {'feature': k, **v} for k, v in self.master_regulators.items()
        ])
        master_reg_df.to_csv(output_dir / "master_regulators.csv", index=False)
        
        # Save druggability assessment
        druggability_df = pd.DataFrame([
            {'feature': k, **v} for k, v in self.druggability_info.items()
        ])
        druggability_df.to_csv(output_dir / "druggability_assessment.csv", index=False)
        
        print(f"\nStage 3 results saved to {output_dir}")

if __name__ == "__main__":
    identifier = LinchpinIdentifier()
    results = identifier.run_linchpin_analysis()