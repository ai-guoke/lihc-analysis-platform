"""
Advanced Analysis Pipeline with Real Algorithms
高级分析流程，集成真实的生物信息学算法
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import ttest_ind, mannwhitneyu, pearsonr, spearmanr
from scipy.cluster import hierarchy
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import networkx as nx
from pathlib import Path
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Import progress manager
try:
    from .progress_manager import ProgressManager, ProgressUpdater
    PROGRESS_AVAILABLE = True
except ImportError:
    PROGRESS_AVAILABLE = False

class AdvancedAnalyzer:
    """Execute advanced bioinformatics analysis with real algorithms"""
    
    def __init__(self, session_id: str, progress_manager: Optional[ProgressManager] = None):
        self.session_id = session_id
        self.data_dir = Path(f"data/user_uploads/{session_id}")
        self.results_dir = Path(f"data/history/{session_id}/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Progress manager
        self.progress_manager = progress_manager
        if not self.progress_manager and PROGRESS_AVAILABLE:
            self.progress_manager = ProgressManager(session_id)
        
        # Analysis parameters (can be configured)
        self.params = {
            'pvalue_threshold': 0.05,
            'foldchange_threshold': 2.0,
            'min_samples': 3,
            'correlation_threshold': 0.7,
            'top_genes': 50
        }
    
    def differential_expression_analysis(self, expression_df: pd.DataFrame, 
                                       clinical_df: pd.DataFrame,
                                       group_column: str = 'stage') -> Dict:
        """
        Perform differential expression analysis
        差异表达分析 - 使用t检验或Mann-Whitney U检验
        """
        results = {
            'method': 'differential_expression',
            'group_column': group_column,
            'genes': []
        }
        
        # Get unique groups
        if group_column not in clinical_df.columns:
            # Create binary groups based on survival
            if 'os_status' in clinical_df.columns:
                clinical_df['group'] = clinical_df['os_status'].apply(lambda x: 'High' if x == 1 else 'Low')
                group_column = 'group'
            else:
                # Random grouping for demo
                clinical_df['group'] = np.random.choice(['GroupA', 'GroupB'], size=len(clinical_df))
                group_column = 'group'
        
        groups = clinical_df[group_column].unique()
        if len(groups) < 2:
            return results
        
        # Compare first two groups
        group1_samples = clinical_df[clinical_df[group_column] == groups[0]]['sample_id'].tolist()
        group2_samples = clinical_df[clinical_df[group_column] == groups[1]]['sample_id'].tolist()
        
        # Filter samples that exist in expression data
        group1_samples = [s for s in group1_samples if s in expression_df.columns]
        group2_samples = [s for s in group2_samples if s in expression_df.columns]
        
        if len(group1_samples) < self.params['min_samples'] or len(group2_samples) < self.params['min_samples']:
            return results
        
        # Perform differential expression for each gene
        for gene in expression_df.index:
            group1_expr = expression_df.loc[gene, group1_samples].values
            group2_expr = expression_df.loc[gene, group2_samples].values
            
            # Remove NaN values
            group1_expr = group1_expr[~np.isnan(group1_expr)]
            group2_expr = group2_expr[~np.isnan(group2_expr)]
            
            if len(group1_expr) < 2 or len(group2_expr) < 2:
                continue
            
            # Calculate statistics
            mean1, mean2 = np.mean(group1_expr), np.mean(group2_expr)
            fold_change = mean2 / (mean1 + 1e-10)  # Avoid division by zero
            log2_fc = np.log2(fold_change + 1e-10)
            
            # Statistical test (t-test or Mann-Whitney U)
            if stats.shapiro(group1_expr)[1] > 0.05 and stats.shapiro(group2_expr)[1] > 0.05:
                # Normal distribution - use t-test
                statistic, pvalue = ttest_ind(group1_expr, group2_expr)
                test_type = 't-test'
            else:
                # Non-normal - use Mann-Whitney U
                statistic, pvalue = mannwhitneyu(group1_expr, group2_expr)
                test_type = 'Mann-Whitney'
            
            # Adjust p-value (Bonferroni correction)
            adjusted_pvalue = pvalue * len(expression_df.index)
            adjusted_pvalue = min(adjusted_pvalue, 1.0)
            
            results['genes'].append({
                'gene': gene,
                'mean_group1': float(mean1),
                'mean_group2': float(mean2),
                'fold_change': float(fold_change),
                'log2_fc': float(log2_fc),
                'pvalue': float(pvalue),
                'adjusted_pvalue': float(adjusted_pvalue),
                'test_type': test_type,
                'significant': pvalue < self.params['pvalue_threshold'] and 
                              abs(log2_fc) > np.log2(self.params['foldchange_threshold'])
            })
        
        # Sort by p-value
        results['genes'] = sorted(results['genes'], key=lambda x: x['pvalue'])
        
        # Create volcano plot
        self._create_volcano_plot(results['genes'])
        
        return results
    
    def survival_analysis(self, clinical_df: pd.DataFrame, 
                         expression_df: pd.DataFrame = None,
                         gene: str = None) -> Dict:
        """
        Perform survival analysis
        生存分析 - Kaplan-Meier和Cox回归
        """
        from lifelines import KaplanMeierFitter, CoxPHFitter
        from lifelines.statistics import logrank_test
        
        results = {
            'method': 'survival_analysis',
            'analyses': []
        }
        
        # Basic Kaplan-Meier
        if 'os_time' in clinical_df.columns and 'os_status' in clinical_df.columns:
            kmf = KaplanMeierFitter()
            kmf.fit(clinical_df['os_time'], clinical_df['os_status'])
            
            # Overall survival statistics
            median_survival = kmf.median_survival_time_
            survival_at_1_year = kmf.predict(365) if max(clinical_df['os_time']) > 365 else None
            
            results['overall_survival'] = {
                'median_survival_days': float(median_survival) if not np.isnan(median_survival) else None,
                'survival_at_1_year': float(survival_at_1_year) if survival_at_1_year else None,
                'total_patients': len(clinical_df),
                'events': int(clinical_df['os_status'].sum())
            }
            
            # Gene-based survival analysis
            if expression_df is not None and gene and gene in expression_df.index:
                gene_expr = expression_df.loc[gene]
                median_expr = gene_expr.median()
                
                # Split into high/low expression groups
                high_expr = gene_expr >= median_expr
                low_expr = gene_expr < median_expr
                
                # Get clinical data for each group
                high_samples = gene_expr[high_expr].index
                low_samples = gene_expr[low_expr].index
                
                high_clinical = clinical_df[clinical_df['sample_id'].isin(high_samples)]
                low_clinical = clinical_df[clinical_df['sample_id'].isin(low_samples)]
                
                if len(high_clinical) > 0 and len(low_clinical) > 0:
                    # Perform log-rank test
                    lr_result = logrank_test(
                        high_clinical['os_time'], low_clinical['os_time'],
                        high_clinical['os_status'], low_clinical['os_status']
                    )
                    
                    results['gene_survival'] = {
                        'gene': gene,
                        'high_expr_n': len(high_clinical),
                        'low_expr_n': len(low_clinical),
                        'logrank_pvalue': float(lr_result.p_value),
                        'test_statistic': float(lr_result.test_statistic)
                    }
            
            # Cox proportional hazards
            if 'age' in clinical_df.columns:
                cox_df = clinical_df[['os_time', 'os_status', 'age']].dropna()
                if len(cox_df) > 10:
                    cph = CoxPHFitter()
                    cph.fit(cox_df, duration_col='os_time', event_col='os_status')
                    
                    results['cox_model'] = {
                        'concordance_index': float(cph.concordance_index_),
                        'age_hazard_ratio': float(np.exp(cph.params_['age'])),
                        'age_pvalue': float(cph.summary.p['age'])
                    }
            
            # Create survival plot
            self._create_survival_plot(clinical_df, gene, expression_df)
        
        return results
    
    def network_analysis(self, expression_df: pd.DataFrame) -> Dict:
        """
        Perform gene co-expression network analysis
        基因共表达网络分析
        """
        results = {
            'method': 'network_analysis',
            'network_stats': {},
            'modules': [],
            'hub_genes': []
        }
        
        # Select top variable genes
        gene_variance = expression_df.var(axis=1)
        top_genes = gene_variance.nlargest(self.params['top_genes']).index
        expr_subset = expression_df.loc[top_genes]
        
        # Calculate correlation matrix
        corr_matrix = expr_subset.T.corr(method='pearson')
        
        # Create network from correlation matrix
        G = nx.Graph()
        threshold = self.params['correlation_threshold']
        
        for i in range(len(corr_matrix)):
            for j in range(i+1, len(corr_matrix)):
                if abs(corr_matrix.iloc[i, j]) > threshold:
                    G.add_edge(
                        corr_matrix.index[i], 
                        corr_matrix.index[j],
                        weight=abs(corr_matrix.iloc[i, j])
                    )
        
        # Calculate network statistics
        if G.number_of_nodes() > 0:
            results['network_stats'] = {
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'density': float(nx.density(G)),
                'clustering_coefficient': float(nx.average_clustering(G)) if G.number_of_edges() > 0 else 0
            }
            
            # Find hub genes (high degree centrality)
            if G.number_of_edges() > 0:
                degree_centrality = nx.degree_centrality(G)
                sorted_genes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
                
                results['hub_genes'] = [
                    {
                        'gene': gene,
                        'degree_centrality': float(centrality),
                        'degree': G.degree(gene)
                    }
                    for gene, centrality in sorted_genes[:10]
                ]
            
            # Detect communities/modules
            if G.number_of_edges() > 10:
                from networkx.algorithms import community
                communities = community.greedy_modularity_communities(G)
                
                results['modules'] = [
                    {
                        'module_id': f'M{i+1}',
                        'size': len(module),
                        'genes': list(module)[:10]  # Top 10 genes per module
                    }
                    for i, module in enumerate(communities) if len(module) >= 3
                ]
        
        # Create network visualization
        self._create_network_plot(G, corr_matrix)
        
        return results
    
    def pathway_enrichment_analysis(self, gene_list: List[str]) -> Dict:
        """
        Perform pathway enrichment analysis
        通路富集分析 - 简化版本
        """
        # Predefined pathways (in real implementation, use KEGG/GO databases)
        pathways = {
            'Cell Cycle': ['CCNA2', 'CCNB1', 'CCNE1', 'CDK1', 'CDK2', 'CDK4', 'CDKN1A', 'CDKN2A'],
            'Apoptosis': ['TP53', 'BCL2', 'BAX', 'CASP3', 'CASP8', 'CASP9', 'FAS', 'FADD'],
            'PI3K-Akt': ['PIK3CA', 'AKT1', 'PTEN', 'MTOR', 'TSC1', 'TSC2', 'FOXO1', 'FOXO3'],
            'p53 signaling': ['TP53', 'MDM2', 'CDKN1A', 'BAX', 'PUMA', 'NOXA', 'GADD45A'],
            'Wnt signaling': ['CTNNB1', 'APC', 'AXIN1', 'GSK3B', 'TCF7', 'LEF1', 'MYC'],
            'MAPK signaling': ['KRAS', 'BRAF', 'MAP2K1', 'MAPK1', 'MAPK3', 'JUN', 'FOS'],
            'DNA repair': ['BRCA1', 'BRCA2', 'ATM', 'ATR', 'RAD51', 'MLH1', 'MSH2'],
            'Metabolism': ['HK2', 'PKM', 'LDHA', 'G6PD', 'FASN', 'ACLY', 'SCD1']
        }
        
        results = {
            'method': 'pathway_enrichment',
            'enriched_pathways': []
        }
        
        # Convert gene list to uppercase for matching
        gene_set = set(g.upper() for g in gene_list)
        
        for pathway_name, pathway_genes in pathways.items():
            pathway_set = set(pathway_genes)
            overlap = gene_set.intersection(pathway_set)
            
            if len(overlap) > 0:
                # Fisher's exact test
                a = len(overlap)  # Genes in both
                b = len(gene_set) - a  # Genes only in query
                c = len(pathway_set) - a  # Genes only in pathway
                d = 20000 - a - b - c  # Approximate total genes
                
                odds_ratio, pvalue = stats.fisher_exact([[a, b], [c, d]])
                
                results['enriched_pathways'].append({
                    'pathway': pathway_name,
                    'overlap_genes': list(overlap),
                    'overlap_count': len(overlap),
                    'pathway_size': len(pathway_set),
                    'pvalue': float(pvalue),
                    'odds_ratio': float(odds_ratio)
                })
        
        # Sort by p-value
        results['enriched_pathways'] = sorted(
            results['enriched_pathways'], 
            key=lambda x: x['pvalue']
        )
        
        return results
    
    def machine_learning_prediction(self, expression_df: pd.DataFrame, 
                                  clinical_df: pd.DataFrame,
                                  target: str = 'os_status') -> Dict:
        """
        Build machine learning prediction model
        机器学习预测模型
        """
        results = {
            'method': 'machine_learning',
            'model': 'RandomForest',
            'target': target
        }
        
        # Prepare data
        common_samples = list(set(expression_df.columns) & set(clinical_df['sample_id']))
        if len(common_samples) < 20 or target not in clinical_df.columns:
            results['error'] = 'Insufficient data for modeling'
            return results
        
        # Align data
        X = expression_df[common_samples].T
        y = clinical_df[clinical_df['sample_id'].isin(common_samples)][target]
        
        # Remove NaN
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]
        
        if len(X) < 20:
            results['error'] = 'Too few samples after filtering'
            return results
        
        # Feature selection - top variable genes
        gene_variance = X.var()
        top_features = gene_variance.nlargest(min(50, len(gene_variance))).index
        X_selected = X[top_features]
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_selected)
        
        # Train model with cross-validation
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        cv_scores = cross_val_score(rf, X_scaled, y, cv=5, scoring='roc_auc')
        
        # Fit final model
        rf.fit(X_scaled, y)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'gene': top_features,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        results['performance'] = {
            'mean_auc': float(cv_scores.mean()),
            'std_auc': float(cv_scores.std()),
            'cv_scores': cv_scores.tolist()
        }
        
        results['top_features'] = [
            {
                'gene': row['gene'],
                'importance': float(row['importance'])
            }
            for _, row in feature_importance.head(20).iterrows()
        ]
        
        # Create feature importance plot
        self._create_feature_importance_plot(feature_importance.head(20))
        
        return results
    
    def molecular_subtyping(self, expression_df: pd.DataFrame) -> Dict:
        """
        Perform molecular subtyping using clustering
        分子亚型分类
        """
        results = {
            'method': 'molecular_subtyping',
            'algorithm': 'hierarchical_clustering'
        }
        
        # Select top variable genes
        gene_variance = expression_df.var(axis=1)
        top_genes = gene_variance.nlargest(min(500, len(gene_variance))).index
        expr_subset = expression_df.loc[top_genes]
        
        # Standardize data
        scaler = StandardScaler()
        expr_scaled = scaler.fit_transform(expr_subset.T)
        
        # Hierarchical clustering
        linkage_matrix = hierarchy.linkage(expr_scaled, method='ward')
        
        # Cut tree to get 3-5 clusters
        n_clusters = min(4, len(expression_df.columns) // 10)
        clusters = hierarchy.fcluster(linkage_matrix, n_clusters, criterion='maxclust')
        
        # Characterize each cluster
        cluster_info = []
        for i in range(1, n_clusters + 1):
            cluster_samples = [s for j, s in enumerate(expression_df.columns) if clusters[j] == i]
            
            # Find marker genes for this cluster
            if len(cluster_samples) >= 3:
                cluster_expr = expression_df[cluster_samples].mean(axis=1)
                other_expr = expression_df[[s for s in expression_df.columns if s not in cluster_samples]].mean(axis=1)
                
                fold_changes = cluster_expr / (other_expr + 1e-10)
                top_markers = fold_changes.nlargest(10)
                
                cluster_info.append({
                    'cluster_id': f'Subtype_{i}',
                    'n_samples': len(cluster_samples),
                    'samples': cluster_samples[:10],  # First 10 samples
                    'marker_genes': [
                        {
                            'gene': gene,
                            'fold_change': float(fc)
                        }
                        for gene, fc in top_markers.items()
                    ]
                })
        
        results['subtypes'] = cluster_info
        results['total_samples'] = len(expression_df.columns)
        
        # PCA visualization
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(expr_scaled)
        
        results['pca_variance_explained'] = {
            'PC1': float(pca.explained_variance_ratio_[0]),
            'PC2': float(pca.explained_variance_ratio_[1])
        }
        
        # Create clustering visualization
        self._create_clustering_plot(pca_result, clusters)
        
        return results
    
    # Visualization methods
    def _create_volcano_plot(self, genes: List[Dict]):
        """Create volcano plot for differential expression"""
        plt.figure(figsize=(10, 8))
        
        # Extract data
        log2_fc = [g['log2_fc'] for g in genes]
        neg_log10_p = [-np.log10(g['pvalue'] + 1e-10) for g in genes]
        significant = [g['significant'] for g in genes]
        
        # Create scatter plot
        colors = ['red' if sig else 'gray' for sig in significant]
        plt.scatter(log2_fc, neg_log10_p, c=colors, alpha=0.6)
        
        # Add threshold lines
        plt.axhline(y=-np.log10(self.params['pvalue_threshold']), color='b', linestyle='--', alpha=0.5)
        plt.axvline(x=np.log2(self.params['foldchange_threshold']), color='b', linestyle='--', alpha=0.5)
        plt.axvline(x=-np.log2(self.params['foldchange_threshold']), color='b', linestyle='--', alpha=0.5)
        
        plt.xlabel('Log2 Fold Change')
        plt.ylabel('-Log10 P-value')
        plt.title('Volcano Plot - Differential Expression Analysis')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'volcano_plot.png', dpi=150)
        plt.close()
    
    def _create_survival_plot(self, clinical_df: pd.DataFrame, gene: str = None, expression_df: pd.DataFrame = None):
        """Create Kaplan-Meier survival plot"""
        from lifelines import KaplanMeierFitter
        
        plt.figure(figsize=(10, 8))
        
        if gene and expression_df is not None and gene in expression_df.index:
            # Gene-based survival
            gene_expr = expression_df.loc[gene]
            median_expr = gene_expr.median()
            
            for label, condition in [('High', gene_expr >= median_expr), ('Low', gene_expr < median_expr)]:
                samples = gene_expr[condition].index
                subset = clinical_df[clinical_df['sample_id'].isin(samples)]
                
                if len(subset) > 0:
                    kmf = KaplanMeierFitter()
                    kmf.fit(subset['os_time'], subset['os_status'], label=f'{gene} {label}')
                    kmf.plot_survival_function()
        else:
            # Overall survival
            kmf = KaplanMeierFitter()
            kmf.fit(clinical_df['os_time'], clinical_df['os_status'], label='Overall')
            kmf.plot_survival_function()
        
        plt.xlabel('Time (days)')
        plt.ylabel('Survival Probability')
        plt.title('Kaplan-Meier Survival Analysis')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'survival_plot.png', dpi=150)
        plt.close()
    
    def _create_network_plot(self, G: nx.Graph, corr_matrix: pd.DataFrame):
        """Create network visualization"""
        plt.figure(figsize=(12, 10))
        
        if G.number_of_nodes() > 0:
            # Use spring layout
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # Draw nodes
            node_sizes = [G.degree(node) * 100 for node in G.nodes()]
            nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='lightblue', alpha=0.7)
            
            # Draw edges
            edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
            nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.5)
            
            # Draw labels for hub genes
            degree_dict = dict(G.degree())
            top_nodes = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)[:10]
            top_node_names = {node: node for node, _ in top_nodes}
            nx.draw_networkx_labels(G, pos, labels=top_node_names, font_size=10)
        
        plt.title('Gene Co-expression Network')
        plt.axis('off')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'network_plot.png', dpi=150)
        plt.close()
        
        # Also create correlation heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_matrix, cmap='RdBu_r', center=0, square=True)
        plt.title('Gene Correlation Heatmap')
        plt.tight_layout()
        plt.savefig(self.results_dir / 'correlation_heatmap.png', dpi=150)
        plt.close()
    
    def _create_feature_importance_plot(self, feature_importance: pd.DataFrame):
        """Create feature importance plot"""
        plt.figure(figsize=(10, 8))
        
        plt.barh(feature_importance['gene'], feature_importance['importance'])
        plt.xlabel('Importance Score')
        plt.ylabel('Gene')
        plt.title('Top 20 Important Features for Prediction')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'feature_importance.png', dpi=150)
        plt.close()
    
    def _create_clustering_plot(self, pca_result: np.ndarray, clusters: np.ndarray):
        """Create clustering visualization"""
        plt.figure(figsize=(10, 8))
        
        scatter = plt.scatter(pca_result[:, 0], pca_result[:, 1], c=clusters, cmap='viridis', alpha=0.6)
        plt.colorbar(scatter, label='Cluster')
        
        plt.xlabel('PC1')
        plt.ylabel('PC2')
        plt.title('Molecular Subtyping - PCA Visualization')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'clustering_plot.png', dpi=150)
        plt.close()
    
    def run_comprehensive_analysis(self, modules: List[str]) -> Dict:
        """
        Run comprehensive analysis pipeline
        运行完整的分析流程
        """
        # Initialize progress
        if self.progress_manager:
            self.progress_manager.start_analysis(modules)
        
        try:
            # Load data
            data = self.load_user_data()
            if not data:
                if self.progress_manager:
                    self.progress_manager.fail_analysis("No data found")
                return {'error': 'No data found'}
            
            all_results = {
                'session_id': self.session_id,
                'timestamp': pd.Timestamp.now().isoformat(),
                'analyses': {}
            }
        
            # 1. Differential Expression Analysis
            if 'differential_expression' in modules and 'expression' in data and 'clinical' in data:
                print("Running differential expression analysis...")
                
                if self.progress_manager:
                    with ProgressUpdater(self.progress_manager, 'differential_expression', 100) as progress:
                        progress.update(10, "Loading expression data...")
                        de_results = self.differential_expression_analysis(
                            data['expression'], 
                            data['clinical']
                        )
                        progress.update(90, "Saving results...")
                        all_results['analyses']['differential_expression'] = de_results
                        
                        # Save significant genes
                        sig_genes = [g for g in de_results['genes'] if g['significant']]
                        with open(self.results_dir / 'significant_genes.json', 'w') as f:
                            json.dump(sig_genes[:100], f, indent=2)
                        progress.update(100, "Differential expression analysis completed")
                else:
                    de_results = self.differential_expression_analysis(
                        data['expression'], 
                        data['clinical']
                    )
                    all_results['analyses']['differential_expression'] = de_results
                    
                    # Save significant genes
                    sig_genes = [g for g in de_results['genes'] if g['significant']]
                    with open(self.results_dir / 'significant_genes.json', 'w') as f:
                        json.dump(sig_genes[:100], f, indent=2)
            
            # 2. Survival Analysis
            if 'survival' in modules and 'clinical' in data:
                print("Running survival analysis...")
                # Overall survival
                surv_results = self.survival_analysis(data['clinical'])
                
                # Gene-based survival for top DE genes
                if 'expression' in data and 'differential_expression' in all_results['analyses']:
                    top_genes = all_results['analyses']['differential_expression']['genes'][:5]
                    for gene_info in top_genes:
                        gene = gene_info['gene']
                        if gene in data['expression'].index:
                            gene_surv = self.survival_analysis(
                                data['clinical'], 
                                data['expression'], 
                                gene
                            )
                            surv_results[f'gene_{gene}'] = gene_surv.get('gene_survival', {})
                
                all_results['analyses']['survival'] = surv_results
            
            # 3. Network Analysis
            if 'network' in modules and 'expression' in data:
                print("Running network analysis...")
                network_results = self.network_analysis(data['expression'])
                all_results['analyses']['network'] = network_results
            
            # 4. Pathway Enrichment
            if 'pathway' in modules and 'differential_expression' in all_results['analyses']:
                print("Running pathway enrichment analysis...")
                sig_genes = [g['gene'] for g in all_results['analyses']['differential_expression']['genes'] 
                            if g['significant']][:100]
                pathway_results = self.pathway_enrichment_analysis(sig_genes)
                all_results['analyses']['pathway'] = pathway_results
            
            # 5. Machine Learning Prediction
            if 'machine_learning' in modules and 'expression' in data and 'clinical' in data:
                print("Running machine learning prediction...")
                ml_results = self.machine_learning_prediction(
                    data['expression'], 
                    data['clinical']
                )
                all_results['analyses']['machine_learning'] = ml_results
            
            # 6. Molecular Subtyping
            if 'subtyping' in modules and 'expression' in data:
                print("Running molecular subtyping...")
                subtype_results = self.molecular_subtyping(data['expression'])
                all_results['analyses']['subtyping'] = subtype_results
            
            # Generate comprehensive report
            if self.progress_manager:
                self.progress_manager.add_log("Generating comprehensive report...")
            self.generate_comprehensive_report(all_results)
            
            # Save all results
            with open(self.results_dir / 'comprehensive_results.json', 'w') as f:
                json.dump(all_results, f, indent=2, default=str)
            
            if self.progress_manager:
                self.progress_manager.complete_analysis()
            
            return all_results
            
        except Exception as e:
            if self.progress_manager:
                self.progress_manager.fail_analysis(str(e))
            raise
    
    def load_user_data(self) -> Dict:
        """Load user uploaded data"""
        data = {}
        
        # Load clinical data
        clinical_file = self.data_dir / "clinical_data.csv"
        if clinical_file.exists():
            data['clinical'] = pd.read_csv(clinical_file)
            # Ensure sample_id column exists
            if 'sample_id' not in data['clinical'].columns:
                data['clinical']['sample_id'] = data['clinical'].index.astype(str)
        
        # Load expression data
        expression_file = self.data_dir / "expression_data.csv"
        if expression_file.exists():
            data['expression'] = pd.read_csv(expression_file, index_col=0)
        
        # Load mutation data
        mutation_file = self.data_dir / "mutation_data.csv"
        if mutation_file.exists():
            data['mutations'] = pd.read_csv(mutation_file)
        
        return data
    
    def generate_comprehensive_report(self, results: Dict):
        """Generate comprehensive HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Comprehensive LIHC Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                h3 {{ color: #7f8c8d; }}
                .summary-box {{ 
                    background: #ecf0f1; 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin: 20px 0;
                    border-left: 5px solid #3498db;
                }}
                .result-section {{ 
                    background: #f8f9fa; 
                    padding: 20px; 
                    margin: 20px 0;
                    border-radius: 8px;
                }}
                table {{ 
                    border-collapse: collapse; 
                    width: 100%; 
                    margin: 20px 0;
                }}
                th, td {{ 
                    border: 1px solid #ddd; 
                    padding: 12px; 
                    text-align: left; 
                }}
                th {{ 
                    background-color: #3498db; 
                    color: white; 
                }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .metric {{ 
                    font-size: 24px; 
                    color: #2c3e50; 
                    font-weight: bold; 
                }}
                .significant {{ color: #e74c3c; font-weight: bold; }}
                img {{ 
                    max-width: 100%; 
                    height: auto; 
                    margin: 20px 0;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <h1>🧬 Comprehensive LIHC Analysis Report</h1>
            <div class="summary-box">
                <p><strong>Session ID:</strong> {results['session_id']}</p>
                <p><strong>Analysis Date:</strong> {results['timestamp']}</p>
                <p><strong>Modules Completed:</strong> {', '.join(results['analyses'].keys())}</p>
            </div>
        """
        
        # Add analysis results
        for analysis_name, analysis_results in results['analyses'].items():
            html_content += f"""
            <div class="result-section">
                <h2>{analysis_name.replace('_', ' ').title()}</h2>
            """
            
            if analysis_name == 'differential_expression':
                sig_genes = [g for g in analysis_results.get('genes', []) if g.get('significant')][:20]
                html_content += f"""
                <p>Total genes analyzed: <span class="metric">{len(analysis_results.get('genes', []))}</span></p>
                <p>Significant genes: <span class="metric significant">{len(sig_genes)}</span></p>
                
                <h3>Top 20 Differentially Expressed Genes</h3>
                <table>
                    <tr>
                        <th>Gene</th>
                        <th>Log2 FC</th>
                        <th>P-value</th>
                        <th>Adjusted P-value</th>
                    </tr>
                """
                for gene in sig_genes:
                    html_content += f"""
                    <tr>
                        <td>{gene['gene']}</td>
                        <td>{gene['log2_fc']:.3f}</td>
                        <td>{gene['pvalue']:.2e}</td>
                        <td>{gene['adjusted_pvalue']:.2e}</td>
                    </tr>
                    """
                html_content += "</table>"
                
                # Add volcano plot
                if (self.results_dir / 'volcano_plot.png').exists():
                    html_content += '<img src="volcano_plot.png" alt="Volcano Plot">'
            
            elif analysis_name == 'survival':
                overall = analysis_results.get('overall_survival', {})
                html_content += f"""
                <p>Total patients: <span class="metric">{overall.get('total_patients', 'N/A')}</span></p>
                <p>Events: <span class="metric">{overall.get('events', 'N/A')}</span></p>
                <p>Median survival: <span class="metric">{overall.get('median_survival_days', 'N/A'):.0f}</span> days</p>
                """
                
                # Add survival plot
                if (self.results_dir / 'survival_plot.png').exists():
                    html_content += '<img src="survival_plot.png" alt="Survival Plot">'
            
            elif analysis_name == 'network':
                stats = analysis_results.get('network_stats', {})
                html_content += f"""
                <p>Network nodes: <span class="metric">{stats.get('nodes', 0)}</span></p>
                <p>Network edges: <span class="metric">{stats.get('edges', 0)}</span></p>
                <p>Network density: <span class="metric">{stats.get('density', 0):.3f}</span></p>
                
                <h3>Top 10 Hub Genes</h3>
                <table>
                    <tr>
                        <th>Gene</th>
                        <th>Degree Centrality</th>
                        <th>Degree</th>
                    </tr>
                """
                for hub in analysis_results.get('hub_genes', [])[:10]:
                    html_content += f"""
                    <tr>
                        <td>{hub['gene']}</td>
                        <td>{hub['degree_centrality']:.3f}</td>
                        <td>{hub['degree']}</td>
                    </tr>
                    """
                html_content += "</table>"
                
                # Add network plots
                if (self.results_dir / 'network_plot.png').exists():
                    html_content += '<img src="network_plot.png" alt="Network Plot">'
                if (self.results_dir / 'correlation_heatmap.png').exists():
                    html_content += '<img src="correlation_heatmap.png" alt="Correlation Heatmap">'
            
            elif analysis_name == 'machine_learning':
                perf = analysis_results.get('performance', {})
                html_content += f"""
                <p>Model: <span class="metric">{analysis_results.get('model', 'N/A')}</span></p>
                <p>Mean AUC: <span class="metric">{perf.get('mean_auc', 0):.3f}</span></p>
                <p>Std AUC: <span class="metric">{perf.get('std_auc', 0):.3f}</span></p>
                
                <h3>Top 10 Predictive Features</h3>
                <table>
                    <tr>
                        <th>Gene</th>
                        <th>Importance</th>
                    </tr>
                """
                for feat in analysis_results.get('top_features', [])[:10]:
                    html_content += f"""
                    <tr>
                        <td>{feat['gene']}</td>
                        <td>{feat['importance']:.4f}</td>
                    </tr>
                    """
                html_content += "</table>"
                
                # Add feature importance plot
                if (self.results_dir / 'feature_importance.png').exists():
                    html_content += '<img src="feature_importance.png" alt="Feature Importance">'
            
            html_content += "</div>"
        
        html_content += """
        </body>
        </html>
        """
        
        # Save report
        with open(self.results_dir / 'comprehensive_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)