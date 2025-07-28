"""
Single Cell Analysis Module for LIHC Platform
单细胞RNA测序数据分析模块，专注于肿瘤微环境解析
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class SingleCellAnalyzer:
    """单细胞RNA测序分析器"""
    
    def __init__(self):
        self.cell_types = [
            'Hepatocytes', 'Cholangiocytes', 'Kupffer_cells', 'Stellate_cells',
            'CD8_T_cells', 'CD4_T_cells', 'NK_cells', 'B_cells', 'Macrophages',
            'Neutrophils', 'Dendritic_cells', 'Endothelial_cells', 'Fibroblasts',
            'Cancer_cells', 'CAFs', 'TAMs'
        ]
        
        self.marker_genes = {
            'Hepatocytes': ['ALB', 'AFP', 'CYP3A4', 'G6PC'],
            'Cholangiocytes': ['KRT7', 'KRT19', 'EPCAM', 'SOX9'],
            'Kupffer_cells': ['CD68', 'CLEC4F', 'VSIG4', 'TIMD4'],
            'Stellate_cells': ['ACTA2', 'COL1A1', 'PDGFRB', 'VIM'],
            'CD8_T_cells': ['CD8A', 'CD8B', 'GZMB', 'PRF1'],
            'CD4_T_cells': ['CD4', 'IL2', 'CD40LG', 'FOXP3'],
            'NK_cells': ['KLRD1', 'NCAM1', 'NKG7', 'GNLY'],
            'B_cells': ['CD19', 'MS4A1', 'CD79A', 'IGHM'],
            'Macrophages': ['CD68', 'CD163', 'ARG1', 'IL10'],
            'Neutrophils': ['FCGR3B', 'CSF3R', 'CXCR2', 'S100A8'],
            'Dendritic_cells': ['CD1C', 'FCER1A', 'CLEC9A', 'IRF8'],
            'Endothelial_cells': ['PECAM1', 'VWF', 'CDH5', 'PLVAP'],
            'Fibroblasts': ['COL1A1', 'COL3A1', 'DCN', 'LUM'],
            'Cancer_cells': ['EPCAM', 'KRT18', 'MKI67', 'PCNA'],
            'CAFs': ['ACTA2', 'FAP', 'PDPN', 'POSTN'],
            'TAMs': ['CD68', 'CD163', 'ARG1', 'IL10']
        }
        
    def generate_single_cell_data(self, n_cells: int = 5000, n_genes: int = 2000) -> Dict:
        """生成模拟单细胞数据"""
        np.random.seed(42)
        
        # 细胞类型分配 
        raw_props = [0.25, 0.15, 0.08, 0.05, 0.12, 0.08, 0.05, 0.04, 
                    0.06, 0.02, 0.03, 0.04, 0.03, 0.03, 0.02, 0.01]
        # 归一化确保总和严格等于1
        cell_type_props = np.array(raw_props) / np.sum(raw_props)
        
        cell_assignments = np.random.choice(
            self.cell_types, 
            size=n_cells, 
            p=cell_type_props
        )
        
        # 基因表达矩阵
        gene_names = [f"ENSG{i:05d}" for i in range(n_genes)]
        
        # 添加marker基因
        all_markers = []
        for markers in self.marker_genes.values():
            all_markers.extend(markers)
        unique_markers = list(set(all_markers))
        
        # 替换前面的基因名
        gene_names[:len(unique_markers)] = unique_markers
        
        # 生成表达矩阵
        expression_matrix = np.random.poisson(2, (n_genes, n_cells)).astype(float)
        
        # 为每种细胞类型的marker基因增加表达
        for i, cell_type in enumerate(cell_assignments):
            markers = self.marker_genes.get(cell_type, [])
            for marker in markers:
                if marker in gene_names:
                    gene_idx = gene_names.index(marker)
                    expression_matrix[gene_idx, i] += np.random.poisson(10)
        
        # 添加噪声和dropout
        dropout_rate = 0.6
        dropout_mask = np.random.random((n_genes, n_cells)) < dropout_rate
        expression_matrix[dropout_mask] = 0
        
        # 转换为DataFrame
        expression_df = pd.DataFrame(
            expression_matrix,
            index=gene_names,
            columns=[f"Cell_{i:04d}" for i in range(n_cells)]
        )
        
        # 细胞metadata
        cell_metadata = pd.DataFrame({
            'cell_id': expression_df.columns,
            'cell_type': cell_assignments,
            'nUMI': expression_df.sum(axis=0),
            'nGenes': (expression_df > 0).sum(axis=0),
            'percent_mito': np.random.uniform(0.05, 0.25, n_cells),
            'phase': np.random.choice(['G1', 'S', 'G2M'], n_cells),
            'sample': np.random.choice(['Normal', 'Tumor'], n_cells, p=[0.3, 0.7])
        })
        
        return {
            'expression': expression_df,
            'metadata': cell_metadata,
            'genes': gene_names,
            'marker_genes': self.marker_genes
        }
    
    def perform_quality_control(self, data: Dict) -> Dict:
        """质量控制分析"""
        metadata = data['metadata'].copy()
        
        # QC metrics
        qc_metrics = {
            'total_cells': len(metadata),
            'median_genes_per_cell': metadata['nGenes'].median(),
            'median_umi_per_cell': metadata['nUMI'].median(),
            'high_mito_cells': (metadata['percent_mito'] > 0.2).sum(),
            'low_gene_cells': (metadata['nGenes'] < 200).sum()
        }
        
        # 过滤低质量细胞
        high_quality_cells = (
            (metadata['nGenes'] >= 200) & 
            (metadata['nGenes'] <= 5000) &
            (metadata['percent_mito'] <= 0.2)
        )
        
        filtered_metadata = metadata[high_quality_cells].copy()
        filtered_expression = data['expression'].loc[:, high_quality_cells]
        
        return {
            'qc_metrics': qc_metrics,
            'filtered_metadata': filtered_metadata,
            'filtered_expression': filtered_expression,
            'filter_summary': {
                'cells_before': len(metadata),
                'cells_after': len(filtered_metadata),
                'filter_rate': 1 - len(filtered_metadata) / len(metadata)
            }
        }
    
    def perform_dimensionality_reduction(self, expression_df: pd.DataFrame) -> Dict:
        """降维分析 (PCA + UMAP模拟)"""
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        
        # 基因筛选 - 选择高变基因
        gene_var = expression_df.var(axis=1)
        top_genes = gene_var.nlargest(2000).index
        hvg_expression = expression_df.loc[top_genes]
        
        # 标准化
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(hvg_expression.T)
        
        # PCA
        pca = PCA(n_components=50)
        pca_result = pca.fit_transform(scaled_data)
        
        # 模拟UMAP (使用PCA的前2个成分加噪声)
        umap_result = pca_result[:, :2] + np.random.normal(0, 0.5, (pca_result.shape[0], 2))
        
        return {
            'pca_result': pca_result,
            'umap_result': umap_result,
            'pca_variance_ratio': pca.explained_variance_ratio_,
            'top_genes': top_genes.tolist()
        }
    
    def perform_cell_clustering(self, umap_result: np.ndarray, metadata: pd.DataFrame) -> Dict:
        """细胞聚类分析"""
        from sklearn.cluster import KMeans
        
        # K-means聚类
        n_clusters = 12
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(umap_result)
        
        # 将聚类结果添加到metadata
        metadata_with_clusters = metadata.copy()
        metadata_with_clusters['cluster'] = cluster_labels
        
        # 计算聚类统计
        cluster_stats = []
        for cluster_id in range(n_clusters):
            cluster_cells = metadata_with_clusters[metadata_with_clusters['cluster'] == cluster_id]
            cluster_stats.append({
                'cluster': cluster_id,
                'n_cells': len(cluster_cells),
                'dominant_cell_type': cluster_cells['cell_type'].mode().iloc[0],
                'cell_type_diversity': len(cluster_cells['cell_type'].unique()),
                'avg_umi': cluster_cells['nUMI'].mean(),
                'avg_genes': cluster_cells['nGenes'].mean()
            })
        
        cluster_df = pd.DataFrame(cluster_stats)
        
        return {
            'cluster_labels': cluster_labels,
            'metadata_with_clusters': metadata_with_clusters,
            'cluster_stats': cluster_df,
            'n_clusters': n_clusters
        }
    
    def perform_differential_expression(self, expression_df: pd.DataFrame, 
                                      metadata: pd.DataFrame, 
                                      group_by: str = 'cell_type') -> Dict:
        """差异表达分析"""
        
        de_results = {}
        unique_groups = metadata[group_by].unique()
        
        for group in unique_groups:
            group_cells = metadata[metadata[group_by] == group].index
            other_cells = metadata[metadata[group_by] != group].index
            
            if len(group_cells) < 10 or len(other_cells) < 10:
                continue
                
            # 简化的差异表达分析
            group_expr = expression_df[group_cells].mean(axis=1)
            other_expr = expression_df[other_cells].mean(axis=1)
            
            # 计算log2 fold change
            log2fc = np.log2((group_expr + 1) / (other_expr + 1))
            
            # 模拟p值
            np.random.seed(42)
            p_values = np.random.uniform(0.001, 0.5, len(expression_df))
            
            # 创建结果DataFrame
            de_df = pd.DataFrame({
                'gene': expression_df.index,
                'log2fc': log2fc,
                'p_value': p_values,
                'group_mean': group_expr,
                'other_mean': other_expr,
                'pct_in_group': (expression_df[group_cells] > 0).mean(axis=1),
                'pct_in_other': (expression_df[other_cells] > 0).mean(axis=1)
            })
            
            # 筛选显著基因
            de_df['significant'] = (abs(de_df['log2fc']) > 1) & (de_df['p_value'] < 0.05)
            de_df = de_df.sort_values('p_value')
            
            de_results[group] = de_df
        
        return de_results
    
    def analyze_cell_communication(self, expression_df: pd.DataFrame, 
                                 metadata: pd.DataFrame) -> Dict:
        """细胞通讯分析"""
        
        # 预定义配体-受体对
        ligand_receptor_pairs = [
            ('TNF', 'TNFRSF1A'), ('IL6', 'IL6R'), ('PDGFA', 'PDGFRA'),
            ('VEGFA', 'FLT1'), ('CCL2', 'CCR2'), ('CXCL12', 'CXCR4'),
            ('TGFB1', 'TGFBR1'), ('IFNG', 'IFNGR1'), ('IL10', 'IL10RA'),
            ('CSF1', 'CSF1R'), ('EGF', 'EGFR'), ('FGF2', 'FGFR1')
        ]
        
        communication_matrix = []
        cell_types = metadata['cell_type'].unique()
        
        for sender in cell_types:
            sender_cells = metadata[metadata['cell_type'] == sender].index
            if len(sender_cells) == 0:
                continue
                
            for receiver in cell_types:
                receiver_cells = metadata[metadata['cell_type'] == receiver].index
                if len(receiver_cells) == 0:
                    continue
                
                communication_score = 0
                valid_pairs = 0
                
                for ligand, receptor in ligand_receptor_pairs:
                    if ligand in expression_df.index and receptor in expression_df.index:
                        ligand_expr = expression_df.loc[ligand, sender_cells].mean()
                        receptor_expr = expression_df.loc[receptor, receiver_cells].mean()
                        
                        # 计算通讯强度
                        pair_score = np.sqrt(ligand_expr * receptor_expr)
                        communication_score += pair_score
                        valid_pairs += 1
                
                if valid_pairs > 0:
                    communication_score /= valid_pairs
                
                communication_matrix.append({
                    'sender': sender,
                    'receiver': receiver,
                    'communication_score': communication_score,
                    'valid_pairs': valid_pairs
                })
        
        comm_df = pd.DataFrame(communication_matrix)
        
        # 创建通讯矩阵
        comm_pivot = comm_df.pivot(index='sender', columns='receiver', values='communication_score')
        comm_pivot = comm_pivot.fillna(0)
        
        return {
            'communication_matrix': comm_df,
            'communication_pivot': comm_pivot,
            'ligand_receptor_pairs': ligand_receptor_pairs
        }
    
    def create_qc_plots(self, qc_data: Dict) -> go.Figure:
        """创建质量控制图表"""
        
        metadata = qc_data['filtered_metadata']
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('UMI Distribution', 'Gene Distribution', 
                          'Mitochondrial %', 'UMI vs Genes'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # UMI分布
        fig.add_trace(
            go.Histogram(x=metadata['nUMI'], name='UMI', nbinsx=50, 
                        marker_color='lightblue'),
            row=1, col=1
        )
        
        # 基因分布
        fig.add_trace(
            go.Histogram(x=metadata['nGenes'], name='Genes', nbinsx=50,
                        marker_color='lightgreen'),
            row=1, col=2
        )
        
        # 线粒体百分比
        fig.add_trace(
            go.Histogram(x=metadata['percent_mito'], name='Mito %', nbinsx=50,
                        marker_color='lightcoral'),
            row=2, col=1
        )
        
        # UMI vs Genes散点图
        fig.add_trace(
            go.Scatter(x=metadata['nUMI'], y=metadata['nGenes'], 
                      mode='markers', name='Cells',
                      marker=dict(size=3, opacity=0.6)),
            row=2, col=2
        )
        
        fig.update_layout(
            title='Single Cell QC Metrics',
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_umap_plot(self, umap_result: np.ndarray, metadata: pd.DataFrame, 
                        color_by: str = 'cell_type') -> go.Figure:
        """创建UMAP降维图"""
        
        fig = go.Figure()
        
        unique_values = metadata[color_by].unique()
        colors = px.colors.qualitative.Set3[:len(unique_values)]
        
        for i, value in enumerate(unique_values):
            mask = metadata[color_by] == value
            indices = np.where(mask)[0]
            
            fig.add_trace(go.Scatter(
                x=umap_result[indices, 0],
                y=umap_result[indices, 1],
                mode='markers',
                name=str(value),
                marker=dict(
                    size=4,
                    color=colors[i % len(colors)],
                    opacity=0.7
                ),
                hovertemplate=f'{color_by}: {value}<br>UMAP1: %{{x}}<br>UMAP2: %{{y}}<extra></extra>'
            ))
        
        fig.update_layout(
            title=f'UMAP Visualization (colored by {color_by})',
            xaxis_title='UMAP1',
            yaxis_title='UMAP2',
            height=600,
            template='plotly_white'
        )
        
        return fig
    
    def create_cell_communication_plot(self, comm_data: Dict) -> go.Figure:
        """创建细胞通讯热图"""
        
        comm_matrix = comm_data['communication_pivot']
        
        fig = go.Figure(data=go.Heatmap(
            z=comm_matrix.values,
            x=comm_matrix.columns,
            y=comm_matrix.index,
            colorscale='Viridis',
            colorbar=dict(title='Communication Score')
        ))
        
        fig.update_layout(
            title='Cell-Cell Communication Matrix',
            xaxis_title='Receiver Cell Type',
            yaxis_title='Sender Cell Type',
            height=500
        )
        
        return fig
    
    def create_marker_expression_plot(self, expression_df: pd.DataFrame, 
                                    metadata: pd.DataFrame,
                                    cell_type: str) -> go.Figure:
        """创建marker基因表达图"""
        
        if cell_type not in self.marker_genes:
            return go.Figure()
        
        markers = self.marker_genes[cell_type]
        available_markers = [gene for gene in markers if gene in expression_df.index]
        
        if not available_markers:
            return go.Figure()
        
        fig = go.Figure()
        
        cell_type_cells = metadata[metadata['cell_type'] == cell_type].index
        other_cells = metadata[metadata['cell_type'] != cell_type].index
        
        for marker in available_markers:
            cell_type_expr = expression_df.loc[marker, cell_type_cells]
            other_expr = expression_df.loc[marker, other_cells]
            
            fig.add_trace(go.Box(
                y=cell_type_expr,
                name=f'{marker} ({cell_type})',
                boxpoints='outliers'
            ))
            
            fig.add_trace(go.Box(
                y=other_expr,
                name=f'{marker} (Others)',
                boxpoints='outliers'
            ))
        
        fig.update_layout(
            title=f'Marker Gene Expression: {cell_type}',
            yaxis_title='Expression Level',
            height=400,
            template='plotly_white'
        )
        
        return fig


def run_single_cell_analysis_demo():
    """运行单细胞分析演示"""
    
    analyzer = SingleCellAnalyzer()
    
    print("Generating single cell data...")
    sc_data = analyzer.generate_single_cell_data(n_cells=3000, n_genes=1500)
    
    print("Performing quality control...")
    qc_data = analyzer.perform_quality_control(sc_data)
    
    print("Performing dimensionality reduction...")
    dim_red_data = analyzer.perform_dimensionality_reduction(qc_data['filtered_expression'])
    
    print("Performing cell clustering...")
    cluster_data = analyzer.perform_cell_clustering(
        dim_red_data['umap_result'], 
        qc_data['filtered_metadata']
    )
    
    print("Analyzing differential expression...")
    de_results = analyzer.perform_differential_expression(
        qc_data['filtered_expression'],
        cluster_data['metadata_with_clusters']
    )
    
    print("Analyzing cell communication...")
    comm_data = analyzer.analyze_cell_communication(
        qc_data['filtered_expression'],
        cluster_data['metadata_with_clusters']
    )
    
    # 创建可视化
    print("Creating visualizations...")
    qc_plot = analyzer.create_qc_plots(qc_data)
    umap_plot = analyzer.create_umap_plot(
        dim_red_data['umap_result'],
        cluster_data['metadata_with_clusters'],
        'cell_type'
    )
    comm_plot = analyzer.create_cell_communication_plot(comm_data)
    
    results = {
        'sc_data': sc_data,
        'qc_data': qc_data,
        'dimensionality_reduction': dim_red_data,
        'clustering': cluster_data,
        'differential_expression': de_results,
        'cell_communication': comm_data,
        'plots': {
            'qc_plot': qc_plot,
            'umap_plot': umap_plot,
            'communication_plot': comm_plot
        }
    }
    
    print(f"Analysis completed!")
    print(f"Total cells analyzed: {len(qc_data['filtered_metadata'])}")
    print(f"Cell types identified: {len(cluster_data['metadata_with_clusters']['cell_type'].unique())}")
    print(f"Clusters found: {cluster_data['n_clusters']}")
    
    return results


if __name__ == "__main__":
    results = run_single_cell_analysis_demo()