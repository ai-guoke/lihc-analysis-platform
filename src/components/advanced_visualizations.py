"""
Advanced 3D Visualization Components
高级3D可视化组件 - 提供尖端的三维数据可视化能力
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import json
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import networkx as nx
from dash import dcc, html

class Advanced3DVisualizer:
    """高级3D可视化器"""
    
    def __init__(self):
        self.color_palettes = {
            'expression': ['#053061', '#2166ac', '#4393c3', '#92c5de', '#d1e5f0', 
                          '#fddbc7', '#f4a582', '#d6604d', '#b2182b', '#67001f'],
            'clinical': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            'immune': ['#e31a1c', '#fb9a99', '#33a02c', '#b2df8a', '#1f78b4'],
            'pathway': ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3']
        }
    
    def create_3d_pca_plot(self, expression_df: pd.DataFrame, clinical_df: pd.DataFrame = None,
                          color_by: str = None, title: str = "3D PCA 主成分分析") -> go.Figure:
        """创建3D PCA可视化"""
        
        # 数据预处理
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(expression_df.T)  # 转置，样本为行
        
        # PCA降维到3D
        pca = PCA(n_components=3)
        pca_result = pca.fit_transform(scaled_data)
        
        # 准备绘图数据
        plot_df = pd.DataFrame({
            'PC1': pca_result[:, 0],
            'PC2': pca_result[:, 1], 
            'PC3': pca_result[:, 2],
            'Sample': expression_df.columns
        })
        
        # 添加颜色分组
        color_column = None
        if clinical_df is not None and color_by and color_by in clinical_df.columns:
            # 匹配样本
            matched_clinical = clinical_df.set_index('sample_id').reindex(plot_df['Sample'])
            plot_df['Color_Group'] = matched_clinical[color_by].values
            color_column = 'Color_Group'
        
        # 创建3D散点图
        fig = go.Figure()
        
        if color_column and not plot_df[color_column].isna().all():
            # 按组分色
            unique_groups = plot_df[color_column].dropna().unique()
            colors = self.color_palettes['clinical'][:len(unique_groups)]
            
            for i, group in enumerate(unique_groups):
                group_data = plot_df[plot_df[color_column] == group]
                
                fig.add_trace(go.Scatter3d(
                    x=group_data['PC1'],
                    y=group_data['PC2'],
                    z=group_data['PC3'],
                    mode='markers',
                    name=str(group),
                    marker=dict(
                        size=8,
                        color=colors[i % len(colors)],
                        opacity=0.8,
                        line=dict(width=1, color='white')
                    ),
                    text=group_data['Sample'],
                    hovertemplate='<b>%{text}</b><br>' +
                                 f'PC1: %{{x:.2f}}<br>' +
                                 f'PC2: %{{y:.2f}}<br>' +
                                 f'PC3: %{{z:.2f}}<br>' +
                                 f'{color_by}: {group}<extra></extra>'
                ))
        else:
            # 单色显示
            fig.add_trace(go.Scatter3d(
                x=plot_df['PC1'],
                y=plot_df['PC2'],
                z=plot_df['PC3'],
                mode='markers',
                name='Samples',
                marker=dict(
                    size=8,
                    color='#1f77b4',
                    opacity=0.8,
                    line=dict(width=1, color='white')
                ),
                text=plot_df['Sample'],
                hovertemplate='<b>%{text}</b><br>' +
                             'PC1: %{x:.2f}<br>' +
                             'PC2: %{y:.2f}<br>' +
                             'PC3: %{z:.2f}<extra></extra>'
            ))
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text=f"{title}<br><sub>PC1: {pca.explained_variance_ratio_[0]:.1%}, "
                     f"PC2: {pca.explained_variance_ratio_[1]:.1%}, "
                     f"PC3: {pca.explained_variance_ratio_[2]:.1%} 方差解释</sub>",
                x=0.5
            ),
            scene=dict(
                xaxis_title=f'PC1 ({pca.explained_variance_ratio_[0]:.1%})',
                yaxis_title=f'PC2 ({pca.explained_variance_ratio_[1]:.1%})',
                zaxis_title=f'PC3 ({pca.explained_variance_ratio_[2]:.1%})',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5),
                    center=dict(x=0, y=0, z=0)
                ),
                bgcolor='rgba(240,240,240,0.1)',
                xaxis=dict(backgroundcolor="white", gridcolor="lightgray"),
                yaxis=dict(backgroundcolor="white", gridcolor="lightgray"),
                zaxis=dict(backgroundcolor="white", gridcolor="lightgray")
            ),
            height=600,
            margin=dict(l=0, r=0, t=50, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_3d_tsne_plot(self, expression_df: pd.DataFrame, clinical_df: pd.DataFrame = None,
                           color_by: str = None, perplexity: int = 30, 
                           title: str = "3D t-SNE 降维可视化") -> go.Figure:
        """创建3D t-SNE可视化"""
        
        # 数据预处理
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(expression_df.T)
        
        # t-SNE降维
        tsne = TSNE(n_components=3, perplexity=perplexity, random_state=42, 
                   n_iter=1000, learning_rate='auto', init='random')
        tsne_result = tsne.fit_transform(scaled_data)
        
        # 准备数据
        plot_df = pd.DataFrame({
            'tSNE1': tsne_result[:, 0],
            'tSNE2': tsne_result[:, 1],
            'tSNE3': tsne_result[:, 2],
            'Sample': expression_df.columns
        })
        
        # 添加颜色分组
        color_column = None
        if clinical_df is not None and color_by and color_by in clinical_df.columns:
            matched_clinical = clinical_df.set_index('sample_id').reindex(plot_df['Sample'])
            plot_df['Color_Group'] = matched_clinical[color_by].values
            color_column = 'Color_Group'
        
        # 创建3D散点图
        fig = go.Figure()
        
        if color_column and not plot_df[color_column].isna().all():
            unique_groups = plot_df[color_column].dropna().unique()
            colors = self.color_palettes['clinical'][:len(unique_groups)]
            
            for i, group in enumerate(unique_groups):
                group_data = plot_df[plot_df[color_column] == group]
                
                fig.add_trace(go.Scatter3d(
                    x=group_data['tSNE1'],
                    y=group_data['tSNE2'],
                    z=group_data['tSNE3'],
                    mode='markers',
                    name=str(group),
                    marker=dict(
                        size=10,
                        color=colors[i % len(colors)],
                        opacity=0.8,
                        line=dict(width=2, color='white')
                    ),
                    text=group_data['Sample'],
                    hovertemplate=f'<b>%{{text}}</b><br>' +
                                 f'tSNE1: %{{x:.2f}}<br>' +
                                 f'tSNE2: %{{y:.2f}}<br>' +
                                 f'tSNE3: %{{z:.2f}}<br>' +
                                 f'{color_by}: {group}<extra></extra>'
                ))
        else:
            fig.add_trace(go.Scatter3d(
                x=plot_df['tSNE1'],
                y=plot_df['tSNE2'],
                z=plot_df['tSNE3'],
                mode='markers',
                name='Samples',
                marker=dict(
                    size=10,
                    color='#ff7f0e',
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                text=plot_df['Sample'],
                hovertemplate='<b>%{text}</b><br>' +
                             'tSNE1: %{x:.2f}<br>' +
                             'tSNE2: %{y:.2f}<br>' +
                             'tSNE3: %{z:.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            title=dict(
                text=f"{title}<br><sub>Perplexity: {perplexity}, 3D 非线性降维</sub>",
                x=0.5
            ),
            scene=dict(
                xaxis_title='t-SNE 维度 1',
                yaxis_title='t-SNE 维度 2',
                zaxis_title='t-SNE 维度 3',
                camera=dict(
                    eye=dict(x=1.8, y=1.8, z=1.8),
                    center=dict(x=0, y=0, z=0)
                ),
                bgcolor='rgba(250,250,250,0.1)'
            ),
            height=600,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        return fig
    
    def create_3d_network_plot(self, nodes_df: pd.DataFrame, edges_df: pd.DataFrame,
                              node_size_col: str = None, node_color_col: str = None,
                              title: str = "3D 基因网络可视化") -> go.Figure:
        """创建3D网络可视化"""
        
        # 创建网络图
        G = nx.from_pandas_edgelist(edges_df, 'source', 'target')
        
        # 添加节点属性
        for _, node in nodes_df.iterrows():
            if node['id'] in G.nodes():
                for col in nodes_df.columns:
                    G.nodes[node['id']][col] = node[col]
        
        # 3D布局 - 使用spring layout
        pos_2d = nx.spring_layout(G, k=1, iterations=50)
        
        # 扩展到3D
        pos_3d = {}
        for node, (x, y) in pos_2d.items():
            # 添加Z轴变化
            z = np.random.normal(0, 0.3)
            pos_3d[node] = (x, y, z)
        
        # 准备边的坐标
        edge_x, edge_y, edge_z = [], [], []
        edge_info = []
        
        for edge in G.edges():
            x0, y0, z0 = pos_3d[edge[0]]
            x1, y1, z1 = pos_3d[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_z.extend([z0, z1, None])
            edge_info.append(f"{edge[0]} - {edge[1]}")
        
        # 创建图形
        fig = go.Figure()
        
        # 添加边
        fig.add_trace(go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            mode='lines',
            line=dict(color='rgba(125,125,125,0.5)', width=2),
            hoverinfo='none',
            showlegend=False,
            name='Edges'
        ))
        
        # 准备节点数据
        node_x = [pos_3d[node][0] for node in G.nodes()]
        node_y = [pos_3d[node][1] for node in G.nodes()]
        node_z = [pos_3d[node][2] for node in G.nodes()]
        node_text = list(G.nodes())
        
        # 节点大小
        if node_size_col and node_size_col in nodes_df.columns:
            size_map = dict(zip(nodes_df['id'], nodes_df[node_size_col]))
            node_sizes = [size_map.get(node, 10) for node in G.nodes()]
            # 归一化大小
            min_size, max_size = min(node_sizes), max(node_sizes)
            if max_size > min_size:
                node_sizes = [8 + 20 * (s - min_size) / (max_size - min_size) for s in node_sizes]
            else:
                node_sizes = [15] * len(node_sizes)
        else:
            node_sizes = [15] * len(G.nodes())
        
        # 节点颜色
        if node_color_col and node_color_col in nodes_df.columns:
            color_map = dict(zip(nodes_df['id'], nodes_df[node_color_col]))
            node_colors = [color_map.get(node, 0) for node in G.nodes()]
        else:
            # 使用度中心性作为颜色
            node_colors = [G.degree(node) for node in G.nodes()]
        
        # 添加节点
        fig.add_trace(go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers+text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                colorscale='Viridis',
                colorbar=dict(
                    title="节点重要性",
                    thickness=15,
                    len=0.5,
                    x=1.02
                ),
                line=dict(width=2, color='white'),
                opacity=0.9
            ),
            text=node_text,
            textposition="middle center",
            textfont=dict(size=8, color='black'),
            hovertemplate='<b>%{text}</b><br>' +
                         '连接度: %{marker.color}<br>' +
                         '坐标: (%{x:.2f}, %{y:.2f}, %{z:.2f})<extra></extra>',
            showlegend=False,
            name='Nodes'
        ))
        
        fig.update_layout(
            title=dict(
                text=f"{title}<br><sub>节点: {len(G.nodes())}, 边: {len(G.edges())}</sub>",
                x=0.5
            ),
            scene=dict(
                xaxis_title='网络 X',
                yaxis_title='网络 Y', 
                zaxis_title='网络 Z',
                camera=dict(
                    eye=dict(x=2, y=2, z=2),
                    center=dict(x=0, y=0, z=0)
                ),
                bgcolor='rgba(245,245,245,0.1)',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, showticklabels=False),
                zaxis=dict(showgrid=False, showticklabels=False)
            ),
            height=700,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        return fig
    
    def create_3d_surface_plot(self, data_matrix: pd.DataFrame, 
                              title: str = "3D 表达谱曲面图") -> go.Figure:
        """创建3D表面图"""
        
        # 准备数据
        z = data_matrix.values
        x = list(range(len(data_matrix.columns)))
        y = list(range(len(data_matrix.index)))
        
        fig = go.Figure(data=[go.Surface(
            z=z,
            x=data_matrix.columns,
            y=data_matrix.index,
            colorscale='RdBu_r',
            hovertemplate='基因: %{y}<br>' +
                         '样本: %{x}<br>' +
                         '表达值: %{z:.3f}<extra></extra>',
            colorbar=dict(
                title="表达值",
                thickness=20,
                len=0.7,
                x=1.02
            )
        )])
        
        fig.update_layout(
            title=dict(text=title, x=0.5),
            scene=dict(
                xaxis_title='样本',
                yaxis_title='基因',
                zaxis_title='表达值',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            height=600,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        return fig
    
    def create_interactive_heatmap_3d(self, data_matrix: pd.DataFrame,
                                     title: str = "交互式3D热图") -> go.Figure:
        """创建交互式3D热图"""
        
        # 添加聚类
        from scipy.cluster.hierarchy import dendrogram, linkage
        from scipy.spatial.distance import pdist
        
        # 对基因进行聚类
        if len(data_matrix) > 2:
            linkage_matrix = linkage(data_matrix.values, method='ward')
            # 简化版：不重排序，直接使用原顺序
        
        # 创建3D热图
        z_offset = 0.1  # 3D效果的Z轴偏移
        
        fig = go.Figure()
        
        # 为每个基因创建一个3D bar
        for i, gene in enumerate(data_matrix.index):
            y_vals = [i] * len(data_matrix.columns)
            x_vals = list(range(len(data_matrix.columns)))
            z_vals = data_matrix.loc[gene].values
            
            fig.add_trace(go.Scatter3d(
                x=x_vals,
                y=y_vals,
                z=z_vals,
                mode='markers',
                marker=dict(
                    size=8,
                    color=z_vals,
                    colorscale='RdBu_r',
                    opacity=0.8,
                    colorbar=dict(
                        title="表达值",
                        x=1.02,
                        len=0.7
                    ) if i == 0 else None,
                    showscale=(i == 0)
                ),
                text=[f"{gene}<br>样本: {col}<br>值: {val:.3f}" 
                      for col, val in zip(data_matrix.columns, z_vals)],
                hovertemplate='%{text}<extra></extra>',
                showlegend=False,
                name=gene if i < 5 else None  # 只显示前5个基因的图例
            ))
        
        fig.update_layout(
            title=dict(text=title, x=0.5),
            scene=dict(
                xaxis_title='样本索引',
                yaxis_title='基因索引',
                zaxis_title='表达值',
                camera=dict(
                    eye=dict(x=2, y=2, z=1.5)
                )
            ),
            height=600,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        return fig

# 全局实例
advanced_3d_visualizer = Advanced3DVisualizer()