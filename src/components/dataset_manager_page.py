"""
Dataset Management Page Component
数据集管理页面组件 - 提供数据集的增删改查功能
"""

import dash
from dash import html, dcc, dash_table, Input, Output, State, callback_context, no_update
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import humanize

class DatasetManagerPage:
    """Dataset management page with CRUD operations"""
    
    def __init__(self, app, dataset_manager):
        self.app = app
        self.dataset_manager = dataset_manager
        self.register_callbacks()
    
    def create_layout(self):
        """Create the dataset management page layout"""
        return html.Div([
            # Header Section
            html.Div([
                html.H2([
                    html.I(className="fas fa-database", style={'marginRight': '10px'}),
                    "数据集管理中心"
                ], className="card-title"),
                html.P("管理、查看和组织您的多组学数据集", 
                      style={'marginBottom': '20px', 'color': '#666'})
            ], className="card"),
            
            # Stats Overview
            html.Div(id='dataset-stats-cards', children=self._create_stats_cards()),
            
            # Action Bar
            html.Div([
                html.Div([
                    # Search and Filter
                    html.Div([
                        dcc.Input(
                            id='dataset-search',
                            type='text',
                            placeholder='搜索数据集...',
                            style={'width': '300px', 'marginRight': '10px'},
                            className='form-control'
                        ),
                        dcc.Dropdown(
                            id='dataset-type-filter',
                            options=[
                                {'label': '全部类型', 'value': 'all'},
                                {'label': '演示数据', 'value': 'demo'},
                                {'label': '用户数据', 'value': 'user'},
                                {'label': '公共数据', 'value': 'public'}
                            ],
                            value='all',
                            style={'width': '150px', 'marginRight': '10px'}
                        ),
                        dcc.Dropdown(
                            id='dataset-status-filter',
                            options=[
                                {'label': '全部状态', 'value': 'all'},
                                {'label': '已验证', 'value': 'validated'},
                                {'label': '处理中', 'value': 'processing'},
                                {'label': '错误', 'value': 'error'}
                            ],
                            value='all',
                            style={'width': '150px'}
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'flex': '1'}),
                    
                    # Action Buttons
                    html.Div([
                        html.Button([
                            html.I(className="fas fa-sync-alt"),
                            " 刷新"
                        ], id="refresh-datasets", className="btn btn-secondary",
                           style={'marginRight': '10px'}),
                        
                        html.Button([
                            html.I(className="fas fa-trash-alt"),
                            " 批量删除"
                        ], id="batch-delete-datasets", className="btn btn-danger",
                           style={'marginRight': '10px'}),
                        
                        html.Button([
                            html.I(className="fas fa-download"),
                            " 导出清单"
                        ], id="export-dataset-list", className="btn btn-info")
                    ])
                ], style={'display': 'flex', 'justifyContent': 'space-between', 
                         'alignItems': 'center', 'marginBottom': '20px'})
            ], className="card"),
            
            # Datasets Table
            html.Div([
                html.H3([
                    html.I(className="fas fa-table", style={'marginRight': '10px'}),
                    "数据集列表"
                ]),
                html.Div(id='datasets-table-container')
            ], className="card"),
            
            # Dataset Details Modal
            self._create_dataset_details_modal(),
            
            # Confirm Delete Modal
            self._create_confirm_delete_modal(),
            
            # Storage Usage Chart
            html.Div([
                html.H3([
                    html.I(className="fas fa-chart-pie", style={'marginRight': '10px'}),
                    "存储使用情况"
                ]),
                dcc.Graph(id='storage-usage-chart')
            ], className="card"),
            
            # Hidden stores
            dcc.Store(id='selected-datasets'),
            dcc.Store(id='dataset-to-delete'),
            dcc.Download(id='download-dataset-list')
        ])
    
    def _create_stats_cards(self):
        """Create statistics cards"""
        if not self.dataset_manager:
            return html.Div("数据集管理器未初始化", className="alert alert-warning")
        
        datasets = self.dataset_manager.list_datasets()
        
        # Calculate statistics
        total_datasets = len(datasets)
        user_datasets = len([ds for ds in datasets if ds.get('type') == 'user'])
        demo_datasets = len([ds for ds in datasets if ds.get('type') == 'demo'])
        
        # Calculate total size
        total_size = 0
        for ds in datasets:
            size_str = ds.get('size', '0 B')
            if 'MB' in size_str:
                total_size += float(size_str.split(' ')[0])
            elif 'GB' in size_str:
                total_size += float(size_str.split(' ')[0]) * 1024
            elif 'KB' in size_str:
                total_size += float(size_str.split(' ')[0]) / 1024
        
        # Recent uploads (last 7 days)
        recent_count = 0
        week_ago = datetime.now() - timedelta(days=7)
        for ds in datasets:
            if ds.get('upload_time'):
                try:
                    upload_time = datetime.fromisoformat(ds['upload_time'].replace('Z', '+00:00'))
                    if upload_time.replace(tzinfo=None) > week_ago:
                        recent_count += 1
                except:
                    continue
        
        return html.Div([
            # Total Datasets
            html.Div([
                html.Div([
                    html.I(className="fas fa-database", 
                          style={'fontSize': '2rem', 'color': '#3498db'}),
                    html.Div([
                        html.H3(str(total_datasets), style={'margin': '0', 'color': '#2c3e50'}),
                        html.P("总数据集", style={'margin': '0', 'color': '#7f8c8d'})
                    ], style={'marginLeft': '15px'})
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], className="metric-card"),
            
            # User Datasets
            html.Div([
                html.Div([
                    html.I(className="fas fa-user-circle", 
                          style={'fontSize': '2rem', 'color': '#27ae60'}),
                    html.Div([
                        html.H3(str(user_datasets), style={'margin': '0', 'color': '#2c3e50'}),
                        html.P("用户数据集", style={'margin': '0', 'color': '#7f8c8d'})
                    ], style={'marginLeft': '15px'})
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], className="metric-card"),
            
            # Storage Used
            html.Div([
                html.Div([
                    html.I(className="fas fa-hdd", 
                          style={'fontSize': '2rem', 'color': '#f39c12'}),
                    html.Div([
                        html.H3(f"{total_size:.1f} MB", style={'margin': '0', 'color': '#2c3e50'}),
                        html.P("存储使用", style={'margin': '0', 'color': '#7f8c8d'})
                    ], style={'marginLeft': '15px'})
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], className="metric-card"),
            
            # Recent Uploads
            html.Div([
                html.Div([
                    html.I(className="fas fa-clock", 
                          style={'fontSize': '2rem', 'color': '#e74c3c'}),
                    html.Div([
                        html.H3(str(recent_count), style={'margin': '0', 'color': '#2c3e50'}),
                        html.P("最近7天", style={'margin': '0', 'color': '#7f8c8d'})
                    ], style={'marginLeft': '15px'})
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], className="metric-card")
        ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 
                 'gap': '20px', 'marginBottom': '30px'})
    
    def _create_dataset_details_modal(self):
        """Create dataset details modal"""
        return html.Div([
            html.Div([
                html.Div([
                    # Modal Header
                    html.Div([
                        html.H3("数据集详情", style={'margin': '0'}),
                        html.Button("×", id="close-dataset-details", 
                                  style={'background': 'none', 'border': 'none', 
                                         'fontSize': '28px', 'cursor': 'pointer'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 
                             'alignItems': 'center', 'padding': '20px', 
                             'borderBottom': '1px solid #dee2e6'}),
                    
                    # Modal Body
                    html.Div(id='dataset-details-content', 
                           style={'padding': '20px', 'maxHeight': '70vh', 
                                 'overflowY': 'auto'}),
                    
                    # Modal Footer
                    html.Div([
                        html.Button("编辑", id="edit-dataset", className="btn btn-primary",
                                  style={'marginRight': '10px'}),
                        html.Button("删除", id="delete-dataset-from-modal", 
                                  className="btn btn-danger", style={'marginRight': '10px'}),
                        html.Button("关闭", id="close-dataset-details-footer", 
                                  className="btn btn-secondary")
                    ], style={'padding': '20px', 'borderTop': '1px solid #dee2e6', 
                             'textAlign': 'right'})
                ], style={'background': 'white', 'borderRadius': '8px', 
                         'maxWidth': '800px', 'margin': '50px auto', 
                         'boxShadow': '0 5px 15px rgba(0,0,0,.5)'})
            ], style={'position': 'fixed', 'top': '0', 'left': '0', 'right': '0', 
                     'bottom': '0', 'background': 'rgba(0,0,0,0.5)', 'zIndex': '1050'})
        ], id="dataset-details-modal", style={'display': 'none'})
    
    def _create_confirm_delete_modal(self):
        """Create confirm delete modal"""
        return html.Div([
            html.Div([
                html.Div([
                    # Modal Header
                    html.Div([
                        html.H3("确认删除", style={'margin': '0', 'color': '#dc3545'}),
                        html.Button("×", id="close-confirm-delete", 
                                  style={'background': 'none', 'border': 'none', 
                                         'fontSize': '28px', 'cursor': 'pointer'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 
                             'alignItems': 'center', 'padding': '20px', 
                             'borderBottom': '1px solid #dee2e6'}),
                    
                    # Modal Body
                    html.Div([
                        html.I(className="fas fa-exclamation-triangle", 
                              style={'fontSize': '3rem', 'color': '#ffc107', 'marginBottom': '15px'}),
                        html.P("确定要删除这个数据集吗？", style={'fontSize': '1.2rem', 'marginBottom': '10px'}),
                        html.P("此操作无法撤销，将永久删除数据集及其所有分析结果。", 
                              style={'color': '#6c757d', 'marginBottom': '20px'}),
                        html.Div(id='delete-dataset-info')
                    ], style={'padding': '20px', 'textAlign': 'center'}),
                    
                    # Modal Footer
                    html.Div([
                        html.Button("取消", id="cancel-delete", className="btn btn-secondary",
                                  style={'marginRight': '10px'}),
                        html.Button("确认删除", id="confirm-delete", className="btn btn-danger")
                    ], style={'padding': '20px', 'textAlign': 'center'})
                ], style={'background': 'white', 'borderRadius': '8px', 
                         'maxWidth': '500px', 'margin': '100px auto', 
                         'boxShadow': '0 5px 15px rgba(0,0,0,.5)'})
            ], style={'position': 'fixed', 'top': '0', 'left': '0', 'right': '0', 
                     'bottom': '0', 'background': 'rgba(0,0,0,0.5)', 'zIndex': '1060'})
        ], id="confirm-delete-modal", style={'display': 'none'})
    
    def register_callbacks(self):
        """Register all callbacks for the dataset manager page"""
        
        # Update datasets table
        @self.app.callback(
            Output('datasets-table-container', 'children'),
            [Input('refresh-datasets', 'n_clicks'),
             Input('dataset-search', 'value'),
             Input('dataset-type-filter', 'value'),
             Input('dataset-status-filter', 'value')],
            prevent_initial_call=False
        )
        def update_datasets_table(refresh_clicks, search_value, type_filter, status_filter):
            if not self.dataset_manager:
                return html.Div("数据集管理器未初始化", className="alert alert-warning")
            
            # Get datasets
            datasets = self.dataset_manager.list_datasets()
            
            # Apply filters
            if search_value:
                datasets = [ds for ds in datasets 
                           if search_value.lower() in ds.get('name', '').lower()]
            
            if type_filter and type_filter != 'all':
                datasets = [ds for ds in datasets if ds.get('type') == type_filter]
            
            if status_filter and status_filter != 'all':
                datasets = [ds for ds in datasets if ds.get('status') == status_filter]
            
            if not datasets:
                return html.Div([
                    html.I(className="fas fa-inbox", 
                          style={'fontSize': '48px', 'color': '#bdc3c7'}),
                    html.P("没有找到数据集", style={'marginTop': '10px'})
                ], style={'textAlign': 'center', 'padding': '40px'})
            
            # Create table data
            table_data = []
            for ds in datasets:
                # Format upload time
                upload_time = ds.get('upload_time', 'N/A')
                if upload_time and upload_time != 'N/A':
                    try:
                        dt = datetime.fromisoformat(upload_time.replace('Z', '+00:00'))
                        upload_time = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                
                # Status badge
                status = ds.get('status', 'unknown')
                status_color = {
                    'validated': '#28a745',
                    'processing': '#ffc107', 
                    'error': '#dc3545',
                    'unknown': '#6c757d'
                }.get(status, '#6c757d')
                
                table_data.append({
                    'name': ds.get('name', 'Unnamed'),
                    'type': ds.get('type', 'unknown'),
                    'size': ds.get('size', '0 B'),
                    'samples': ds.get('samples', 0),
                    'features': ds.get('features', 0),
                    'upload_time': upload_time,
                    'status': status,
                    'id': ds.get('id')
                })
            
            # Create DataTable
            return dash_table.DataTable(
                id='datasets-table',
                columns=[
                    {'name': '数据集名称', 'id': 'name'},
                    {'name': '类型', 'id': 'type'},
                    {'name': '大小', 'id': 'size'},
                    {'name': '样本数', 'id': 'samples', 'type': 'numeric'},
                    {'name': '特征数', 'id': 'features', 'type': 'numeric'},
                    {'name': '上传时间', 'id': 'upload_time'},
                    {'name': '状态', 'id': 'status'},
                    {'name': '操作', 'id': 'actions', 'presentation': 'markdown'}
                ],
                data=[{
                    **row,
                    'actions': f"[查看详情](#{row['id']}) | [分析](#{row['id']}) | [删除](#{row['id']})"
                } for row in table_data],
                style_cell={'textAlign': 'center', 'padding': '10px'},
                style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{status} = validated'},
                        'backgroundColor': '#d4edda',
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{status} = error'},
                        'backgroundColor': '#f8d7da',
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{type} = demo'},
                        'fontStyle': 'italic'
                    }
                ],
                row_selectable='multi',
                selected_rows=[],
                sort_action='native',
                filter_action='native',
                page_action='native',
                page_current=0,
                page_size=10
            )
        
        # Update storage usage chart
        @self.app.callback(
            Output('storage-usage-chart', 'figure'),
            [Input('refresh-datasets', 'n_clicks')],
            prevent_initial_call=False
        )
        def update_storage_chart(refresh_clicks):
            if not self.dataset_manager:
                return {}
            
            datasets = self.dataset_manager.list_datasets()
            
            # Calculate storage by type
            storage_by_type = {}
            for ds in datasets:
                ds_type = ds.get('type', 'unknown')
                size_str = ds.get('size', '0 B')
                
                # Parse size
                size_mb = 0
                if 'MB' in size_str:
                    size_mb = float(size_str.split(' ')[0])
                elif 'GB' in size_str:
                    size_mb = float(size_str.split(' ')[0]) * 1024
                elif 'KB' in size_str:
                    size_mb = float(size_str.split(' ')[0]) / 1024
                
                storage_by_type[ds_type] = storage_by_type.get(ds_type, 0) + size_mb
            
            if not storage_by_type:
                return {}
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=list(storage_by_type.keys()),
                values=list(storage_by_type.values()),
                hole=0.3
            )])
            
            fig.update_layout(
                title="按类型分布的存储使用情况",
                annotations=[dict(text='存储<br>分布', x=0.5, y=0.5, font_size=12, showarrow=False)]
            )
            
            return fig
        
        # Show/hide dataset details modal
        @self.app.callback(
            [Output('dataset-details-modal', 'style'),
             Output('dataset-details-content', 'children')],
            [Input('datasets-table', 'active_cell'),
             Input('close-dataset-details', 'n_clicks'),
             Input('close-dataset-details-footer', 'n_clicks')],
            [State('datasets-table', 'data')],
            prevent_initial_call=True
        )
        def toggle_dataset_details(active_cell, close1, close2, table_data):
            ctx = callback_context
            
            if not ctx.triggered:
                return no_update, no_update
            
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if trigger_id in ['close-dataset-details', 'close-dataset-details-footer']:
                return {'display': 'none'}, no_update
            
            if trigger_id == 'datasets-table' and active_cell:
                # Show details for clicked dataset
                row_index = active_cell['row']
                if row_index < len(table_data):
                    dataset_id = table_data[row_index]['id'] if 'id' in table_data[row_index] else table_data[row_index]['name']
                    
                    # Get full dataset info
                    dataset = self.dataset_manager.get_dataset(dataset_id) if self.dataset_manager else {}
                    
                    if not dataset:
                        content = html.Div("数据集不存在", className="alert alert-danger")
                    else:
                        content = self._create_dataset_details_content(dataset)
                    
                    return {'display': 'block'}, content
            
            return no_update, no_update
        
        # Export dataset list
        @self.app.callback(
            Output('download-dataset-list', 'data'),
            [Input('export-dataset-list', 'n_clicks')],
            prevent_initial_call=True
        )
        def export_dataset_list(n_clicks):
            if not n_clicks or not self.dataset_manager:
                return no_update
            
            datasets = self.dataset_manager.list_datasets()
            df = pd.DataFrame(datasets)
            
            return dcc.send_data_frame(
                df.to_csv, 
                "dataset_list.csv", 
                index=False
            )
    
    def _create_dataset_details_content(self, dataset: Dict):
        """Create detailed content for a dataset"""
        return html.Div([
            # Basic Information
            html.Div([
                html.H4("基本信息"),
                html.Div([
                    html.Div([
                        html.Strong("数据集名称: "),
                        dataset.get('name', 'N/A')
                    ], style={'marginBottom': '10px'}),
                    
                    html.Div([
                        html.Strong("数据集ID: "),
                        dataset.get('id', 'N/A')
                    ], style={'marginBottom': '10px'}),
                    
                    html.Div([
                        html.Strong("类型: "),
                        {'demo': '演示数据', 'user': '用户数据', 'public': '公共数据'}.get(
                            dataset.get('type'), dataset.get('type', 'N/A'))
                    ], style={'marginBottom': '10px'}),
                    
                    html.Div([
                        html.Strong("状态: "),
                        html.Span(
                            {'validated': '已验证', 'processing': '处理中', 'error': '错误'}.get(
                                dataset.get('status'), dataset.get('status', 'N/A')),
                            style={'color': {
                                'validated': '#28a745',
                                'processing': '#ffc107',
                                'error': '#dc3545'
                            }.get(dataset.get('status'), '#6c757d')}
                        )
                    ], style={'marginBottom': '10px'}),
                    
                    html.Div([
                        html.Strong("上传时间: "),
                        dataset.get('upload_time', 'N/A')
                    ], style={'marginBottom': '10px'}),
                ])
            ], style={'marginBottom': '30px'}),
            
            # Data Statistics
            html.Div([
                html.H4("数据统计"),
                html.Div([
                    html.Div([
                        html.Strong("文件大小: "),
                        dataset.get('size', 'N/A')
                    ], style={'marginBottom': '10px'}),
                    
                    html.Div([
                        html.Strong("样本数量: "),
                        str(dataset.get('samples', 'N/A'))
                    ], style={'marginBottom': '10px'}),
                    
                    html.Div([
                        html.Strong("特征数量: "),
                        str(dataset.get('features', 'N/A'))
                    ], style={'marginBottom': '10px'}),
                    
                    html.Div([
                        html.Strong("包含数据类型: "),
                        ', '.join(dataset.get('data_types', []))
                    ], style={'marginBottom': '10px'}),
                ])
            ], style={'marginBottom': '30px'}),
            
            # File Information
            html.Div([
                html.H4("文件信息"),
                html.Div([
                    html.Div([
                        html.Strong("临床数据: "),
                        "✓ 已包含" if dataset.get('has_clinical') else "✗ 未包含"
                    ], style={'marginBottom': '10px'}),
                    
                    html.Div([
                        html.Strong("表达数据: "),
                        "✓ 已包含" if dataset.get('has_expression') else "✗ 未包含"
                    ], style={'marginBottom': '10px'}),
                    
                    html.Div([
                        html.Strong("突变数据: "),
                        "✓ 已包含" if dataset.get('has_mutations') else "✗ 未包含"
                    ], style={'marginBottom': '10px'}),
                    
                    html.Div([
                        html.Strong("存储路径: "),
                        html.Code(dataset.get('file_path', 'N/A'))
                    ], style={'marginBottom': '10px'}),
                ])
            ], style={'marginBottom': '30px'}),
            
            # Analysis History
            html.Div([
                html.H4("分析历史"),
                html.P(f"该数据集已进行 {dataset.get('analysis_count', 0)} 次分析"),
                html.P(f"最后分析时间: {dataset.get('last_analysis', 'N/A')}")
            ])
        ])


# Create page layout function for easy integration
def create_dataset_manager_page(app, dataset_manager):
    """Create dataset manager page"""
    manager_page = DatasetManagerPage(app, dataset_manager)
    return manager_page.create_layout()