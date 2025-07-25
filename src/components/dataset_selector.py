"""
Dataset Selector Component
数据集选择器组件，用于在分析页面选择要分析的数据集
"""

from dash import dcc, html
from typing import Dict, List

def create_dataset_selector(dataset_manager, component_id='dataset-selector'):
    """Create a dataset selector component"""
    
    if not dataset_manager:
        return html.Div()
    
    # Get current dataset and all datasets
    current_dataset = dataset_manager.get_current_dataset()
    datasets = dataset_manager.list_datasets()
    
    # Create options for dropdown
    options = []
    for dataset in datasets:
        label = f"{dataset['name']} ({dataset['type']})"
        if dataset.get('features'):
            label += f" - {dataset['features']['samples']}样本"
        options.append({
            'label': label,
            'value': dataset['id']
        })
    
    # Create selector component
    return html.Div([
        html.Div([
            html.Div([
                # Current dataset info
                html.Div([
                    html.H5("当前数据集", style={'marginBottom': '10px'}),
                    html.Div([
                        html.I(className="fas fa-database", style={'marginRight': '10px'}),
                        html.Span(current_dataset['name'], style={'fontWeight': 'bold'}),
                        html.Span(f" ({current_dataset['type']})", style={'color': '#666', 'fontSize': '0.9rem'})
                    ]),
                    html.Small(current_dataset.get('description', ''), style={'color': '#666'})
                ], style={'flex': '1'}),
                
                # Dataset switcher
                html.Div([
                    dcc.Dropdown(
                        id=component_id,
                        options=options,
                        value=dataset_manager.config.get('current_dataset', 'demo'),
                        clearable=False,
                        style={'width': '300px'}
                    )
                ], style={'marginLeft': '20px'})
            ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between'}),
            
            # Dataset features
            html.Div([
                html.Hr(style={'margin': '15px 0'}),
                html.Div([
                    create_feature_badge("样本数", current_dataset['features']['samples'], "fa-users"),
                    create_feature_badge("基因数", current_dataset['features']['genes'], "fa-dna"),
                    create_feature_badge("临床", "✓" if current_dataset['features']['has_clinical'] else "✗", 
                                       "fa-hospital", current_dataset['features']['has_clinical']),
                    create_feature_badge("表达", "✓" if current_dataset['features']['has_expression'] else "✗", 
                                       "fa-chart-bar", current_dataset['features']['has_expression']),
                    create_feature_badge("突变", "✓" if current_dataset['features']['has_mutation'] else "✗", 
                                       "fa-exclamation-triangle", current_dataset['features']['has_mutation']),
                ], style={'display': 'flex', 'gap': '10px', 'flexWrap': 'wrap'})
            ]) if current_dataset.get('features') else html.Div()
        ], style={
            'backgroundColor': '#f8f9fa',
            'padding': '20px',
            'borderRadius': '8px',
            'marginBottom': '20px',
            'border': '1px solid #dee2e6'
        })
    ], className="dataset-selector-container")

def create_feature_badge(label, value, icon, is_available=True):
    """Create a feature badge"""
    color = "#28a745" if is_available else "#dc3545" if isinstance(is_available, bool) else "#6c757d"
    return html.Div([
        html.I(className=f"fas {icon}", style={'marginRight': '5px', 'color': color}),
        html.Span(f"{label}: ", style={'fontSize': '0.9rem'}),
        html.Span(str(value), style={'fontWeight': 'bold', 'color': color})
    ], style={
        'padding': '5px 10px',
        'backgroundColor': 'white',
        'borderRadius': '20px',
        'border': f'1px solid {color}',
        'fontSize': '0.85rem'
    })

def create_data_source_indicator(dataset_info: Dict):
    """Create a small data source indicator"""
    is_demo = dataset_info.get('type', 'demo') == 'demo'
    
    return html.Div([
        html.I(className="fas fa-database", style={'marginRight': '5px'}),
        html.Span("Demo数据" if is_demo else "用户数据"),
        html.Span(f" - {dataset_info['name']}", style={'fontWeight': 'normal'})
    ], style={
        'position': 'absolute',
        'top': '10px',
        'right': '10px',
        'backgroundColor': '#007bff' if is_demo else '#28a745',
        'color': 'white',
        'padding': '5px 15px',
        'borderRadius': '20px',
        'fontSize': '0.85rem',
        'fontWeight': 'bold',
        'zIndex': '10'
    })