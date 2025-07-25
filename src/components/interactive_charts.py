"""
Interactive Chart Components
交互式图表组件 - 为所有图表添加高级交互功能
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import json
import base64
import io
from dash import dcc, html, Input, Output, State, callback_context, no_update
import dash

class InteractiveChartEnhancer:
    """Enhanced chart functionality with advanced interactions"""
    
    def __init__(self):
        self.selected_data = {}
        self.chart_configs = {}
        self.filter_links = {}
        
    def enhance_figure(self, fig: go.Figure, chart_id: str, chart_type: str = 'scatter', 
                      enable_crossfilter: bool = True, export_formats: List[str] = None) -> go.Figure:
        """Enhance a Plotly figure with advanced interaction capabilities"""
        
        if export_formats is None:
            export_formats = ['png', 'svg', 'pdf', 'html']
        
        # Store chart configuration
        self.chart_configs[chart_id] = {
            'type': chart_type,
            'crossfilter': enable_crossfilter,
            'export_formats': export_formats
        }
        
        # Add enhanced layout configurations
        fig.update_layout(
            # Enable selection tools
            dragmode='select',
            selectdirection='diagonal',
            
            # Enhanced hover functionality
            hovermode='closest',
            
            # Professional styling
            template='plotly_white',
            
            # Custom toolbar
            modebar=dict(
                orientation='v',
                bgcolor='rgba(255,255,255,0.8)',
                color='#666',
                activecolor='#007bff'
            ),
            
            # Interactive legends
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.2)",
                borderwidth=1
            ),
            
            # Annotations for guidance
            annotations=[
                dict(
                    text="📊 拖拽选择数据点 | 🔍 双击重置视图 | 📁 右键导出图表",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.5, y=-0.1,
                    xanchor='center', yanchor='top',
                    font=dict(size=10, color='#666'),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="rgba(0,0,0,0.1)",
                    borderwidth=1
                )
            ]
        )
        
        # Add custom trace configurations for interaction
        for trace in fig.data:
            if hasattr(trace, 'marker'):
                # Enhanced marker styling for selection
                if trace.marker:
                    trace.marker.update(
                        size=8,
                        line=dict(width=1, color='white'),
                        opacity=0.8
                    )
                
                # Add selection styling
                trace.update(
                    selected=dict(marker=dict(color='red', size=12, opacity=1.0)),
                    unselected=dict(marker=dict(opacity=0.3))
                )
        
        # Configure zoom and pan
        fig.update_xaxes(
            showspikes=True,
            spikecolor="orange",
            spikesnap="cursor",
            spikemode="across",
            spikethickness=1
        )
        fig.update_yaxes(
            showspikes=True,
            spikecolor="orange",
            spikesnap="cursor",
            spikemode="across",
            spikethickness=1
        )
        
        return fig
    
    def create_enhanced_scatter(self, df: pd.DataFrame, x_col: str, y_col: str, 
                               color_col: str = None, size_col: str = None,
                               chart_id: str = None, title: str = "交互式散点图") -> go.Figure:
        """Create enhanced interactive scatter plot"""
        
        fig = px.scatter(
            df, x=x_col, y=y_col, 
            color=color_col, size=size_col,
            hover_data=df.columns.tolist(),
            title=title,
            labels={
                x_col: f"{x_col} 📈",
                y_col: f"{y_col} 📊"
            }
        )
        
        if chart_id:
            fig = self.enhance_figure(fig, chart_id, 'scatter')
        
        return fig
    
    def create_enhanced_heatmap(self, df: pd.DataFrame, chart_id: str = None,
                               title: str = "交互式热图") -> go.Figure:
        """Create enhanced interactive heatmap"""
        
        fig = go.Figure(data=go.Heatmap(
            z=df.values,
            x=df.columns,
            y=df.index,
            colorscale='RdBu_r',
            hoverongaps=False,
            hovertemplate='<b>%{y}</b><br>' +
                         '<b>%{x}</b><br>' +
                         '值: %{z:.3f}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="样本",
            yaxis_title="基因",
            height=600
        )
        
        if chart_id:
            fig = self.enhance_figure(fig, chart_id, 'heatmap')
        
        return fig
    
    def create_enhanced_bar(self, df: pd.DataFrame, x_col: str, y_col: str,
                           color_col: str = None, chart_id: str = None,
                           title: str = "交互式柱状图") -> go.Figure:
        """Create enhanced interactive bar chart"""
        
        fig = px.bar(
            df, x=x_col, y=y_col, color=color_col,
            title=title,
            hover_data=df.columns.tolist()
        )
        
        # Add value annotations on bars
        fig.update_traces(
            texttemplate='%{y:.2f}',
            textposition='outside'
        )
        
        if chart_id:
            fig = self.enhance_figure(fig, chart_id, 'bar')
        
        return fig
    
    def create_enhanced_line(self, df: pd.DataFrame, x_col: str, y_col: str,
                            color_col: str = None, chart_id: str = None,
                            title: str = "交互式折线图") -> go.Figure:
        """Create enhanced interactive line chart"""
        
        fig = px.line(
            df, x=x_col, y=y_col, color=color_col,
            title=title,
            hover_data=df.columns.tolist(),
            markers=True
        )
        
        # Enhanced line styling
        fig.update_traces(
            mode='lines+markers',
            line=dict(width=3),
            marker=dict(size=8, line=dict(width=2, color='white'))
        )
        
        if chart_id:
            fig = self.enhance_figure(fig, chart_id, 'line')
        
        return fig
    
    def create_enhanced_violin(self, df: pd.DataFrame, x_col: str, y_col: str,
                              chart_id: str = None, title: str = "交互式小提琴图") -> go.Figure:
        """Create enhanced interactive violin plot"""
        
        fig = go.Figure()
        
        for category in df[x_col].unique():
            category_data = df[df[x_col] == category][y_col]
            
            fig.add_trace(go.Violin(
                y=category_data,
                x=[category] * len(category_data),
                name=str(category),
                box_visible=True,
                meanline_visible=True,
                points='all',
                jitter=0.05,
                pointpos=0,
                hoveron='points+kde'
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            showlegend=True
        )
        
        if chart_id:
            fig = self.enhance_figure(fig, chart_id, 'violin')
        
        return fig
    
    def create_enhanced_network(self, nodes: pd.DataFrame, edges: pd.DataFrame,
                               chart_id: str = None, title: str = "交互式网络图") -> go.Figure:
        """Create enhanced interactive network visualization"""
        
        # Create network layout (simplified force-directed)
        np.random.seed(42)
        n_nodes = len(nodes)
        
        # Generate positions
        pos = {}
        for i, node in enumerate(nodes['id']):
            angle = 2 * np.pi * i / n_nodes
            radius = 5 + 2 * np.random.random()
            pos[node] = {
                'x': radius * np.cos(angle) + np.random.normal(0, 0.5),
                'y': radius * np.sin(angle) + np.random.normal(0, 0.5)
            }
        
        # Create edge traces
        edge_x = []
        edge_y = []
        edge_info = []
        
        for _, edge in edges.iterrows():
            x0, y0 = pos[edge['source']]['x'], pos[edge['source']]['y']
            x1, y1 = pos[edge['target']]['x'], pos[edge['target']]['y']
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_info.append(f"{edge['source']} - {edge['target']}")
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create node trace
        node_x = [pos[node]['x'] for node in nodes['id']]
        node_y = [pos[node]['y'] for node in nodes['id']]
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=nodes['id'],
            textposition="middle center",
            marker=dict(
                showscale=True,
                colorscale='Viridis',
                reversescale=True,
                color=nodes.get('value', range(len(nodes))),
                size=nodes.get('size', [20] * len(nodes)),
                colorbar=dict(
                    thickness=15,
                    len=0.5,
                    x=1.1,
                    title="节点权重"
                ),
                line=dict(width=2, color='white')
            )
        )
        
        # Add hover text
        hover_text = []
        for _, node in nodes.iterrows():
            hover_info = f"<b>{node['id']}</b><br>"
            hover_info += f"连接数: {len(edges[(edges['source'] == node['id']) | (edges['target'] == node['id'])])}<br>"
            if 'label' in node:
                hover_info += f"类型: {node['label']}<br>"
            hover_text.append(hover_info)
        
        node_trace.hovertext = hover_text
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title=title,
                           titlefont_size=16,
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="节点大小表示连接度，颜色表示重要性",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002 ) ],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                       )
        
        if chart_id:
            fig = self.enhance_figure(fig, chart_id, 'network')
        
        return fig
    
    def create_chart_export_component(self, chart_id: str) -> html.Div:
        """Create export controls for a chart"""
        
        return html.Div([
            html.Div([
                html.H6([
                    html.I(className="fas fa-download"),
                    " 导出选项"
                ], style={'marginBottom': '10px'}),
                
                html.Div([
                    html.Button([
                        html.I(className="fas fa-image"),
                        " PNG"
                    ], id=f"export-png-{chart_id}", 
                       className="btn btn-sm btn-outline-primary",
                       style={'marginRight': '5px', 'marginBottom': '5px'}),
                    
                    html.Button([
                        html.I(className="fas fa-vector-square"),
                        " SVG"
                    ], id=f"export-svg-{chart_id}", 
                       className="btn btn-sm btn-outline-primary",
                       style={'marginRight': '5px', 'marginBottom': '5px'}),
                    
                    html.Button([
                        html.I(className="fas fa-file-pdf"),
                        " PDF"
                    ], id=f"export-pdf-{chart_id}", 
                       className="btn btn-sm btn-outline-primary",
                       style={'marginRight': '5px', 'marginBottom': '5px'}),
                    
                    html.Button([
                        html.I(className="fas fa-code"),
                        " HTML"
                    ], id=f"export-html-{chart_id}", 
                       className="btn btn-sm btn-outline-primary",
                       style={'marginRight': '5px', 'marginBottom': '5px'}),
                    
                    html.Button([
                        html.I(className="fas fa-table"),
                        " 数据"
                    ], id=f"export-data-{chart_id}", 
                       className="btn btn-sm btn-outline-success",
                       style={'marginBottom': '5px'})
                ], style={'display': 'flex', 'flexWrap': 'wrap'})
            ], style={
                'backgroundColor': '#f8f9fa',
                'padding': '15px',
                'borderRadius': '8px',
                'border': '1px solid #dee2e6',
                'marginTop': '10px'
            }),
            
            # Hidden download components
            dcc.Download(id=f"download-{chart_id}")
        ])
    
    def create_chart_filters_component(self, chart_id: str, 
                                     filter_options: List[Dict]) -> html.Div:
        """Create filtering controls for a chart"""
        
        filters = []
        for option in filter_options:
            filter_component = html.Div([
                html.Label(option['label'], style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id=f"filter-{option['id']}-{chart_id}",
                    options=option['options'],
                    value=option.get('default'),
                    multi=option.get('multi', False),
                    clearable=True,
                    placeholder=f"选择{option['label']}..."
                )
            ], style={'marginBottom': '15px'})
            filters.append(filter_component)
        
        return html.Div([
            html.Div([
                html.H6([
                    html.I(className="fas fa-filter"),
                    " 数据筛选"
                ], style={'marginBottom': '15px'}),
                
                html.Div(filters),
                
                html.Div([
                    html.Button([
                        html.I(className="fas fa-sync-alt"),
                        " 重置筛选"
                    ], id=f"reset-filters-{chart_id}", 
                       className="btn btn-sm btn-outline-secondary",
                       style={'marginRight': '10px'}),
                    
                    html.Button([
                        html.I(className="fas fa-apply"),
                        " 应用筛选"
                    ], id=f"apply-filters-{chart_id}", 
                       className="btn btn-sm btn-primary")
                ])
            ], style={
                'backgroundColor': '#f8f9fa',
                'padding': '15px',
                'borderRadius': '8px',
                'border': '1px solid #dee2e6',
                'marginTop': '10px'
            })
        ])
    
    def create_chart_statistics_component(self, chart_id: str) -> html.Div:
        """Create statistics panel for selected data"""
        
        return html.Div([
            html.Div([
                html.H6([
                    html.I(className="fas fa-chart-bar"),
                    " 选中数据统计"
                ], style={'marginBottom': '15px'}),
                
                html.Div(id=f"stats-content-{chart_id}", children=[
                    html.P("请在图表中选择数据点查看统计信息", 
                          style={'color': '#666', 'fontStyle': 'italic'})
                ])
            ], style={
                'backgroundColor': '#f8f9fa',
                'padding': '15px',
                'borderRadius': '8px',
                'border': '1px solid #dee2e6',
                'marginTop': '10px'
            })
        ])
    
    def create_enhanced_chart_container(self, chart_id: str, figure: go.Figure,
                                      filter_options: List[Dict] = None,
                                      show_export: bool = True,
                                      show_filters: bool = True,
                                      show_stats: bool = True) -> html.Div:
        """Create a complete enhanced chart container with all controls"""
        
        components = [
            # Main chart
            dcc.Graph(
                id=f"chart-{chart_id}",
                figure=figure,
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['lasso2d'],
                    'modeBarButtonsToAdd': [
                        {
                            'name': '选择模式',
                            'icon': {'width': 512, 'height': 512, 
                                    'path': 'M0 0h512v512H0z', 'color': '#333'},
                            'click': 'function(gd) { Plotly.relayout(gd, {dragmode: "select"}); }'
                        }
                    ]
                },
                style={'height': '500px'}
            )
        ]
        
        # Add control panels in a collapsible accordion
        controls = []
        
        if show_export:
            controls.append(
                dcc.Collapse(
                    id=f"export-collapse-{chart_id}",
                    children=[self.create_chart_export_component(chart_id)],
                    is_open=False
                )
            )
        
        if show_filters and filter_options:
            controls.append(
                dcc.Collapse(
                    id=f"filter-collapse-{chart_id}",
                    children=[self.create_chart_filters_component(chart_id, filter_options)],
                    is_open=False
                )
            )
        
        if show_stats:
            controls.append(
                dcc.Collapse(
                    id=f"stats-collapse-{chart_id}",
                    children=[self.create_chart_statistics_component(chart_id)],
                    is_open=False
                )
            )
        
        if controls:
            # Control buttons
            control_buttons = html.Div([
                html.Button([
                    html.I(className="fas fa-download"),
                    " 导出"
                ], id=f"toggle-export-{chart_id}", 
                   className="btn btn-sm btn-outline-primary",
                   style={'marginRight': '5px'}),
                
                html.Button([
                    html.I(className="fas fa-filter"),
                    " 筛选"
                ], id=f"toggle-filter-{chart_id}", 
                   className="btn btn-sm btn-outline-secondary",
                   style={'marginRight': '5px'}),
                
                html.Button([
                    html.I(className="fas fa-chart-bar"),
                    " 统计"
                ], id=f"toggle-stats-{chart_id}", 
                   className="btn btn-sm btn-outline-info")
            ], style={'marginTop': '10px', 'textAlign': 'center'})
            
            components.extend([control_buttons] + controls)
        
        return html.Div(components, className="enhanced-chart-container")

# Global instance
chart_enhancer = InteractiveChartEnhancer()