"""
Dataset Management Page
数据集管理页面 - 提供完整的数据集管理界面
"""

import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context, no_update
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from src.analysis.dataset_manager import dataset_manager, DatasetInfo
from src.utils.i18n import i18n

def create_dataset_management_page():
    """Create comprehensive dataset management page"""
    
    # Get dataset statistics
    stats = dataset_manager.get_dataset_statistics()
    datasets = dataset_manager.list_datasets()
    
    return html.Div([
        # Header Section
        html.Div([
            html.H1([
                html.I(className="fas fa-database", style={'marginRight': '15px'}),
                i18n.get_text('dataset_management_center', '数据集管理中心')
            ], className="page-title"),
            html.P(i18n.get_text('dataset_management_description', 
                                '全面管理您的多组学数据集，包括查看、编辑、分析和导出功能'),
                  className="page-description")
        ], className="page-header"),
        
        # Statistics Dashboard
        html.Div([
            html.H3([
                html.I(className="fas fa-chart-bar", style={'marginRight': '10px'}),
                i18n.get_text('dataset_statistics', '数据集统计')
            ], style={'marginBottom': '20px'}),
            
            # Statistics Cards
            html.Div([
                _create_stat_card(
                    i18n.get_text('total_datasets', '总数据集'),
                    stats['total_datasets'],
                    'fas fa-database',
                    '#3498db'
                ),
                _create_stat_card(
                    i18n.get_text('user_datasets', '用户数据集'),
                    stats['user_datasets'],
                    'fas fa-user',
                    '#2ecc71'
                ),
                _create_stat_card(
                    i18n.get_text('demo_datasets', '示例数据集'),
                    stats['demo_datasets'],
                    'fas fa-star',
                    '#f39c12'
                ),
                _create_stat_card(
                    i18n.get_text('total_size', '总大小'),
                    f"{stats['total_size_mb']:.1f} MB",
                    'fas fa-hdd',
                    '#9b59b6'
                ),
            ], className="stats-grid", style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
                'gap': '20px',
                'marginBottom': '30px'
            }),
            
            # Status Distribution Chart
            html.Div([
                dcc.Graph(
                    id='dataset-status-chart',
                    figure=_create_status_chart(stats['status_distribution']),
                    style={'height': '300px'}
                )
            ], style={'marginBottom': '30px'})
        ], className="card"),
        
        # Search and Filter Section
        html.Div([
            html.H3([
                html.I(className="fas fa-search", style={'marginRight': '10px'}),
                i18n.get_text('search_filter', '搜索与筛选')
            ], style={'marginBottom': '20px'}),
            
            html.Div([
                # Search box
                html.Div([
                    dcc.Input(
                        id='dataset-search',
                        type='text',
                        placeholder=i18n.get_text('search_placeholder', '搜索数据集名称、描述或标签...'),
                        style={'width': '100%'},
                        className='form-control'
                    )
                ], style={'flex': '1', 'marginRight': '20px'}),
                
                # Type filter
                html.Div([
                    dcc.Dropdown(
                        id='type-filter',
                        options=[
                            {'label': i18n.get_text('all_types', '所有类型'), 'value': 'all'},
                            {'label': i18n.get_text('demo_data', '示例数据'), 'value': 'demo'},
                            {'label': i18n.get_text('user_data', '用户数据'), 'value': 'user'},
                            {'label': i18n.get_text('generated_data', '生成数据'), 'value': 'generated'}
                        ],
                        value='all',
                        clearable=False,
                        style={'width': '200px'}
                    )
                ], style={'marginRight': '20px'}),
                
                # Status filter
                html.Div([
                    dcc.Dropdown(
                        id='status-filter',
                        options=[
                            {'label': i18n.get_text('all_status', '所有状态'), 'value': 'all'},
                            {'label': i18n.get_text('active', '活跃'), 'value': 'active'},
                            {'label': i18n.get_text('archived', '已归档'), 'value': 'archived'},
                            {'label': i18n.get_text('processing', '处理中'), 'value': 'processing'},
                            {'label': i18n.get_text('error', '错误'), 'value': 'error'}
                        ],
                        value='all',
                        clearable=False,
                        style={'width': '200px'}
                    )
                ], style={'marginRight': '20px'}),
                
                # Refresh button
                html.Button([
                    html.I(className="fas fa-sync-alt"),
                    " " + i18n.get_text('refresh', '刷新')
                ], id='refresh-datasets', className='btn btn-primary')
                
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'})
        ], className="card"),
        
        # Dataset Table Section
        html.Div([
            html.H3([
                html.I(className="fas fa-table", style={'marginRight': '10px'}),
                i18n.get_text('dataset_list', '数据集列表')
            ], style={'marginBottom': '20px'}),
            
            # Action buttons
            html.Div([
                html.Button([
                    html.I(className="fas fa-plus"),
                    " " + i18n.get_text('add_dataset', '添加数据集')
                ], id='add-dataset-btn', className='btn btn-success', 
                   style={'marginRight': '10px'}),
                
                html.Button([
                    html.I(className="fas fa-upload"),
                    " " + i18n.get_text('import_dataset', '导入数据集')
                ], id='import-dataset-btn', className='btn btn-primary',
                   style={'marginRight': '10px'}),
                
                html.Button([
                    html.I(className="fas fa-download"),
                    " " + i18n.get_text('export_selected', '导出选中')
                ], id='export-selected-btn', className='btn btn-secondary',
                   style={'marginRight': '10px'}),
                
                html.Button([
                    html.I(className="fas fa-trash"),
                    " " + i18n.get_text('delete_selected', '删除选中')
                ], id='delete-selected-btn', className='btn btn-danger')
            ], style={'marginBottom': '20px'}),
            
            # Dataset table
            html.Div(id='dataset-table-container'),
            
        ], className="card"),
        
        # Modals for various operations
        _create_dataset_detail_modal(),
        _create_add_dataset_modal(),
        _create_edit_dataset_modal(),
        _create_export_modal(),
        _create_delete_confirmation_modal(),
        
        # Hidden divs for data storage
        dcc.Store(id='filtered-datasets', data=[]),
        dcc.Store(id='selected-datasets', data=[]),
        dcc.Store(id='current-dataset-detail', data={}),
        
        # Interval component for auto-refresh
        dcc.Interval(
            id='dataset-refresh-interval',
            interval=30*1000,  # 30 seconds
            n_intervals=0,
            disabled=True
        )
        
    ], className="dataset-management-page")

def _create_stat_card(title, value, icon, color):
    """Create a statistics card"""
    return html.Div([
        html.Div([
            html.I(className=icon, style={
                'fontSize': '2rem',
                'color': color,
                'marginBottom': '10px'
            }),
            html.H3(str(value), style={
                'margin': '0',
                'color': '#2c3e50',
                'fontSize': '2rem',
                'fontWeight': 'bold'
            }),
            html.P(title, style={
                'margin': '0',
                'color': '#7f8c8d',
                'fontSize': '0.9rem'
            })
        ], style={'textAlign': 'center'})
    ], className="stat-card", style={
        'backgroundColor': 'white',
        'padding': '25px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
        'border': f'3px solid {color}',
        'transition': 'transform 0.2s',
        'cursor': 'pointer'
    })

def _create_status_chart(status_distribution):
    """Create status distribution chart"""
    if not status_distribution:
        return go.Figure()
    
    labels = list(status_distribution.keys())
    values = list(status_distribution.values())
    
    colors = {
        'active': '#2ecc71',
        'archived': '#95a5a6',
        'processing': '#f39c12',
        'error': '#e74c3c'
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=[colors.get(label, '#3498db') for label in labels]),
        hole=0.4
    )])
    
    fig.update_layout(
        title=i18n.get_text('dataset_status_distribution', '数据集状态分布'),
        showlegend=True,
        margin=dict(t=40, b=20, l=20, r=20)
    )
    
    return fig

def _create_dataset_table(datasets):
    """Create dataset table"""
    if not datasets:
        return html.Div([
            html.P(i18n.get_text('no_datasets_found', '未找到数据集'),
                  style={'textAlign': 'center', 'padding': '40px', 'color': '#666'})
        ])
    
    # Prepare data for table
    table_data = []
    for ds in datasets:
        table_data.append({
            'select': False,
            'id': ds.id,
            'name': ds.name,
            'type': ds.type,
            'status': ds.status,
            'samples': ds.samples,
            'genes': ds.genes,
            'size_mb': f"{ds.size_mb:.1f}",
            'created_at': ds.created_at[:10] if ds.created_at else '',
            'tags': ', '.join(ds.tags[:3]) + ('...' if len(ds.tags) > 3 else ''),
            'actions': ds.id
        })
    
    columns = [
        {'name': '', 'id': 'select', 'presentation': 'input', 'type': 'text'},
        {'name': i18n.get_text('dataset_id', 'ID'), 'id': 'id'},
        {'name': i18n.get_text('name', '名称'), 'id': 'name'},
        {'name': i18n.get_text('type', '类型'), 'id': 'type'},
        {'name': i18n.get_text('status', '状态'), 'id': 'status'},
        {'name': i18n.get_text('samples', '样本数'), 'id': 'samples', 'type': 'numeric'},
        {'name': i18n.get_text('genes', '基因数'), 'id': 'genes', 'type': 'numeric'},
        {'name': i18n.get_text('size_mb', '大小(MB)'), 'id': 'size_mb', 'type': 'numeric'},
        {'name': i18n.get_text('created_date', '创建日期'), 'id': 'created_at'},
        {'name': i18n.get_text('tags', '标签'), 'id': 'tags'},
        {'name': i18n.get_text('actions', '操作'), 'id': 'actions', 'presentation': 'markdown'}
    ]
    
    # Add action buttons to each row
    for row in table_data:
        dataset_id = row['actions']
        row['actions'] = f"""
        [📊]({dataset_id}#view) 
        [✏️]({dataset_id}#edit) 
        [📥]({dataset_id}#export) 
        [🗑️]({dataset_id}#delete)
        """
    
    return dash_table.DataTable(
        id='dataset-table',
        columns=columns,
        data=table_data,
        editable=False,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=False,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=20,
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontFamily': 'Arial, sans-serif'
        },
        style_header={
            'backgroundColor': '#3498db',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{type} = demo'},
                'backgroundColor': '#e8f5e8',
            },
            {
                'if': {'filter_query': '{status} = error'},
                'backgroundColor': '#ffeaea',
                'color': '#721c24'
            },
            {
                'if': {'filter_query': '{status} = processing'},
                'backgroundColor': '#fff3cd',
                'color': '#856404'
            }
        ],
        style_as_list_view=True,
        markdown_options={'link_target': '_blank'}
    )

def _create_dataset_detail_modal():
    """Create dataset detail modal"""
    return dcc.ConfirmDialog(
        id='dataset-detail-modal',
        displayed=False
    )

def _create_add_dataset_modal():
    """Create add dataset modal"""
    return html.Div(
        id='add-dataset-modal',
        style={'display': 'none'}
    )

def _create_edit_dataset_modal():
    """Create edit dataset modal"""
    return html.Div(
        id='edit-dataset-modal',
        style={'display': 'none'}
    )

def _create_export_modal():
    """Create export modal"""
    return html.Div(
        id='export-modal',
        style={'display': 'none'}
    )

def _create_delete_confirmation_modal():
    """Create delete confirmation modal"""
    return dcc.ConfirmDialog(
        id='delete-confirmation-modal',
        message='',
        displayed=False
    )

def register_dataset_management_callbacks(app):
    """Register all callbacks for dataset management page"""
    
    @app.callback(
        [Output('dataset-table-container', 'children'),
         Output('filtered-datasets', 'data')],
        [Input('refresh-datasets', 'n_clicks'),
         Input('dataset-search', 'value'),
         Input('type-filter', 'value'),
         Input('status-filter', 'value'),
         Input('dataset-refresh-interval', 'n_intervals')]
    )
    def update_dataset_table(refresh_clicks, search_term, type_filter, status_filter, n_intervals):
        """Update dataset table based on filters"""
        # Get all datasets
        datasets = dataset_manager.list_datasets()
        
        # Apply filters
        if type_filter and type_filter != 'all':
            datasets = [ds for ds in datasets if ds.type == type_filter]
        
        if status_filter and status_filter != 'all':
            datasets = [ds for ds in datasets if ds.status == status_filter]
        
        if search_term:
            search_results = dataset_manager.search_datasets(search_term)
            dataset_ids = [ds.id for ds in search_results]
            datasets = [ds for ds in datasets if ds.id in dataset_ids]
        
        # Create table
        table = _create_dataset_table(datasets)
        
        # Store filtered datasets for other callbacks
        filtered_data = [
            {
                'id': ds.id,
                'name': ds.name,
                'type': ds.type,
                'status': ds.status
            } for ds in datasets
        ]
        
        return table, filtered_data
    
    @app.callback(
        Output('dataset-status-chart', 'figure'),
        [Input('refresh-datasets', 'n_clicks'),
         Input('dataset-refresh-interval', 'n_intervals')]
    )
    def update_status_chart(refresh_clicks, n_intervals):
        """Update status distribution chart"""
        stats = dataset_manager.get_dataset_statistics()
        return _create_status_chart(stats['status_distribution'])
    
    # Additional callbacks for modal operations, dataset actions, etc.
    # would be added here...

if __name__ == "__main__":
    # For testing
    app = dash.Dash(__name__)
    app.layout = create_dataset_management_page()
    register_dataset_management_callbacks(app)
    app.run_server(debug=True)