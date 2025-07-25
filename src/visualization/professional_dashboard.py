"""
Professional LIHC Dashboard with Top + Sidebar Navigation
专业的LIHC仪表板，采用顶部+侧边导航布局
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

import dash
from dash import dcc, html, Input, Output, State, dash_table, callback, no_update
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import base64
import io
import zipfile
import tempfile
import json

# Import utilities
try:
    from src.utils.i18n import i18n
    from src.utils.common import PathManager, ResultsLoader, DataValidator
    from src.analysis.survival_analysis import SurvivalAnalyzer, create_demo_survival_data
    from src.data_processing.data_upload_manager import DataUploadManager, UserDataAnalyzer
    from src.analysis.data_loader import data_loader, create_dataset_specific_content
    from src.analysis.progress_manager import ProgressManager, create_progress_callback
    DATALOADER_AVAILABLE = True
    PROGRESS_AVAILABLE = True
except ImportError:
    # Fallback
    class MockI18n:
        def get_text(self, key, fallback=None):
            return fallback or key
        def set_language(self, lang):
            return True
        def get_current_language(self):
            return 'zh'
    i18n = MockI18n()
    DATALOADER_AVAILABLE = False
    PROGRESS_AVAILABLE = False
    data_loader = None

class ProfessionalDashboard:
    """Professional dashboard with enhanced navigation"""
    
    def __init__(self):
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)
        self.load_demo_data()
        self.setup_styling()
        self.setup_layout()
        self.setup_callbacks()
        self.setup_batch_callbacks()
        self.setup_taskqueue_callbacks()
        
        # Initialize upload manager
        try:
            self.upload_manager = DataUploadManager()
        except:
            self.upload_manager = None
        
        # Initialize history manager
        try:
            from src.data_processing.history_manager import HistoryManager
            self.history_manager = HistoryManager()
        except:
            self.history_manager = None
        
        # Initialize dataset manager
        try:
            from src.data_processing.dataset_manager import DatasetManager
            self.dataset_manager = DatasetManager()
        except:
            self.dataset_manager = None
    
    def load_demo_data(self):
        """Load demo data for display"""
        try:
            # Load clinical data
            self.clinical_data = pd.read_csv('examples/demo_data/clinical.csv', index_col=0)
            # Load expression data
            self.expression_data = pd.read_csv('examples/demo_data/expression.csv', index_col=0)
            # Load multi-omics data
            self.cnv_data = pd.read_csv('examples/demo_data/cnv.csv', index_col=0)
            self.methylation_data = pd.read_csv('examples/demo_data/methylation.csv', index_col=0)
            self.mutations_data = pd.read_csv('examples/demo_data/mutations.csv')
            # Load linchpin results
            self.linchpin_data = pd.read_csv('results/linchpins/linchpin_scores.csv')
            # Load network data
            self.network_data = pd.read_csv('results/networks/network_centrality.csv')
            print("✅ Demo data loaded successfully")
        except Exception as e:
            print(f"⚠️ Could not load some demo data: {e}")
            # Create mock data if files not found
            self.create_mock_demo_data()
    
    def create_mock_demo_data(self):
        """Create mock demo data for testing"""
        # Mock clinical data
        np.random.seed(42)
        n_patients = 200
        self.clinical_data = pd.DataFrame({
            'survival_time': np.random.exponential(1000, n_patients),
            'survival_status': np.random.binomial(1, 0.3, n_patients),
            'age': np.random.normal(60, 10, n_patients),
            'gender': np.random.choice(['M', 'F'], n_patients),
            'stage': np.random.choice(['I', 'II', 'III', 'IV'], n_patients),
            'risk_score': np.random.normal(0, 0.5, n_patients)
        }, index=[f'Patient_{i:03d}' for i in range(n_patients)])
        
        # Mock expression data
        n_genes = 100
        self.expression_data = pd.DataFrame(
            np.random.randn(n_genes, n_patients),
            index=[f'Gene_{i:03d}' for i in range(n_genes)],
            columns=self.clinical_data.index
        )
        
        # Mock multi-omics data
        self.cnv_data = pd.DataFrame(
            np.random.randn(n_genes, n_patients) * 0.5,
            index=self.expression_data.index,
            columns=self.expression_data.columns
        )
        
        self.methylation_data = pd.DataFrame(
            np.random.beta(2, 5, (n_genes, n_patients)),
            index=self.expression_data.index,
            columns=self.expression_data.columns
        )
        
        # Mock mutations data
        mutation_records = []
        for gene_idx in range(n_genes):
            n_mutations = np.random.poisson(3)
            for _ in range(n_mutations):
                patient = np.random.choice(self.clinical_data.index)
                mutation_type = np.random.choice(['missense', 'nonsense', 'frameshift', 'silent'])
                mutation_records.append({
                    'gene_id': f'Gene_{gene_idx:03d}',
                    'sample_id': patient,
                    'mutation_type': mutation_type
                })
        self.mutations_data = pd.DataFrame(mutation_records)
        
        # Mock linchpin data
        gene_names = ['VEGFR2', 'TNF', 'TP53', 'IDH1', 'IL6', 'EGFR', 'MYC', 'PIK3CA', 
                     'KRAS', 'BRAF', 'AKT1', 'MTOR', 'STAT3', 'NF1', 'PTEN', 'RB1', 
                     'CDKN2A', 'ARID1A', 'CTNNB1', 'TERT']
        self.linchpin_data = pd.DataFrame({
            'gene_id': gene_names[:20],
            'linchpin_score': np.random.uniform(0.5, 0.9, 20),
            'prognostic_score': np.random.uniform(0.4, 0.95, 20),
            'network_hub_score': np.random.uniform(0.45, 0.92, 20),
            'cross_domain_score': np.random.uniform(0.4, 0.85, 20),
            'regulator_score': np.random.uniform(0.3, 0.9, 20),
            'druggable': np.random.choice([True, False], 20, p=[0.7, 0.3])
        }).sort_values('linchpin_score', ascending=False)
        
        # Mock network data
        self.network_data = pd.DataFrame({
            'gene_id': gene_names[:50],
            'degree_centrality': np.random.uniform(0.1, 0.9, 50),
            'betweenness_centrality': np.random.uniform(0, 0.5, 50),
            'closeness_centrality': np.random.uniform(0.3, 0.8, 50),
            'eigenvector_centrality': np.random.uniform(0.1, 1, 50)
        })
    
    def setup_styling(self):
        """Setup custom CSS styling"""
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>LIHC Analysis Platform - Professional</title>
                {%favicon%}
                {%css%}
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                <style>
                ''' + self.get_professional_css() + '''
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
        
    def setup_layout(self):
        """Setup the professional layout with top bar and sidebar"""
        self.app.layout = html.Div([
            # Store components
            dcc.Store(id='current-page', data='overview'),
            dcc.Store(id='sidebar-state', data='expanded'),
            dcc.Store(id='language-store', data='zh'),
            dcc.Store(id='current-session-id', data=None),
            
            # Progress modal
            html.Div(
                id='analysis-progress-modal',
                style={'display': 'none'},
                children=[
                    html.Div(
                        id='analysis-progress',
                        className='progress-modal-content'
                    )
                ]
            ),
            
            # Top Navigation Bar
            html.Div([
                # Toggle button for mobile
                html.Button("☰", id="sidebar-toggle", className="sidebar-toggle"),
                
                # Brand
                html.Div("LIHC Analysis Platform", className="brand"),
                
                # Top navigation items
                html.Div([
                    html.Button([
                        html.I(className="fas fa-upload"),
                        html.Span(" 数据上传", id="nav-data-upload")
                    ], id="top-nav-data", className="nav-item"),
                    
                    html.Button([
                        html.I(className="fas fa-database"),
                        html.Span(" 数据集管理", id="nav-dataset-management")
                    ], id="top-nav-datasets", className="nav-item"),
                    
                    html.Button([
                        html.I(className="fas fa-flask"),
                        html.Span(" 测试Demo", id="nav-demo")
                    ], id="top-nav-demo", className="nav-item"),
                    
                    html.Button([
                        html.I(className="fas fa-cog"),
                        html.Span(" 系统设置", id="nav-settings")
                    ], id="top-nav-settings", className="nav-item"),
                    
                    # Language switcher
                    html.Div([
                        html.Button("中文", id="lang-zh", className="lang-btn active"),
                        html.Button("EN", id="lang-en", className="lang-btn"),
                    ], className="language-switcher"),
                ], className="nav-items"),
            ], className="top-navbar"),
            
            # Sidebar Navigation
            html.Div([
                # Analysis section
                html.Div([
                    html.Div("分析功能", className="sidebar-section-title"),
                    
                    html.Button([
                        html.I(className="fas fa-home"),
                        html.Span(" 平台概览", id="side-overview")
                    ], id="sidebar-overview", className="sidebar-item active"),
                    
                    html.Button([
                        html.I(className="fas fa-cubes"),
                        html.Span(" 多维度分析", id="side-multidim")
                    ], id="sidebar-multidim", className="sidebar-item"),
                    
                    html.Button([
                        html.I(className="fas fa-project-diagram"),
                        html.Span(" 网络分析", id="side-network")
                    ], id="sidebar-network", className="sidebar-item"),
                    
                    html.Button([
                        html.I(className="fas fa-crosshairs"),
                        html.Span(" Linchpin靶点", id="side-linchpin")
                    ], id="sidebar-linchpin", className="sidebar-item"),
                    
                    html.Button([
                        html.I(className="fas fa-chart-line"),
                        html.Span(" 生存分析", id="side-survival")
                    ], id="sidebar-survival", className="sidebar-item"),
                ], className="sidebar-section"),
                
                # Advanced Analysis section
                html.Div([
                    html.Div("高级分析", className="sidebar-section-title"),
                    
                    html.Button([
                        html.I(className="fas fa-dna"),
                        html.Span(" 多组学整合", id="side-multiomics")
                    ], id="sidebar-multiomics", className="sidebar-item"),
                    
                    html.Button([
                        html.I(className="fas fa-sync-alt"),
                        html.Span(" ClosedLoop分析", id="side-closedloop")
                    ], id="sidebar-closedloop", className="sidebar-item"),
                    
                    html.Button([
                        html.I(className="fas fa-chart-bar"),
                        html.Span(" 综合图表", id="side-charts")
                    ], id="sidebar-charts", className="sidebar-item"),
                ], className="sidebar-section"),
                
                # Precision Medicine section
                html.Div([
                    html.Div("精准医学", className="sidebar-section-title"),
                    
                    html.Button([
                        html.I(className="fas fa-shield-alt"),
                        html.Span(" 免疫微环境", id="side-immune")
                    ], id="sidebar-immune", className="sidebar-item"),
                    
                    html.Button([
                        html.I(className="fas fa-pills"),
                        html.Span(" 药物响应", id="side-drug")
                    ], id="sidebar-drug", className="sidebar-item"),
                    
                    html.Button([
                        html.I(className="fas fa-layer-group"),
                        html.Span(" 分子分型", id="side-subtype")
                    ], id="sidebar-subtype", className="sidebar-item"),
                    
                    html.Button([
                        html.I(className="fas fa-fire"),
                        html.Span(" 代谢分析", id="side-metabolism")
                    ], id="sidebar-metabolism", className="sidebar-item"),
                    
                    html.Button([
                        html.I(className="fas fa-code-branch"),
                        html.Span(" 异质性分析", id="side-heterogeneity")
                    ], id="sidebar-heterogeneity", className="sidebar-item"),
                ], className="sidebar-section"),
                
                # Results section
                html.Div([
                    html.Div("分析结果", className="sidebar-section-title"),
                    
                    html.Button([
                        html.I(className="fas fa-table"),
                        html.Span(" 结果表格", id="side-tables")
                    ], id="sidebar-tables", className="sidebar-item"),
                    
                    html.Button([
                        html.I(className="fas fa-file-download"),
                        html.Span(" 下载报告", id="side-download")
                    ], id="sidebar-download", className="sidebar-item"),
                    
                    html.Button([
                        html.I(className="fas fa-history"),
                        html.Span(" 历史记录", id="side-history")
                    ], id="sidebar-history", className="sidebar-item"),
                    
                    html.Button([
                        html.I(className="fas fa-layer-group"),
                        html.Span(" 批量处理", id="side-batch")
                    ], id="sidebar-batch", className="sidebar-item"),
                    
                    html.Button([
                        html.I(className="fas fa-tasks"),
                        html.Span(" 任务队列", id="side-taskqueue")
                    ], id="sidebar-taskqueue", className="sidebar-item"),
                ], className="sidebar-section"),
            ], id="sidebar", className="sidebar"),
            
            # Main Content Area
            html.Div([
                html.Div(id="main-content", className="main-content")
            ], className="main-wrapper"),
            
            # Progress tracking components
            dcc.Interval(
                id='analysis-progress-interval',
                interval=1000,  # Update every second
                disabled=True  # Will be enabled when analysis starts
            ),
            
            # Hidden store removed (already exists above)
        ])
    
    def get_professional_css(self):
        """Professional CSS with modern design"""
        return """
        /* CSS Variables */
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --accent-color: #e74c3c;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --light-bg: #ecf0f1;
            --dark-bg: #34495e;
            --text-primary: #2c3e50;
            --text-secondary: #7f8c8d;
            --border-color: #bdc3c7;
            --card-shadow: 0 2px 10px rgba(0,0,0,0.1);
            --hover-shadow: 0 5px 20px rgba(0,0,0,0.15);
            --sidebar-width: 260px;
            --topbar-height: 60px;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f6fa;
            color: var(--text-primary);
        }
        
        /* Top Navigation Bar */
        .top-navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--topbar-height);
            background: var(--dark-bg);
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            z-index: 1000;
            display: flex;
            align-items: center;
            padding: 0 20px;
        }
        
        .sidebar-toggle {
            display: none;
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            margin-right: 20px;
        }
        
        .brand {
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            margin-right: auto;
        }
        
        .nav-items {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .nav-item {
            padding: 8px 16px;
            color: white;
            background: none;
            border: none;
            cursor: pointer;
            transition: background 0.3s;
            border-radius: 5px;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .nav-item:hover {
            background: rgba(255,255,255,0.1);
        }
        
        .nav-item.active {
            background: var(--secondary-color);
        }
        
        .language-switcher {
            display: flex;
            margin-left: 20px;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 5px;
            overflow: hidden;
        }
        
        .lang-btn {
            padding: 5px 15px;
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .lang-btn.active {
            background: var(--secondary-color);
        }
        
        /* Sidebar Navigation */
        .sidebar {
            position: fixed;
            left: 0;
            top: var(--topbar-height);
            bottom: 0;
            width: var(--sidebar-width);
            background: white;
            border-right: 1px solid var(--border-color);
            overflow-y: auto;
            z-index: 999;
            box-shadow: 2px 0 5px rgba(0,0,0,0.05);
        }
        
        .sidebar-section {
            padding: 20px 0;
            border-bottom: 1px solid var(--border-color);
        }
        
        .sidebar-section:last-child {
            border-bottom: none;
        }
        
        .sidebar-section-title {
            padding: 0 20px 10px 20px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 1px;
        }
        
        .sidebar-item {
            display: flex;
            align-items: center;
            width: 100%;
            padding: 12px 20px;
            border: none;
            background: none;
            text-align: left;
            cursor: pointer;
            transition: all 0.3s;
            color: var(--text-primary);
            font-size: 0.95rem;
            gap: 10px;
        }
        
        .sidebar-item:hover {
            background: var(--light-bg);
            padding-left: 25px;
        }
        
        .sidebar-item.active {
            background: var(--secondary-color);
            color: white;
            font-weight: 500;
        }
        
        .sidebar-item i {
            width: 20px;
            text-align: center;
        }
        
        /* Main Content Area */
        .main-wrapper {
            margin-top: var(--topbar-height);
            margin-left: var(--sidebar-width);
            min-height: calc(100vh - var(--topbar-height));
            background: #f5f6fa;
        }
        
        .main-content {
            padding: 30px;
        }
        
        /* Cards */
        .card {
            background: white;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.3s;
            overflow: hidden;
        }
        
        .card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* Prevent graph overflow */
        .js-plotly-plot .plotly .modebar {
            position: absolute !important;
            top: 5px !important;
            right: 5px !important;
        }
        
        .js-plotly-plot {
            overflow: hidden !important;
        }
        
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 16px;
            color: var(--text-primary);
        }
        
        /* Responsive Design */
        @media (max-width: 968px) {
            .sidebar {
                transform: translateX(-100%);
                transition: transform 0.3s;
            }
            
            .sidebar.active {
                transform: translateX(0);
            }
            
            .main-wrapper {
                margin-left: 0;
            }
            
            .sidebar-toggle {
                display: block;
            }
            
            .nav-item span {
                display: none;
            }
            
            .nav-item {
                padding: 8px;
            }
        }
        
        @media (max-width: 640px) {
            .language-switcher {
                display: none;
            }
            
            .brand {
                font-size: 1.2rem;
            }
        }
        
        /* Buttons */
        .btn-primary {
            background: var(--secondary-color);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 500;
        }
        
        .btn-primary:hover {
            background: #2980b9;
            transform: translateY(-1px);
        }
        
        /* Loading state */
        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 400px;
            color: var(--text-secondary);
        }
        
        /* Metric cards for demo */
        .metric-card {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s;
        }
        
        .metric-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        
        .metric-card h3 {
            margin: 10px 0;
            font-size: 2rem;
            font-weight: 600;
        }
        
        .metric-card h5 {
            margin: 0 0 10px 0;
            font-weight: 500;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 1px;
        }
        
        .metric-card p {
            margin: 0;
            color: var(--text-secondary);
        }
        
        /* Task Queue Status Cards */
        .status-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            border: 2px solid;
            transition: all 0.3s;
        }
        
        .status-card.queued {
            border-color: #7f8c8d;
            background: #f8f9fa;
        }
        
        .status-card.active {
            border-color: #3498db;
            background: #ebf5ff;
        }
        
        .status-card.scheduled {
            border-color: #f39c12;
            background: #fef5e7;
        }
        
        .status-card.failed {
            border-color: #e74c3c;
            background: #fdedec;
        }
        
        .status-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .primary-button {
            background: var(--secondary-color);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 500;
        }
        
        .primary-button:hover {
            background: #2980b9;
            box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
        }
        
        .small-button {
            background: var(--secondary-color);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.3s;
        }
        
        .small-button:hover:not(:disabled) {
            background: #2980b9;
        }
        
        .small-button:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
        }
        """
    
    def setup_callbacks(self):
        """Setup callbacks for navigation and content"""
        
        # Sidebar toggle for mobile
        @self.app.callback(
            Output('sidebar', 'className'),
            Input('sidebar-toggle', 'n_clicks'),
            State('sidebar', 'className'),
            prevent_initial_call=True
        )
        def toggle_sidebar(n_clicks, current_class):
            if n_clicks:
                if 'active' in current_class:
                    return 'sidebar'
                else:
                    return 'sidebar active'
            return 'sidebar'
        
        # Language switching
        @self.app.callback(
            [Output('lang-zh', 'className'),
             Output('lang-en', 'className'),
             Output('language-store', 'data')],
            [Input('lang-zh', 'n_clicks'),
             Input('lang-en', 'n_clicks')],
            State('language-store', 'data'),
            prevent_initial_call=True
        )
        def switch_language(zh_clicks, en_clicks, current_lang):
            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'lang-zh':
                i18n.set_language('zh')
                return 'lang-btn active', 'lang-btn', 'zh'
            else:
                i18n.set_language('en')
                return 'lang-btn', 'lang-btn active', 'en'
        
        # Main content routing
        @self.app.callback(
            [Output('main-content', 'children'),
             Output('current-page', 'data')] + 
            [Output(f'sidebar-{page}', 'className') for page in 
             ['overview', 'multidim', 'network', 'linchpin', 'survival', 
              'multiomics', 'closedloop', 'charts', 'immune', 'drug', 'subtype', 
              'metabolism', 'heterogeneity', 'tables', 'download', 'history', 'batch', 'taskqueue']],
            [Input(f'sidebar-{page}', 'n_clicks') for page in 
             ['overview', 'multidim', 'network', 'linchpin', 'survival', 
              'multiomics', 'closedloop', 'charts', 'immune', 'drug', 'subtype', 
              'metabolism', 'heterogeneity', 'tables', 'download', 'history', 'batch', 'taskqueue']] +
            [Input(f'top-nav-{page}', 'n_clicks') for page in ['data', 'demo', 'settings']],
            State('current-page', 'data')
        )
        def update_content(*args):
            ctx = dash.callback_context
            if not ctx.triggered:
                # Return default overview page
                return self.create_overview_content(), 'overview', *(['sidebar-item active'] + ['sidebar-item'] * 17)
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            # Map button IDs to content
            content_map = {
                'sidebar-overview': ('overview', self.create_overview_content()),
                'sidebar-multidim': ('multidim', self.create_multidim_content()),
                'sidebar-network': ('network', self.create_network_content()),
                'sidebar-linchpin': ('linchpin', self.create_linchpin_content()),
                'sidebar-survival': ('survival', self.create_survival_content()),
                'sidebar-multiomics': ('multiomics', self.create_multiomics_content()),
                'sidebar-closedloop': ('closedloop', self.create_closedloop_content()),
                'sidebar-charts': ('charts', self.create_charts_content()),
                'sidebar-immune': ('immune', self.create_immune_content()),
                'sidebar-drug': ('drug', self.create_drug_content()),
                'sidebar-subtype': ('subtype', self.create_subtype_content()),
                'sidebar-metabolism': ('metabolism', self.create_metabolism_content()),
                'sidebar-heterogeneity': ('heterogeneity', self.create_heterogeneity_content()),
                'sidebar-tables': ('tables', self.create_tables_content()),
                'sidebar-download': ('download', self.create_download_content()),
                'sidebar-history': ('history', self.create_history_content()),
                'sidebar-batch': ('batch', self.create_batch_content()),
                'sidebar-taskqueue': ('taskqueue', self.create_taskqueue_content()),
                'top-nav-data': ('data-upload', self.create_data_management_content()),
                'top-nav-datasets': ('dataset-management', self.create_dataset_management_content()),
                'top-nav-demo': ('demo', self.create_demo_content()),
                'top-nav-settings': ('settings', self.create_settings_content()),
            }
            
            if button_id in content_map:
                page_id, content = content_map[button_id]
                
                # Update sidebar button states
                sidebar_classes = []
                sidebar_pages = ['overview', 'multidim', 'network', 'linchpin', 'survival', 
                               'multiomics', 'closedloop', 'charts', 'immune', 'drug', 'subtype',
                               'metabolism', 'heterogeneity', 'tables', 'download', 'history', 'batch', 'taskqueue']
                
                for page in sidebar_pages:
                    if f'sidebar-{page}' == button_id:
                        sidebar_classes.append('sidebar-item active')
                    else:
                        sidebar_classes.append('sidebar-item')
                
                return content, page_id, *sidebar_classes
            
            return no_update
        
        # Template download callbacks
        @self.app.callback(
            Output('download-clinical', 'data'),
            Input('download-clinical-template', 'n_clicks'),
            prevent_initial_call=True
        )
        def download_clinical_template(n_clicks):
            if self.upload_manager:
                templates = self.upload_manager.get_upload_template()
                df = templates['clinical']
                return dcc.send_data_frame(df.to_csv, "clinical_template.csv")
            return no_update
        
        @self.app.callback(
            Output('download-expression', 'data'),
            Input('download-expression-template', 'n_clicks'),
            prevent_initial_call=True
        )
        def download_expression_template(n_clicks):
            if self.upload_manager:
                templates = self.upload_manager.get_upload_template()
                df = templates['expression']
                return dcc.send_data_frame(df.to_csv, "expression_template.csv")
            return no_update
        
        @self.app.callback(
            Output('download-mutation', 'data'),
            Input('download-mutation-template', 'n_clicks'),
            prevent_initial_call=True
        )
        def download_mutation_template(n_clicks):
            if self.upload_manager:
                templates = self.upload_manager.get_upload_template()
                df = templates['mutation']
                return dcc.send_data_frame(df.to_csv, "mutation_template.csv")
            return no_update
        
        @self.app.callback(
            Output('download-templates-zip', 'data'),
            Input('download-all-templates', 'n_clicks'),
            prevent_initial_call=True
        )
        def download_all_templates(n_clicks):
            if self.upload_manager:
                templates = self.upload_manager.get_upload_template()
                
                # Create zip file in memory
                import io
                import zipfile
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Add each template
                    for name, df in templates.items():
                        if name != 'instructions':
                            csv_buffer = io.StringIO()
                            df.to_csv(csv_buffer)
                            zip_file.writestr(f'{name}_template.csv', csv_buffer.getvalue())
                    
                    # Add instructions
                    instructions_text = "LIHC数据上传模板说明\n\n"
                    for data_type, instruction in templates['instructions'].items():
                        instructions_text += f"{data_type.upper()}数据要求：\n{instruction}\n\n"
                    zip_file.writestr('README.txt', instructions_text)
                
                zip_buffer.seek(0)
                return dcc.send_bytes(zip_buffer.getvalue(), "lihc_templates.zip")
            return no_update
        
        # File upload and validation callbacks
        @self.app.callback(
            [Output('upload-status', 'children'),
             Output('validation-results', 'style'),
             Output('validation-content', 'children'),
             Output('analysis-section', 'style'),
             Output('user-session-id', 'data')],
            Input('upload-data', 'contents'),
            [State('upload-data', 'filename'),
             State('dataset-name-input', 'value')],
            prevent_initial_call=True
        )
        def handle_upload(contents_list, filenames, dataset_name):
            if not contents_list or not self.upload_manager:
                return no_update, no_update, no_update, no_update, no_update
            
            # Generate session ID
            import uuid
            session_id = str(uuid.uuid4())
            
            # Process uploaded files
            validation_results = []
            files_info = []
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Save uploaded files
                for content, filename in zip(contents_list, filenames):
                    content_type, content_string = content.split(',')
                    decoded = base64.b64decode(content_string)
                    
                    file_path = temp_path / filename
                    with open(file_path, 'wb') as f:
                        f.write(decoded)
                    
                    # Validate file
                    data_type = self.upload_manager._identify_data_type(file_path)
                    if data_type:
                        result = self.upload_manager.validate_file_format(file_path, data_type)
                        validation_results.append({
                            'filename': filename,
                            'data_type': data_type,
                            'result': result
                        })
                
                # Process as package
                package_result = self.upload_manager.process_upload_package(
                    temp_path if len(filenames) > 1 else temp_path / filenames[0],
                    session_id
                )
                
                # Save to history if successful
                if self.history_manager and package_result['success']:
                    self.history_manager.add_upload_record(session_id, package_result)
                
                # Add to dataset manager
                if self.dataset_manager and package_result['success']:
                    self.dataset_manager.add_user_dataset(session_id, name=dataset_name)
            
            # Create status display
            status_elements = []
            
            if package_result['success']:
                status_elements.append(
                    html.Div([
                        html.I(className="fas fa-check-circle", 
                              style={'color': 'green', 'fontSize': '24px'}),
                        html.H4(" 数据上传成功！", style={'color': 'green', 'display': 'inline'})
                    ])
                )
            else:
                status_elements.append(
                    html.Div([
                        html.I(className="fas fa-exclamation-circle", 
                              style={'color': 'red', 'fontSize': '24px'}),
                        html.H4(" 数据验证发现问题", style={'color': 'red', 'display': 'inline'})
                    ])
                )
            
            # Validation details
            validation_elements = []
            
            for file_info in validation_results:
                file_status = "✅" if file_info['result']['valid'] else "❌"
                validation_elements.append(
                    html.Div([
                        html.H5(f"{file_status} {file_info['filename']}"),
                        html.P(f"数据类型: {file_info['data_type']}"),
                        
                        # Show info
                        html.Div([
                            html.P(f"数据维度: {file_info['result']['info'].get('shape', 'N/A')}"),
                        ], style={'marginLeft': '20px'}),
                        
                        # Show errors
                        *[html.P(f"❌ {error}", style={'color': 'red', 'marginLeft': '20px'}) 
                          for error in file_info['result'].get('errors', [])],
                        
                        # Show warnings
                        *[html.P(f"⚠️ {warning}", style={'color': 'orange', 'marginLeft': '20px'}) 
                          for warning in file_info['result'].get('warnings', [])],
                        
                        html.Hr()
                    ])
                )
            
            # Show validation results and analysis section if successful
            validation_style = {'display': 'block'}
            analysis_style = {'display': 'block'} if package_result['success'] else {'display': 'none'}
            
            return (
                status_elements,
                validation_style,
                validation_elements,
                analysis_style,
                session_id
            )
        
        # Reset upload callback
        @self.app.callback(
            [Output('upload-data', 'contents'),
             Output('upload-data', 'filename'),
             Output('upload-status', 'children', allow_duplicate=True),
             Output('validation-results', 'style', allow_duplicate=True),
             Output('analysis-section', 'style', allow_duplicate=True)],
            Input('reset-upload', 'n_clicks'),
            prevent_initial_call=True
        )
        def reset_upload(n_clicks):
            return None, None, [], {'display': 'none'}, {'display': 'none'}
        
        # Start analysis callback with progress tracking
        @self.app.callback(
            [Output('analysis-progress', 'children', allow_duplicate=True),
             Output('analysis-progress-interval', 'disabled'),
             Output('current-session-id', 'data'),
             Output('analysis-progress-modal', 'style')],
            Input('start-analysis', 'n_clicks'),
            [State('user-session-id', 'data'),
             State('analysis-modules', 'value')],
            prevent_initial_call=True
        )
        def start_analysis(n_clicks, session_id, selected_modules):
            if not n_clicks:
                return no_update, no_update, no_update, no_update
            
            # Test if callback is triggered
            if not selected_modules:
                selected_modules = []
            
            # Enable progress interval and show modal
            modal_style = {
                'display': 'block',
                'position': 'fixed',
                'top': '50%',
                'left': '50%',
                'transform': 'translate(-50%, -50%)',
                'backgroundColor': 'white',
                'padding': '30px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'zIndex': '1001',
                'maxWidth': '600px',
                'width': '90%',
                'maxHeight': '80vh',
                'overflowY': 'auto'
            }
            
            progress_elements = []
            
            # Show initial progress
            progress_elements.append(
                html.Div([
                    html.H4([html.I(className="fas fa-spinner fa-spin"), " 分析进行中..."],
                           style={'color': '#3498db'}),
                    html.P(f"会话ID: {session_id[:8] if session_id else 'Demo'}...", style={'fontSize': '0.9rem', 'color': '#666'}),
                    html.Hr()
                ])
            )
            
            # Run actual analysis if session_id exists
            analysis_error = None
            if session_id:
                try:
                    # Initialize progress manager if available
                    if PROGRESS_AVAILABLE:
                        from src.analysis.progress_manager import ProgressManager
                        progress_manager = ProgressManager(session_id)
                        progress_manager.start_analysis(selected_modules)
                    
                    # Try to use advanced analyzer first
                    try:
                        from src.analysis.advanced_analyzer import AdvancedAnalyzer
                        from src.analysis.simplified_analyzer import SimplifiedAnalyzer
                        
                        # SimplifiedAnalyzer handles the decision to use AdvancedAnalyzer
                        analyzer = SimplifiedAnalyzer(session_id)
                        analysis_results = analyzer.run_all_analyses(selected_modules)
                    except ImportError:
                        # Fallback to simplified analyzer only
                        from src.analysis.simplified_analyzer import SimplifiedAnalyzer
                        analyzer = SimplifiedAnalyzer(session_id)
                        analysis_results = analyzer.run_all_analyses(selected_modules)
                    
                    if 'error' not in analysis_results:
                        # Add success message with actual results
                        progress_elements.append(
                            html.Div([
                                html.H5("✅ 分析结果已生成", style={'color': 'green'}),
                                html.P(f"结果文件数: {analysis_results.get('results_count', 0)}"),
                                html.P(f"报告位置: {analysis_results.get('report_path', 'N/A')}"),
                                html.Hr()
                            ])
                        )
                    else:
                        analysis_error = analysis_results['error']
                except Exception as e:
                    analysis_error = str(e)
            
            # Create progress indicators for each module
            module_info = {
                'stage1': {
                    'name': 'Stage 1: 多维度生物学分析',
                    'icon': 'fa-dna',
                    'steps': ['加载数据', '五维度分析', '生成报告']
                },
                'stage2': {
                    'name': 'Stage 2: 跨维度网络分析',
                    'icon': 'fa-project-diagram',
                    'steps': ['构建网络', '计算中心性', '识别关键节点']
                },
                'stage3': {
                    'name': 'Stage 3: Linchpin基因识别',
                    'icon': 'fa-bullseye',
                    'steps': ['整合分析', '靶点评分', '优先级排序']
                },
                'precision': {
                    'name': '精准医学分析',
                    'icon': 'fa-microscope',
                    'steps': ['免疫分析', '药物预测', '分子分型', '代谢分析', '异质性分析']
                }
            }
            
            for module in selected_modules:
                if module in module_info:
                    info = module_info[module]
                    progress_elements.append(
                        html.Div([
                            html.H5([
                                html.I(className=f"fas {info['icon']}"),
                                f" {info['name']}"
                            ], style={'marginBottom': '10px'}),
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-check-circle", 
                                          style={'color': 'green', 'marginRight': '5px'}),
                                    step
                                ], style={'padding': '5px 0'})
                                for step in info['steps']
                            ], style={'marginLeft': '20px', 'fontSize': '0.9rem'}),
                            html.Hr()
                        ])
                    )
            
            # Add completion or error message
            if analysis_error:
                progress_elements.append(
                    html.Div([
                        html.H4([
                            html.I(className="fas fa-exclamation-circle", style={'color': 'red'}),
                            " 分析出错"
                        ], style={'color': 'red', 'marginTop': '20px'}),
                        html.P(f"错误信息: {analysis_error}"),
                        html.P("请检查数据格式或联系技术支持。")
                    ])
                )
            else:
                progress_elements.append(
                    html.Div([
                        html.H4([
                            html.I(className="fas fa-check-circle", style={'color': 'green'}),
                            " 分析完成！"
                        ], style={'color': 'green', 'marginTop': '20px'}),
                        html.P("分析结果已保存，请在相应的分析页面查看结果。"),
                        html.Div([
                            html.P("🔍 查看结果："),
                            html.Ul([
                                html.Li("基础分析 → 查看Stage 1-3结果"),
                                html.Li("高级分析 → 查看多组学整合结果"),
                                html.Li("精准医学 → 查看个性化分析结果"),
                                html.Li("结果下载 → 下载完整分析报告"),
                                html.Li("历史记录 → 查看所有分析历史")
                            ])
                        ], style={'backgroundColor': '#f0f8ff', 'padding': '15px', 
                                 'borderRadius': '5px', 'marginTop': '15px'})
                    ])
                )
            
            # Save analysis record to history
            if self.history_manager and session_id:
                analysis_info = {
                    'modules': selected_modules,
                    'status': 'completed',
                    'duration': '演示模式'
                }
                self.history_manager.add_analysis_record(session_id, analysis_info)
            
            # In a real implementation, you would:
            # 1. Create UserDataAnalyzer instance
            # 2. Run actual analysis pipeline
            # 3. Update progress in real-time
            # 4. Save results to user directory
            
            # Return progress elements, disable interval when done, store session ID, and show modal
            return (progress_elements, 
                    True,  # Disable interval when analysis is complete
                    session_id,  # Store current session ID
                    modal_style if not analysis_error else {'display': 'none'})
        
        # History export callback
        @self.app.callback(
            Output('download-history', 'data'),
            Input('export-history', 'n_clicks'),
            prevent_initial_call=True
        )
        def export_history(n_clicks):
            if not n_clicks or not self.history_manager:
                return no_update
            
            # Export history to CSV
            export_path = self.history_manager.export_history(format='csv')
            
            # Create a zip file with both uploads and analyses history
            import io
            import zipfile
            import os
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file in export_path.glob('*.csv'):
                    zip_file.write(file, file.name)
            
            zip_buffer.seek(0)
            return dcc.send_bytes(zip_buffer.getvalue(), "history_export.zip")
        
        # Refresh history callback
        @self.app.callback(
            [Output('sidebar-history', 'n_clicks'),
             Output('current-page', 'data', allow_duplicate=True)],
            Input('refresh-history', 'n_clicks'),
            prevent_initial_call=True
        )
        def refresh_history(n_clicks):
            if not n_clicks:
                return no_update, no_update
            # Trigger a page refresh by simulating a click on history sidebar
            return 1, 'history'
        
        # View results callback
        @self.app.callback(
            [Output('result-viewer-modal', 'style'),
             Output('result-viewer-content', 'children')],
            [Input({'type': 'view-results-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
            [State({'type': 'view-results-btn', 'index': dash.dependencies.ALL}, 'id')],
            prevent_initial_call=True
        )
        def view_results(n_clicks_list, id_list):
            if not any(n_clicks_list):
                return no_update, no_update
            
            # Find which button was clicked
            ctx = dash.callback_context
            if not ctx.triggered:
                return no_update, no_update
            
            # Get session_id from the clicked button
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            import json
            button_dict = json.loads(button_id)
            session_id = button_dict['index']
            
            # Load analysis results
            results_dir = Path(f"data/history/{session_id}/results")
            
            if not results_dir.exists():
                return {'display': 'block'}, html.Div([
                    html.P("未找到分析结果文件", style={'color': 'red'}),
                    html.P(f"会话ID: {session_id}")
                ])
            
            # Create content to display
            content = []
            
            # Add session info
            content.append(html.H4(f"会话: {session_id[:8]}..."))
            
            # Check for HTML report
            report_path = results_dir / "analysis_report.html"
            if report_path.exists():
                try:
                    with open(report_path, 'r', encoding='utf-8') as f:
                        report_content = f.read()
                    content.append(html.Div([
                        html.H5("📄 分析报告"),
                        html.Iframe(srcDoc=report_content, 
                                  style={'width': '100%', 'height': '600px', 'border': '1px solid #ddd'})
                    ]))
                except Exception as e:
                    content.append(html.P(f"无法加载报告: {str(e)}", style={'color': 'red'}))
            
            # List all result files
            content.append(html.H5("📁 生成的文件:"))
            file_list = []
            for file in results_dir.glob("*"):
                if file.is_file():
                    file_list.append(html.Li(f"{file.name} ({file.stat().st_size / 1024:.1f} KB)"))
            
            if file_list:
                content.append(html.Ul(file_list))
            
            # Add JSON results preview
            for json_file in results_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    
                    content.append(html.Details([
                        html.Summary(f"📊 {json_file.name}"),
                        html.Pre(json.dumps(data, indent=2, ensure_ascii=False)[:1000] + "...",
                               style={'backgroundColor': '#f5f5f5', 'padding': '10px',
                                     'borderRadius': '5px', 'overflow': 'auto'})
                    ], style={'marginTop': '10px'}))
                except:
                    pass
            
            # Add images
            import base64
            for img_file in results_dir.glob("*.png"):
                try:
                    with open(img_file, 'rb') as f:
                        img_data = base64.b64encode(f.read()).decode()
                    content.append(html.Div([
                        html.H5(f"📊 {img_file.stem.replace('_', ' ').title()}"),
                        html.Img(src=f"data:image/png;base64,{img_data}",
                               style={'maxWidth': '100%', 'marginBottom': '20px'})
                    ]))
                except Exception as e:
                    content.append(html.P(f"无法加载图片 {img_file.name}: {str(e)}", style={'color': 'red'}))
            
            return {'display': 'block'}, html.Div(content)
        
        # Close result viewer
        @self.app.callback(
            Output('result-viewer-modal', 'style', allow_duplicate=True),
            Input('close-result-viewer', 'n_clicks'),
            prevent_initial_call=True
        )
        def close_result_viewer(n_clicks):
            if n_clicks:
                return {'display': 'none'}
            return no_update
        
        # Download report callback
        @self.app.callback(
            Output('download-report', 'data'),
            [Input({'type': 'download-report-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
            [State({'type': 'download-report-btn', 'index': dash.dependencies.ALL}, 'id')],
            prevent_initial_call=True
        )
        def download_report(n_clicks_list, id_list):
            if not any(n_clicks_list):
                return no_update
            
            # Find which button was clicked
            ctx = dash.callback_context
            if not ctx.triggered:
                return no_update
            
            # Get session_id
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            import json
            button_dict = json.loads(button_id)
            session_id = button_dict['index']
            
            # Create zip file with all results
            results_dir = Path(f"data/history/{session_id}/results")
            if not results_dir.exists():
                return no_update
            
            import io
            import zipfile
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file in results_dir.glob("*"):
                    if file.is_file():
                        zip_file.write(file, file.name)
            
            zip_buffer.seek(0)
            return dcc.send_bytes(zip_buffer.getvalue(), f"analysis_results_{session_id[:8]}.zip")
        
        # Comprehensive dataset selector callback for all pages
        @self.app.callback(
            [
                Output('multidim-analysis-content', 'children'),
                Output('network-analysis-content', 'children', allow_duplicate=True),
                Output('linchpin-analysis-content', 'children', allow_duplicate=True),
                Output('survival-analysis-content', 'children', allow_duplicate=True),
                Output('multiomics-analysis-content', 'children', allow_duplicate=True),
                Output('closedloop-analysis-content', 'children', allow_duplicate=True),
                Output('charts-analysis-content', 'children', allow_duplicate=True),
                Output('immune-analysis-content', 'children', allow_duplicate=True),
                Output('drug-analysis-content', 'children', allow_duplicate=True),
                Output('subtype-analysis-content', 'children', allow_duplicate=True),
                Output('metabolism-analysis-content', 'children', allow_duplicate=True),
                Output('heterogeneity-analysis-content', 'children', allow_duplicate=True)
            ],
            [
                Input('multidim-dataset-selector', 'value'),
                Input('network-dataset-selector', 'value'),
                Input('linchpin-dataset-selector', 'value'),
                Input('survival-dataset-selector', 'value'),
                Input('multiomics-dataset-selector', 'value'),
                Input('closedloop-dataset-selector', 'value'),
                Input('charts-dataset-selector', 'value'),
                Input('immune-dataset-selector', 'value'),
                Input('drug-dataset-selector', 'value'),
                Input('subtype-dataset-selector', 'value'),
                Input('metabolism-dataset-selector', 'value'),
                Input('heterogeneity-dataset-selector', 'value')
            ],
            prevent_initial_call=True
        )
        def switch_dataset(*values):
            # Get which input triggered the callback
            ctx = callback_context
            if not ctx.triggered:
                return [no_update] * 12
            
            # Get the dataset_id from any triggered input
            dataset_id = ctx.triggered[0]['value']
            if not dataset_id or not self.dataset_manager:
                return [no_update] * 12
            
            # Switch current dataset
            self.dataset_manager.set_current_dataset(dataset_id)
            dataset_info = self.dataset_manager.get_current_dataset()
            
            # Determine which output to update based on the triggered input
            triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
            outputs = [no_update] * 12  # Default all outputs to no_update
            
            # Map triggered input to output index
            selector_to_index = {
                'multidim-dataset-selector': 0,
                'network-dataset-selector': 1,
                'linchpin-dataset-selector': 2,
                'survival-dataset-selector': 3,
                'multiomics-dataset-selector': 4,
                'closedloop-dataset-selector': 5,
                'charts-dataset-selector': 6,
                'immune-dataset-selector': 7,
                'drug-dataset-selector': 8,
                'subtype-dataset-selector': 9,
                'metabolism-dataset-selector': 10,
                'heterogeneity-dataset-selector': 11
            }
            
            # Use DataLoader to create dynamic content if available
            if DATALOADER_AVAILABLE and data_loader:
                try:
                    # Load the dataset
                    data = data_loader.load_dataset(dataset_id, dataset_info)
                    
                    # Create content based on the triggered selector
                    if triggered_id == 'multidim-dataset-selector':
                        content = self._create_dynamic_multidim_content(data, dataset_info)
                    elif triggered_id == 'survival-dataset-selector':
                        content = self._create_dynamic_survival_content(data, dataset_info)
                    elif triggered_id == 'network-dataset-selector':
                        content = self._create_dynamic_network_content(data, dataset_info)
                    elif triggered_id == 'linchpin-dataset-selector':
                        content = self._create_dynamic_linchpin_content(data, dataset_info)
                    elif triggered_id == 'multiomics-dataset-selector':
                        content = self._create_dynamic_multiomics_content(data, dataset_info)
                    elif triggered_id == 'immune-dataset-selector':
                        content = self._create_dynamic_immune_content(data, dataset_info)
                    elif triggered_id == 'drug-dataset-selector':
                        content = self._create_dynamic_drug_content(data, dataset_info)
                    elif triggered_id == 'subtype-dataset-selector':
                        content = self._create_dynamic_subtype_content(data, dataset_info)
                    else:
                        # Default content for other selectors
                        content = self._create_default_dataset_content(dataset_info)
                    
                    # Update only the relevant output
                    if triggered_id in selector_to_index:
                        outputs[selector_to_index[triggered_id]] = content
                    
                    return outputs
                    
                except Exception as e:
                    print(f"Error loading dynamic content: {e}")
                    # Fall back to default behavior
            
            # Default success message
            success_msg = html.Div([
                html.Div([
                    html.I(className="fas fa-check-circle", style={'color': 'green', 'marginRight': '10px'}),
                    html.Span(f"已切换到数据集: {dataset_info['name']}", style={'fontWeight': 'bold'})
                ], style={'backgroundColor': '#d4edda', 'padding': '10px', 'borderRadius': '5px', 
                         'marginBottom': '20px'}),
                
                html.H4("数据集信息"),
                html.Ul([
                    html.Li(f"类型: {dataset_info['type']}"),
                    html.Li(f"创建时间: {dataset_info.get('created', 'N/A')}"),
                    html.Li(f"样本数: {dataset_info['features']['samples']}"),
                    html.Li(f"基因数: {dataset_info['features']['genes']}"),
                ]),
                
                html.Hr(),
                
                html.P("分析功能将基于此数据集运行。请点击相应的分析按钮开始分析。"),
                
                html.Button([
                    html.I(className="fas fa-play"),
                    " 运行分析"
                ], className="btn btn-primary", id="run-analysis-from-dataset")
            ])
            
            # Update only the relevant output
            if triggered_id in selector_to_index:
                outputs[selector_to_index[triggered_id]] = success_msg
            
            return outputs
        
        # Table content callback
        @self.app.callback(
            Output('table-content', 'children'),
            [Input('table-tabs', 'value')],
            prevent_initial_call=False
        )
        def update_table_content(active_tab):
            if active_tab == 'clinical':
                # Load clinical data
                if hasattr(self, 'clinical_data'):
                    return html.Div([
                        html.H4("临床数据表"),
                        dash_table.DataTable(
                            id='clinical-table',
                            columns=[{"name": i, "id": i} for i in self.clinical_data.columns],
                            data=self.clinical_data.to_dict('records'),
                            filter_action="native",
                            sort_action="native",
                            page_action="native",
                            page_size=20,
                            style_cell={'textAlign': 'left'},
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                }
                            ],
                            export_format='csv'
                        )
                    ])
                else:
                    return html.P("没有可用的临床数据", style={'color': '#999'})
            
            elif active_tab == 'expression':
                # Load expression data (show top genes)
                if hasattr(self, 'expression_data'):
                    # Show top 100 variable genes
                    var_genes = self.expression_data.var(axis=1).nlargest(100)
                    display_data = self.expression_data.loc[var_genes.index].T
                    
                    return html.Div([
                        html.H4("基因表达数据 (Top 100变异基因)"),
                        dash_table.DataTable(
                            id='expression-table',
                            columns=[{"name": "Sample", "id": "Sample"}] + 
                                   [{"name": gene, "id": gene} for gene in display_data.columns[:20]],
                            data=[{"Sample": idx, **row.to_dict()} 
                                 for idx, row in display_data.iterrows()],
                            filter_action="native",
                            sort_action="native",
                            page_action="native",
                            page_size=15,
                            style_cell={'textAlign': 'left', 'minWidth': '100px'},
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                }
                            ],
                            export_format='csv'
                        )
                    ])
                else:
                    return html.P("没有可用的表达数据", style={'color': '#999'})
            
            elif active_tab == 'mutation':
                # Create mutation summary table
                mutation_summary = pd.DataFrame({
                    'Gene': ['TP53', 'CTNNB1', 'AXIN1', 'ARID1A', 'TERT'],
                    'Mutation_Count': [85, 65, 45, 40, 35],
                    'Percentage': ['42.5%', '32.5%', '22.5%', '20.0%', '17.5%'],
                    'Most_Common_Type': ['Missense', 'Missense', 'Nonsense', 'Frameshift', 'Promoter']
                })
                
                return html.Div([
                    html.H4("突变汇总表"),
                    dash_table.DataTable(
                        id='mutation-table',
                        columns=[{"name": i, "id": i} for i in mutation_summary.columns],
                        data=mutation_summary.to_dict('records'),
                        sort_action="native",
                        style_cell={'textAlign': 'left'},
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'Mutation_Count'},
                                'backgroundColor': '#e3f2fd'
                            }
                        ]
                    )
                ])
            
            elif active_tab == 'results':
                # Show analysis results summary
                results_summary = pd.DataFrame({
                    'Analysis_Module': ['Stage1', 'Stage2', 'Stage3', 'Precision Medicine'],
                    'Status': ['✅ 完成', '✅ 完成', '✅ 完成', '✅ 完成'],
                    'Key_Finding': [
                        '500个差异表达基因',
                        '15个关键网络模块',
                        '10个Linchpin靶点',
                        '4种潜在治疗方案'
                    ],
                    'Time': ['2 min', '3 min', '2 min', '1 min']
                })
                
                return html.Div([
                    html.H4("分析结果汇总"),
                    dash_table.DataTable(
                        id='results-table',
                        columns=[{"name": i, "id": i} for i in results_summary.columns],
                        data=results_summary.to_dict('records'),
                        style_cell={'textAlign': 'left'},
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'Status'},
                                'color': 'green'
                            }
                        ]
                    )
                ])
            
            return html.P("请选择要查看的数据类型")
        
        # Export callbacks
        @self.app.callback(
            Output('table-download', 'data'),
            [Input('export-csv', 'n_clicks'),
             Input('export-excel', 'n_clicks')],
            [State('table-tabs', 'value')],
            prevent_initial_call=True
        )
        def export_table_data(csv_clicks, excel_clicks, active_tab):
            ctx = dash.callback_context
            if not ctx.triggered:
                return no_update
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            # Get data based on active tab
            if active_tab == 'clinical' and hasattr(self, 'clinical_data'):
                df = self.clinical_data
                filename = "clinical_data"
            elif active_tab == 'expression' and hasattr(self, 'expression_data'):
                df = self.expression_data.T  # Transpose for better readability
                filename = "expression_data"
            else:
                return no_update
            
            if button_id == 'export-csv':
                return dcc.send_data_frame(df.to_csv, f"{filename}.csv")
            elif button_id == 'export-excel':
                return dcc.send_data_frame(df.to_excel, f"{filename}.xlsx")
            
            return no_update
        
        # Settings callbacks
        @self.app.callback(
            Output('settings-status', 'children'),
            [Input('save-settings', 'n_clicks'),
             Input('reset-settings', 'n_clicks')],
            [State('language-selector', 'value'),
             State('report-language', 'value'),
             State('pvalue-threshold', 'value'),
             State('foldchange-threshold', 'value'),
             State('min-samples', 'value'),
             State('color-scheme', 'value'),
             State('chart-size', 'value'),
             State('system-options', 'value')],
            prevent_initial_call=True
        )
        def handle_settings(save_clicks, reset_clicks, lang, report_lang, pvalue, 
                          fc, min_samples, color, size, options):
            ctx = dash.callback_context
            if not ctx.triggered:
                return no_update
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'save-settings':
                # Save settings to file
                settings = {
                    'language': lang,
                    'report_language': report_lang,
                    'analysis': {
                        'pvalue_threshold': pvalue,
                        'foldchange_threshold': fc,
                        'min_samples': min_samples
                    },
                    'visualization': {
                        'color_scheme': color,
                        'chart_size': size
                    },
                    'system': options
                }
                
                # Save to config file
                import json
                config_path = Path('config/user_settings.json')
                config_path.parent.mkdir(exist_ok=True)
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                
                return html.Div([
                    html.I(className="fas fa-check-circle", style={'color': 'green', 'marginRight': '10px'}),
                    "设置已保存成功！"
                ], style={'color': 'green', 'padding': '10px', 'backgroundColor': '#d4edda',
                         'borderRadius': '5px', 'marginTop': '10px'})
            
            elif button_id == 'reset-settings':
                return html.Div([
                    html.I(className="fas fa-info-circle", style={'color': 'blue', 'marginRight': '10px'}),
                    "请刷新页面以恢复默认设置"
                ], style={'color': 'blue', 'padding': '10px', 'backgroundColor': '#cce5ff',
                         'borderRadius': '5px', 'marginTop': '10px'})
            
            return no_update
        
        # Download callbacks
        @self.app.callback(
            Output('download-output', 'data'),
            [Input('download-full-report', 'n_clicks'),
             Input('download-all-charts', 'n_clicks'),
             Input('download-all-tables', 'n_clicks'),
             Input('download-all-zip', 'n_clicks'),
             Input({'type': 'download-result', 'index': dash.dependencies.ALL}, 'n_clicks')],
            prevent_initial_call=True
        )
        def handle_downloads(report_clicks, charts_clicks, tables_clicks, zip_clicks, result_clicks):
            ctx = dash.callback_context
            if not ctx.triggered:
                return no_update
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'download-full-report':
                # Generate and download full report
                return self.generate_full_report()
            
            elif button_id == 'download-all-charts':
                # Package all charts
                return self.package_all_charts()
            
            elif button_id == 'download-all-tables':
                # Export all tables
                return self.export_all_tables()
            
            elif button_id == 'download-all-zip':
                # Create complete package
                return self.create_complete_package()
            
            elif 'download-result' in button_id:
                # Download specific result
                import json
                button_dict = json.loads(button_id)
                session_id = button_dict['index']
                return self.download_session_results(session_id)
            
            return no_update
        
        # Progress tracking callback
        if PROGRESS_AVAILABLE:
            # Create progress update callback
            create_progress_callback(self.app, None)
    
    # Helper methods for downloads
    def generate_full_report(self):
        """Generate complete analysis report"""
        # This would generate a PDF/HTML report
        # For now, return a sample
        content = """
        # LIHC 分析报告
        
        ## 执行摘要
        本次分析完成了...
        
        ## 主要发现
        1. 差异表达基因
        2. 生存分析结果
        3. 网络分析
        """
        return dcc.send_string(content, "analysis_report.md")
    
    def package_all_charts(self):
        """Package all charts into a zip file"""
        # Would collect all generated charts
        # For now, return a sample message
        import io
        import zipfile
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr("charts/readme.txt", "All analysis charts")
        
        zip_buffer.seek(0)
        return dcc.send_bytes(zip_buffer.getvalue(), "all_charts.zip")
    
    def export_all_tables(self):
        """Export all data tables"""
        # Would export all tables to Excel
        if hasattr(self, 'clinical_data'):
            return dcc.send_data_frame(self.clinical_data.to_excel, "all_tables.xlsx")
        return no_update
    
    def create_complete_package(self):
        """Create complete analysis package"""
        import io
        import zipfile
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr("README.txt", "Complete LIHC Analysis Package")
            zip_file.writestr("report/analysis_report.html", "<h1>Analysis Report</h1>")
            zip_file.writestr("data/clinical.csv", "sample,data")
            zip_file.writestr("charts/heatmap.png", b"")
        
        zip_buffer.seek(0)
        return dcc.send_bytes(zip_buffer.getvalue(), "lihc_analysis_complete.zip")
    
    def download_session_results(self, session_id):
        """Download results for specific session"""
        results_dir = Path(f"data/history/{session_id}/results")
        if results_dir.exists():
            import io
            import zipfile
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for file in results_dir.glob("*"):
                    if file.is_file():
                        zip_file.write(file, file.name)
            
            zip_buffer.seek(0)
            return dcc.send_bytes(zip_buffer.getvalue(), f"results_{session_id[:8]}.zip")
        
        return no_update
        
        # Batch processing callbacks
        @self.app.callback(
            Output('batch-dataset-selection', 'options'),
            [Input('current-page', 'data'),
             Input('upload-status', 'children')],
            prevent_initial_call=False
        )
        def update_batch_dataset_options(current_page, upload_status):
            """Update available datasets for batch processing"""
            if not self.dataset_manager:
                return []
            
            datasets = self.dataset_manager.list_datasets()
            options = []
            
            for ds in datasets:
                label = f"{ds['name']} ({ds['type']})"
                if ds.get('upload_time'):
                    label += f" - {ds['upload_time']}"
                options.append({'label': label, 'value': ds['id']})
            
            return options
        
        @self.app.callback(
            [Output('batch-job-status', 'children'),
             Output('batch-job-id', 'data')],
            [Input('start-batch-analysis', 'n_clicks')],
            [State('batch-dataset-selection', 'value'),
             State('batch-modules-selection', 'value')],
            prevent_initial_call=True
        )
        def start_batch_processing(n_clicks, selected_datasets, selected_modules):
            """Start batch processing job"""
            if not n_clicks or not selected_datasets or not selected_modules:
                return no_update, no_update
            
            try:
                from src.analysis.batch_processor import batch_processor
                
                # Create batch job
                job_id = batch_processor.create_batch_job(
                    selected_datasets, 
                    selected_modules,
                    self.dataset_manager
                )
                
                # Start processing in background thread
                import threading
                thread = threading.Thread(
                    target=batch_processor.process_batch,
                    args=(job_id, self.dataset_manager)
                )
                thread.daemon = True
                thread.start()
                
                # Return status message
                status_msg = html.Div([
                    html.Div([
                        html.I(className="fas fa-check-circle", 
                              style={'color': '#27ae60', 'fontSize': '24px', 'marginRight': '10px'}),
                        html.Span("批量处理作业已启动!", style={'fontSize': '18px', 'fontWeight': 'bold'})
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '15px'}),
                    
                    html.Div([
                        html.P([
                            html.I(className="fas fa-id-badge", style={'marginRight': '5px'}),
                            f"作业ID: {job_id[:8]}..."
                        ], style={'marginBottom': '5px'}),
                        html.P([
                            html.I(className="fas fa-database", style={'marginRight': '5px'}),
                            f"处理数据集: {len(selected_datasets)} 个"
                        ], style={'marginBottom': '5px'}),
                        html.P([
                            html.I(className="fas fa-puzzle-piece", style={'marginRight': '5px'}),
                            f"分析模块: {len(selected_modules)} 个"
                        ], style={'marginBottom': '5px'}),
                    ], className="alert alert-info"),
                    
                    html.Hr(),
                    
                    html.Div([
                        html.I(className="fas fa-spinner fa-spin", style={'marginRight': '10px'}),
                        "处理中...完成后可在批量任务列表中查看结果。"
                    ], style={'color': '#3498db'})
                ])
                
                return status_msg, job_id
                
            except Exception as e:
                error_msg = html.Div([
                    html.I(className="fas fa-exclamation-triangle", 
                          style={'color': '#e74c3c', 'marginRight': '10px'}),
                    f"启动批量处理失败: {str(e)}"
                ], className="alert alert-danger")
                return error_msg, no_update
        
        @self.app.callback(
            [Output('batch-jobs-modal', 'style'),
             Output('batch-jobs-list', 'children')],
            [Input('view-batch-jobs', 'n_clicks'),
             Input('close-batch-jobs', 'n_clicks'),
             Input('close-batch-jobs-footer', 'n_clicks')],
            [State('batch-jobs-modal', 'style')],
            prevent_initial_call=True
        )
        def toggle_batch_jobs_modal(view_clicks, close_clicks, close_footer_clicks, current_style):
            """Toggle batch jobs modal and load job list"""
            ctx = dash.callback_context
            if not ctx.triggered:
                return no_update, no_update
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id in ['close-batch-jobs', 'close-batch-jobs-footer']:
                return {'display': 'none'}, no_update
            
            if button_id == 'view-batch-jobs':
                try:
                    from src.analysis.batch_processor import batch_processor
                    
                    # Get all batch jobs
                    jobs = batch_processor.list_jobs()
                    
                    if not jobs:
                        content = html.Div([
                            html.I(className="fas fa-inbox", 
                                  style={'fontSize': '48px', 'color': '#bdc3c7'}),
                            html.P("暂无批量处理任务", style={'marginTop': '10px'})
                        ], style={'textAlign': 'center', 'padding': '40px'})
                    else:
                        # Create jobs table
                        rows = []
                        for job in jobs:
                            status_icon = {
                                'pending': 'fa-clock',
                                'running': 'fa-spinner fa-spin',
                                'completed': 'fa-check-circle',
                                'completed_with_errors': 'fa-exclamation-circle',
                                'failed': 'fa-times-circle'
                            }.get(job['status'], 'fa-question-circle')
                            
                            status_color = {
                                'pending': '#f39c12',
                                'running': '#3498db',
                                'completed': '#27ae60',
                                'completed_with_errors': '#e67e22',
                                'failed': '#e74c3c'
                            }.get(job['status'], '#7f8c8d')
                            
                            row = html.Tr([
                                html.Td(job['job_id'][:8] + '...'),
                                html.Td([
                                    html.I(className=f"fas {status_icon}", 
                                          style={'color': status_color, 'marginRight': '5px'}),
                                    job['status'].replace('_', ' ').title()
                                ]),
                                html.Td(f"{job['datasets']} 个"),
                                html.Td(f"{job['modules']} 个"),
                                html.Td(job['created_at'][:19] if job['created_at'] else 'N/A'),
                                html.Td([
                                    html.Button([
                                        html.I(className="fas fa-eye"),
                                        " 查看"
                                    ], 
                                    className="btn btn-sm btn-primary",
                                    id={'type': 'view-batch-job', 'index': job['job_id']},
                                    style={'marginRight': '5px'}),
                                    
                                    html.Button([
                                        html.I(className="fas fa-download"),
                                        " 下载"
                                    ], 
                                    className="btn btn-sm btn-success",
                                    id={'type': 'download-batch-job', 'index': job['job_id']},
                                    disabled=job['status'] not in ['completed', 'completed_with_errors'])
                                ])
                            ])
                            rows.append(row)
                        
                        content = html.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th("作业ID"),
                                    html.Th("状态"),
                                    html.Th("数据集"),
                                    html.Th("模块"),
                                    html.Th("创建时间"),
                                    html.Th("操作")
                                ])
                            ]),
                            html.Tbody(rows)
                        ], className="table table-hover")
                    
                    return {'display': 'block'}, content
                    
                except Exception as e:
                    error_content = html.Div([
                        html.I(className="fas fa-exclamation-triangle", 
                              style={'color': '#e74c3c', 'marginRight': '10px'}),
                        f"加载批量任务失败: {str(e)}"
                    ], className="alert alert-danger")
                    return {'display': 'block'}, error_content
            
            return no_update, no_update
    
    # Content creation methods
    def create_overview_content(self):
        """Create overview page content"""
        return html.Div([
            html.Div([
                html.H1("LIHC多维度预后分析平台", className="card-title"),
                html.P("基于多维度网络分析的肝癌预后分析系统"),
                
                html.Div([
                    html.Div([
                        html.H3("🎯 平台特色"),
                        html.Ul([
                            html.Li("五维度肿瘤微环境分析"),
                            html.Li("跨维度网络整合"),
                            html.Li("Linchpin关键靶点识别"),
                            html.Li("多组学数据整合"),
                            html.Li("ClosedLoop因果推理")
                        ])
                    ], className="card"),
                    
                    html.Div([
                        html.H3("📊 快速开始"),
                        html.P("1. 上传您的数据或使用演示数据"),
                        html.P("2. 选择分析类型"),
                        html.P("3. 查看分析结果"),
                        html.Button("开始分析", className="btn-primary")
                    ], className="card"),
                ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'})
            ], className="card")
        ])
    
    def create_multidim_content(self):
        """Create multi-dimensional analysis content"""
        # Import dataset selector
        try:
            from src.components.dataset_selector import create_dataset_selector, create_data_source_indicator
            dataset_selector = create_dataset_selector(self.dataset_manager, 'multidim-dataset-selector')
            current_dataset = self.dataset_manager.get_current_dataset() if self.dataset_manager else {'name': 'Demo', 'type': 'demo'}
            data_indicator = create_data_source_indicator(current_dataset)
        except:
            dataset_selector = html.Div()
            data_indicator = html.Div()
        
        return html.Div([
            # Dataset selector at top
            dataset_selector,
            
            # Main content card with data source indicator
            html.Div([
                data_indicator,  # Data source indicator in top-right
                html.H2("多维度分析", className="card-title"),
                html.P("五个生物学维度的综合分析"),
                
                # Analysis content based on selected dataset
                html.Div(id='multidim-analysis-content', children=[
                    html.Div([
                        html.H4("分析内容将基于所选数据集生成"),
                        html.P(f"当前数据集: {current_dataset.get('name', 'Demo')}"),
                        html.Hr(),
                        
                        # Placeholder for actual analysis
                        html.Div([
                            html.H5("1. 基因表达分析"),
                            html.P("基于表达数据的差异分析..."),
                            
                            html.H5("2. 突变景观"),
                            html.P("体细胞突变分布..."),
                            
                            html.H5("3. 拷贝数变异"),
                            html.P("染色体水平的扩增和缺失..."),
                            
                            html.H5("4. 甲基化模式"),
                            html.P("CpG岛甲基化状态..."),
                            
                            html.H5("5. 临床关联"),
                            html.P("分子特征与临床表型的关联...")
                        ], style={'marginTop': '20px'})
                    ])
                ])
            ], className="card", style={'position': 'relative'})
        ])
    
    def create_network_content(self):
        """Create network analysis content"""
        # Import dataset selector
        try:
            from src.components.dataset_selector import create_dataset_selector, create_data_source_indicator
            dataset_selector = create_dataset_selector(self.dataset_manager, 'network-dataset-selector')
            current_dataset = self.dataset_manager.get_current_dataset() if self.dataset_manager else {'name': 'Demo', 'type': 'demo'}
            data_indicator = create_data_source_indicator(current_dataset)
        except:
            dataset_selector = html.Div()
            data_indicator = html.Div()
            
        return html.Div([
            # Dataset selector at top
            dataset_selector,
            
            # Main content card
            html.Div([
                data_indicator,  # Data source indicator
                html.H2("网络分析", className="card-title"),
                html.P("分子相互作用网络分析"),
                html.Div(id='network-analysis-content')  # Content container for updates
            ], className="card", style={'position': 'relative'})
        ])
    
    def create_linchpin_content(self):
        """Create linchpin targets content"""
        # Import dataset selector
        try:
            from src.components.dataset_selector import create_dataset_selector, create_data_source_indicator
            dataset_selector = create_dataset_selector(self.dataset_manager, 'linchpin-dataset-selector')
            current_dataset = self.dataset_manager.get_current_dataset() if self.dataset_manager else {'name': 'Demo', 'type': 'demo'}
            data_indicator = create_data_source_indicator(current_dataset)
        except:
            dataset_selector = html.Div()
            data_indicator = html.Div()
            
        return html.Div([
            # Dataset selector at top
            dataset_selector,
            
            # Main content card
            html.Div([
                data_indicator,  # Data source indicator
                html.H2("Linchpin靶点", className="card-title"),
                html.P("关键治疗靶点识别"),
                html.Div(id='linchpin-analysis-content')  # Content container for updates
            ], className="card", style={'position': 'relative'})
        ])
    
    def create_survival_content(self):
        """Create survival analysis content"""
        # Import dataset selector
        try:
            from src.components.dataset_selector import create_dataset_selector, create_data_source_indicator
            dataset_selector = create_dataset_selector(self.dataset_manager, 'survival-dataset-selector')
            current_dataset = self.dataset_manager.get_current_dataset() if self.dataset_manager else {'name': 'Demo', 'type': 'demo'}
            data_indicator = create_data_source_indicator(current_dataset)
        except:
            dataset_selector = html.Div()
            data_indicator = html.Div()
            
        return html.Div([
            # Dataset selector at top
            dataset_selector,
            
            html.Div([
                data_indicator,  # Data source indicator
                html.H2([html.I(className="fas fa-chart-line"), " 生存分析"], className="card-title"),
                html.P("基于Kaplan-Meier方法的生存曲线分析"),
            ], className="card", style={'position': 'relative'}),
            
            # Analysis content container
            html.Div(id='survival-analysis-content'),
            
            # Survival curves
            html.Div([
                html.H3("基因表达与生存期关系"),
                dcc.Graph(
                    id='survival-main',
                    figure=self.create_survival_preview(),
                    style={'height': '500px'}
                )
            ], className="card"),
            
            # Risk score distribution
            html.Div([
                html.Div([
                    html.Div([
                        html.H4("风险评分分布"),
                        dcc.Graph(
                            id='risk-distribution',
                            figure=self.create_risk_distribution(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'}),
                    
                    html.Div([
                        html.H4("分期生存分析"),
                        dcc.Graph(
                            id='stage-survival',
                            figure=self.create_stage_survival(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px'})
            ], className="card")
        ])
    
    def create_multiomics_content(self):
        """Create multi-omics integration content"""
        return html.Div([
            # Header
            html.Div([
                html.H2([html.I(className="fas fa-dna"), " 多组学数据整合分析"], className="card-title"),
                html.P("整合RNA-seq、CNV、突变、甲基化等多维度数据进行综合分析"),
            ], className="card"),
            
            # Summary statistics
            html.Div([
                html.Div([
                    html.Div([
                        html.H5("数据类型", style={'color': '#7f8c8d'}),
                        html.H3("4", style={'color': '#3498db'}),
                        html.P("RNA/CNV/突变/甲基化", style={'fontSize': '0.9rem'})
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H5("分析基因", style={'color': '#7f8c8d'}),
                        html.H3("500", style={'color': '#27ae60'}),
                        html.P("跨组学共同基因", style={'fontSize': '0.9rem'})
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H5("样本数量", style={'color': '#7f8c8d'}),
                        html.H3("200", style={'color': '#e74c3c'}),
                        html.P("TCGA肿瘤样本", style={'fontSize': '0.9rem'})
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H5("关键通路", style={'color': '#7f8c8d'}),
                        html.H3("15", style={'color': '#f39c12'}),
                        html.P("显著富集通路", style={'fontSize': '0.9rem'})
                    ], className="metric-card"),
                ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '20px', 'marginBottom': '30px'})
            ]),
            
            # Analysis content container
            html.Div(id='multiomics-analysis-content'),
            
            # Multi-omics correlation heatmap
            html.Div([
                html.H3([html.I(className="fas fa-th"), " 多组学数据相关性热图"]),
                dcc.Graph(
                    id='multiomics-heatmap',
                    figure=self.create_multiomics_heatmap(),
                    style={'height': '500px'}
                )
            ], className="card"),
            
            # Omics integration scores
            html.Div([
                html.Div([
                    html.Div([
                        html.H3([html.I(className="fas fa-chart-line"), " 组学整合评分"]),
                        dcc.Graph(
                            id='integration-scores',
                            figure=self.create_integration_scores(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'}),
                    
                    html.Div([
                        html.H3([html.I(className="fas fa-project-diagram"), " 通路富集分析"]),
                        dcc.Graph(
                            id='pathway-enrichment',
                            figure=self.create_pathway_enrichment(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px'})
            ], className="card"),
            
            # Mutation landscape
            html.Div([
                html.H3([html.I(className="fas fa-dna"), " 突变景观图"]),
                dcc.Graph(
                    id='mutation-landscape',
                    figure=self.create_mutation_landscape(),
                    style={'height': '450px'}
                )
            ], className="card")
        ])
    
    def create_closedloop_content(self):
        """Create ClosedLoop analysis content"""
        # Import dataset selector
        try:
            from src.components.dataset_selector import create_dataset_selector, create_data_source_indicator
            dataset_selector = create_dataset_selector(self.dataset_manager, 'closedloop-dataset-selector')
            current_dataset = self.dataset_manager.get_current_dataset() if self.dataset_manager else {'name': 'Demo', 'type': 'demo'}
            data_indicator = create_data_source_indicator(current_dataset)
        except:
            dataset_selector = html.Div()
            data_indicator = html.Div()
            
        return html.Div([
            # Dataset selector at top
            dataset_selector,
            
            # Header
            html.Div([
                data_indicator,  # Data source indicator
                html.H2([html.I(className="fas fa-sync-alt"), " ClosedLoop因果推理分析"], className="card-title"),
                html.P("基于多证据链的闭环因果推断与验证系统"),
            ], className="card"),
            
            # Analysis content container
            html.Div(id='closedloop-analysis-content'),
            
            # Causal network visualization
            html.Div([
                html.H3([html.I(className="fas fa-project-diagram"), " 因果网络拓扑"]),
                dcc.Graph(
                    id='causal-network',
                    figure=self.create_causal_network(),
                    style={'height': '600px'}
                )
            ], className="card"),
            
            # Evidence weights and confidence
            html.Div([
                html.Div([
                    html.Div([
                        html.H3([html.I(className="fas fa-balance-scale"), " 证据权重分布"]),
                        dcc.Graph(
                            id='evidence-weights',
                            figure=self.create_evidence_weights(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'}),
                    
                    html.Div([
                        html.H3([html.I(className="fas fa-check-circle"), " 推理置信度"]),
                        dcc.Graph(
                            id='inference-confidence',
                            figure=self.create_inference_confidence(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px'})
            ], className="card"),
            
            # Feedback loops
            html.Div([
                html.H3([html.I(className="fas fa-redo"), " 关键反馈环路"]),
                dcc.Graph(
                    id='feedback-loops',
                    figure=self.create_feedback_loops(),
                    style={'height': '450px'}
                )
            ], className="card")
        ])
    
    def create_charts_content(self):
        """Create comprehensive charts content"""
        # Import dataset selector
        try:
            from src.components.dataset_selector import create_dataset_selector, create_data_source_indicator
            dataset_selector = create_dataset_selector(self.dataset_manager, 'charts-dataset-selector')
            current_dataset = self.dataset_manager.get_current_dataset() if self.dataset_manager else {'name': 'Demo', 'type': 'demo'}
            data_indicator = create_data_source_indicator(current_dataset)
        except:
            dataset_selector = html.Div()
            data_indicator = html.Div()
            
        return html.Div([
            # Dataset selector at top
            dataset_selector,
            
            # Header
            html.Div([
                data_indicator,  # Data source indicator
                html.H2([html.I(className="fas fa-chart-bar"), " 综合数据可视化"], className="card-title"),
                html.P("整合所有分析结果的专业图表展示"),
            ], className="card", style={'position': 'relative'}),
            
            # Analysis content container
            html.Div(id='charts-analysis-content'),
            
            # Comprehensive score radar
            html.Div([
                html.H3([html.I(className="fas fa-chart-radar"), " 综合评分雷达图"]),
                dcc.Graph(
                    id='comprehensive-radar',
                    figure=self.create_comprehensive_radar(),
                    style={'height': '500px'}
                )
            ], className="card"),
            
            # Multi-dimensional analysis
            html.Div([
                html.Div([
                    html.Div([
                        html.H3([html.I(className="fas fa-chart-scatter"), " 多维度散点图"]),
                        dcc.Graph(
                            id='multidim-scatter',
                            figure=self.create_multidim_scatter(),
                            style={'height': '450px'}
                        )
                    ], style={'flex': '1'}),
                    
                    html.Div([
                        html.H3([html.I(className="fas fa-project-diagram"), " 聚类分析图"]),
                        dcc.Graph(
                            id='cluster-analysis',
                            figure=self.create_cluster_analysis(),
                            style={'height': '450px'}
                        )
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px'})
            ], className="card"),
            
            # Integrated heatmap
            html.Div([
                html.H3([html.I(className="fas fa-th"), " 整合分析热图"]),
                dcc.Graph(
                    id='integrated-heatmap',
                    figure=self.create_integrated_heatmap(),
                    style={'height': '600px'}
                )
            ], className="card")
        ])
    
    def create_tables_content(self):
        """Create results tables content"""
        # Import dataset selector
        try:
            from src.components.dataset_selector import create_dataset_selector, create_data_source_indicator
            dataset_selector = create_dataset_selector(self.dataset_manager, 'tables-dataset-selector')
            current_dataset = self.dataset_manager.get_current_dataset() if self.dataset_manager else {'name': 'Demo', 'type': 'demo'}
            data_indicator = create_data_source_indicator(current_dataset)
        except:
            dataset_selector = html.Div()
            data_indicator = html.Div()
            current_dataset = {'name': 'Demo', 'type': 'demo'}
        
        return html.Div([
            # Dataset selector at top
            dataset_selector,
            
            # Header
            html.Div([
                data_indicator,
                html.H2([html.I(className="fas fa-table"), " 数据表格查看"], className="card-title"),
                html.P("查看和导出详细数据表格"),
            ], className="card", style={'position': 'relative'}),
            
            # Tab selection
            html.Div([
                dcc.Tabs(id="table-tabs", value='clinical', children=[
                    dcc.Tab(label='临床数据', value='clinical'),
                    dcc.Tab(label='基因表达', value='expression'),
                    dcc.Tab(label='突变数据', value='mutation'),
                    dcc.Tab(label='分析结果', value='results'),
                ]),
                html.Div(id='table-content', style={'marginTop': '20px'})
            ], className="card"),
            
            # Export options
            html.Div([
                html.H3([html.I(className="fas fa-download"), " 导出选项"]),
                html.Div([
                    html.Button([
                        html.I(className="fas fa-file-csv"),
                        " 导出CSV"
                    ], id="export-csv", className="btn btn-primary", style={'marginRight': '10px'}),
                    html.Button([
                        html.I(className="fas fa-file-excel"),
                        " 导出Excel"
                    ], id="export-excel", className="btn btn-success", style={'marginRight': '10px'}),
                    html.Button([
                        html.I(className="fas fa-clipboard"),
                        " 复制到剪贴板"
                    ], id="copy-clipboard", className="btn btn-info")
                ], style={'marginTop': '15px'}),
                dcc.Download(id="table-download")
            ], className="card")
        ])
    
    def create_download_content(self):
        """Create download content"""
        # Import dataset selector
        try:
            from src.components.dataset_selector import create_dataset_selector, create_data_source_indicator
            dataset_selector = create_dataset_selector(self.dataset_manager, 'download-dataset-selector')
            current_dataset = self.dataset_manager.get_current_dataset() if self.dataset_manager else {'name': 'Demo', 'type': 'demo'}
            data_indicator = create_data_source_indicator(current_dataset)
        except:
            dataset_selector = html.Div()
            data_indicator = html.Div()
        
        # Get available analysis results
        try:
            from src.data_processing.history_manager import HistoryManager
            history_manager = HistoryManager()
            analyses = history_manager.get_user_history()['analyses']
            completed_analyses = [a for a in analyses if a['status'] == 'completed']
        except:
            completed_analyses = []
        
        return html.Div([
            # Dataset selector at top
            dataset_selector,
            
            # Header
            html.Div([
                data_indicator,
                html.H2([html.I(className="fas fa-download"), " 结果下载中心"], className="card-title"),
                html.P("下载分析结果、报告和原始数据"),
            ], className="card", style={'position': 'relative'}),
            
            # Quick download section
            html.Div([
                html.H3([html.I(className="fas fa-rocket"), " 快速下载"]),
                html.Div([
                    html.Div([
                        html.Button([
                            html.I(className="fas fa-file-pdf", style={'fontSize': '2rem'}),
                            html.Br(),
                            "完整报告"
                        ], id="download-full-report", className="download-btn", 
                           style={'width': '120px', 'height': '100px', 'margin': '10px'}),
                        
                        html.Button([
                            html.I(className="fas fa-chart-bar", style={'fontSize': '2rem'}),
                            html.Br(),
                            "所有图表"
                        ], id="download-all-charts", className="download-btn",
                           style={'width': '120px', 'height': '100px', 'margin': '10px'}),
                        
                        html.Button([
                            html.I(className="fas fa-table", style={'fontSize': '2rem'}),
                            html.Br(),
                            "数据表格"
                        ], id="download-all-tables", className="download-btn",
                           style={'width': '120px', 'height': '100px', 'margin': '10px'}),
                        
                        html.Button([
                            html.I(className="fas fa-archive", style={'fontSize': '2rem'}),
                            html.Br(),
                            "打包全部"
                        ], id="download-all-zip", className="download-btn",
                           style={'width': '120px', 'height': '100px', 'margin': '10px'})
                    ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'})
                ])
            ], className="card"),
            
            # Analysis results section
            html.Div([
                html.H3([html.I(className="fas fa-clipboard-check"), " 分析结果"]),
                html.Div([
                    html.Div([
                        html.Div([
                            html.H5(f"会话: {analysis['session_id'][:8]}..."),
                            html.P(f"时间: {analysis['timestamp']}"),
                            html.P(f"模块: {', '.join(analysis.get('modules', []))}"),
                            html.Button([
                                html.I(className="fas fa-download"),
                                " 下载此结果"
                            ], id={'type': 'download-result', 'index': analysis['session_id']},
                               className="btn btn-primary btn-sm")
                        ], style={'border': '1px solid #ddd', 'padding': '15px', 
                                 'borderRadius': '5px', 'marginBottom': '10px'})
                    ]) for analysis in completed_analyses[:5]
                ]) if completed_analyses else html.P("暂无完成的分析结果", style={'color': '#999'})
            ], className="card"),
            
            # Custom report generator
            html.Div([
                html.H3([html.I(className="fas fa-cog"), " 自定义报告生成"]),
                html.Div([
                    html.Label("选择要包含的内容:"),
                    dcc.Checklist(
                        id="report-content-selector",
                        options=[
                            {'label': ' 执行摘要', 'value': 'summary'},
                            {'label': ' 差异表达分析', 'value': 'deg'},
                            {'label': ' 生存分析', 'value': 'survival'},
                            {'label': ' 网络分析', 'value': 'network'},
                            {'label': ' 精准医学分析', 'value': 'precision'},
                            {'label': ' 数据表格', 'value': 'tables'},
                            {'label': ' 方法说明', 'value': 'methods'}
                        ],
                        value=['summary', 'deg', 'survival'],
                        inline=True,
                        style={'marginTop': '10px', 'marginBottom': '20px'}
                    ),
                    
                    html.Label("报告格式:"),
                    dcc.RadioItems(
                        id="report-format",
                        options=[
                            {'label': ' PDF', 'value': 'pdf'},
                            {'label': ' HTML', 'value': 'html'},
                            {'label': ' Word', 'value': 'docx'}
                        ],
                        value='pdf',
                        inline=True,
                        style={'marginTop': '10px', 'marginBottom': '20px'}
                    ),
                    
                    html.Button([
                        html.I(className="fas fa-magic"),
                        " 生成报告"
                    ], id="generate-custom-report", className="btn btn-success")
                ])
            ], className="card"),
            
            # Download status
            html.Div(id="download-status", style={'marginTop': '20px'}),
            dcc.Download(id="download-output")
        ])
    
    def create_history_content(self):
        """Create history content with detailed records"""
        # Initialize history manager
        try:
            from src.data_processing.history_manager import HistoryManager
            history_manager = HistoryManager()
            history_data = history_manager.get_user_history()
            stats = history_manager.get_statistics()
        except:
            history_data = {'uploads': [], 'analyses': []}
            stats = {
                'total_uploads': 0,
                'successful_uploads': 0,
                'total_analyses': 0,
                'recent_uploads': 0
            }
        
        return html.Div([
            # Header
            html.Div([
                html.H2([html.I(className="fas fa-history"), " 历史记录管理中心"], 
                       className="card-title"),
                html.P("查看和管理您的上传历史与分析结果"),
            ], className="card"),
            
            # Statistics Cards
            html.Div([
                html.Div([
                    html.Div([
                        html.H5("总上传次数", style={'color': '#7f8c8d'}),
                        html.H3(str(stats['total_uploads']), style={'color': '#3498db'}),
                        html.P(f"成功: {stats['successful_uploads']}", style={'fontSize': '0.9rem'})
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H5("总分析次数", style={'color': '#7f8c8d'}),
                        html.H3(str(stats['total_analyses']), style={'color': '#27ae60'}),
                        html.P(f"最近7天: {stats['recent_analyses']}", style={'fontSize': '0.9rem'})
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H5("活跃会话", style={'color': '#7f8c8d'}),
                        html.H3(str(stats.get('unique_sessions', 0)), style={'color': '#e74c3c'}),
                        html.P("独立用户会话", style={'fontSize': '0.9rem'})
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H5("最近上传", style={'color': '#7f8c8d'}),
                        html.H3(str(stats['recent_uploads']), style={'color': '#f39c12'}),
                        html.P("过去7天", style={'fontSize': '0.9rem'})
                    ], className="metric-card"),
                ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 
                         'gap': '20px', 'marginBottom': '30px'})
            ], className="card"),
            
            # Upload History Table
            html.Div([
                html.H3([html.I(className="fas fa-upload"), " 上传历史"], 
                       style={'marginBottom': '20px'}),
                
                html.Div([
                    dash_table.DataTable(
                        id='upload-history-table',
                        columns=[
                            {'name': '时间', 'id': 'timestamp'},
                            {'name': '会话ID', 'id': 'session_id'},
                            {'name': '上传文件数', 'id': 'file_count'},
                            {'name': '验证状态', 'id': 'validation_status'},
                            {'name': '操作', 'id': 'actions'}
                        ],
                        data=[
                            {
                                'timestamp': upload['timestamp'],
                                'session_id': upload['session_id'][:8] + '...',
                                'file_count': len(upload.get('files', {})),
                                'validation_status': '✅ 成功' if upload['validation_status'] == 'success' else '❌ 失败',
                                'actions': '查看详情'
                            }
                            for upload in history_data['uploads'][:10]
                        ],
                        style_cell={'textAlign': 'center'},
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'validation_status', 'filter_query': '{validation_status} contains "成功"'},
                                'color': 'green'
                            },
                            {
                                'if': {'column_id': 'validation_status', 'filter_query': '{validation_status} contains "失败"'},
                                'color': 'red'
                            }
                        ],
                        page_size=10
                    )
                ]) if history_data['uploads'] else html.P("暂无上传记录", style={'color': '#999'})
            ], className="card"),
            
            # Analysis History Table
            html.Div([
                html.H3([html.I(className="fas fa-chart-line"), " 分析历史"], 
                       style={'marginBottom': '20px'}),
                
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.P(f"时间: {analysis['timestamp']}", style={'margin': '5px 0'}),
                                    html.P(f"会话: {analysis['session_id'][:8]}...", style={'margin': '5px 0', 'color': '#666'}),
                                    html.P(f"模块: {', '.join(analysis.get('modules', []))}", style={'margin': '5px 0'}),
                                    html.P([
                                        "状态: ",
                                        html.Span('✅ 完成' if analysis['status'] == 'completed' else '⏳ 进行中',
                                                 style={'color': 'green' if analysis['status'] == 'completed' else 'orange'})
                                    ], style={'margin': '5px 0'}),
                                ], style={'flex': '1'}),
                                html.Div([
                                    html.Button([
                                        html.I(className="fas fa-eye"),
                                        " 查看结果"
                                    ], id={'type': 'view-results-btn', 'index': analysis['session_id']},
                                       className="btn btn-sm btn-primary",
                                       disabled=analysis['status'] != 'completed'),
                                    html.Button([
                                        html.I(className="fas fa-download"),
                                        " 下载报告"
                                    ], id={'type': 'download-report-btn', 'index': analysis['session_id']},
                                       className="btn btn-sm btn-secondary",
                                       style={'marginLeft': '5px'},
                                       disabled=analysis['status'] != 'completed')
                                ], style={'display': 'flex', 'alignItems': 'center'})
                            ], style={'display': 'flex', 'justifyContent': 'space-between', 
                                     'padding': '15px', 'border': '1px solid #dee2e6',
                                     'borderRadius': '5px', 'marginBottom': '10px',
                                     'backgroundColor': '#fff'})
                        ])
                        for analysis in history_data['analyses'][:10]
                    ])
                ]) if history_data['analyses'] else html.P("暂无分析记录", style={'color': '#999'})
            ], className="card"),
            
            # Actions
            html.Div([
                html.H3([html.I(className="fas fa-tools"), " 管理操作"], 
                       style={'marginBottom': '20px'}),
                
                html.Div([
                    html.Button([
                        html.I(className="fas fa-download"),
                        " 导出历史记录"
                    ], id="export-history", className="btn btn-primary", 
                       style={'marginRight': '10px'}),
                    
                    html.Button([
                        html.I(className="fas fa-trash"),
                        " 清理过期数据"
                    ], id="clean-history", className="btn btn-warning",
                       style={'marginRight': '10px'}),
                    
                    html.Button([
                        html.I(className="fas fa-sync"),
                        " 刷新"
                    ], id="refresh-history", className="btn btn-secondary"),
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.P("提示：", style={'fontWeight': 'bold'}),
                    html.Ul([
                        html.Li("点击表格中的'查看详情'可以查看具体的上传文件信息"),
                        html.Li("点击'查看结果'可以查看和下载分析结果"),
                        html.Li("数据会保留30天，过期后自动清理"),
                        html.Li("您可以随时导出历史记录作为备份")
                    ])
                ], style={'backgroundColor': '#f0f8ff', 'padding': '15px', 
                         'borderRadius': '5px'})
            ], className="card"),
            
            # Hidden components for interactions
            dcc.Store(id='selected-session'),
            html.Div(id='session-details-modal'),
            dcc.Download(id="download-history"),
            
            # Result viewer modal
            html.Div(id='result-viewer-modal', children=[
                html.Div([
                    html.Div([
                        html.H3("分析结果查看器", style={'display': 'inline-block'}),
                        html.Button("×", id="close-result-viewer", className="close-button",
                                   style={'float': 'right', 'fontSize': '24px', 'border': 'none',
                                         'background': 'none', 'cursor': 'pointer'})
                    ], style={'borderBottom': '1px solid #dee2e6', 'paddingBottom': '10px'}),
                    html.Div(id='result-viewer-content', style={'marginTop': '20px'})
                ], style={'background': 'white', 'padding': '20px', 'borderRadius': '10px',
                         'maxWidth': '90%', 'maxHeight': '80vh', 'overflow': 'auto',
                         'margin': '50px auto', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
            ], style={'display': 'none', 'position': 'fixed', 'top': '0', 'left': '0', 'right': '0', 
                     'bottom': '0', 'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': '1000'}),
            
            dcc.Download(id="download-report")
        ])
    
    def create_batch_content(self):
        """Create batch processing content"""
        # Import batch processor
        try:
            from src.analysis.batch_processor import batch_processor
            batch_jobs = batch_processor.list_jobs()
        except:
            batch_jobs = []
        
        # Get dataset list from dataset manager
        dataset_options = []
        if hasattr(self, 'dataset_manager'):
            datasets = self.dataset_manager.list_datasets()
            dataset_options = [
                {'label': f"{ds['name']} ({ds['type']})", 'value': ds['id']}
                for ds in datasets
            ]
        else:
            dataset_options = [
                {'label': 'Demo数据集', 'value': 'demo'}
            ]
        
        # Analysis modules
        module_options = [
            {'label': '差异表达分析', 'value': 'differential_expression'},
            {'label': '生存分析', 'value': 'survival'},
            {'label': '网络分析', 'value': 'network'},
            {'label': '通路富集', 'value': 'pathway'},
            {'label': '机器学习预测', 'value': 'prediction'},
            {'label': '分子分型', 'value': 'subtyping'},
            {'label': '多维度整合', 'value': 'multidimensional'},
            {'label': '综合分析', 'value': 'comprehensive'}
        ]
        
        return html.Div([
            # Header
            html.Div([
                html.H2([html.I(className="fas fa-layer-group"), " 批量数据处理中心"], 
                       className="card-title"),
                html.P("同时处理多个数据集，进行对比分析"),
            ], className="card"),
            
            # Batch configuration
            html.Div([
                html.H4("批量分析配置"),
                
                # Dataset selection
                html.Div([
                    html.Label("选择数据集 (支持多选):"),
                    dcc.Dropdown(
                        id='batch-dataset-selection',
                        options=dataset_options,
                        value=[],
                        multi=True,
                        placeholder="请选择要分析的数据集..."
                    )
                ], style={'marginBottom': '20px'}),
                
                # Module selection
                html.Div([
                    html.Label("选择分析模块 (支持多选):"),
                    dcc.Dropdown(
                        id='batch-modules-selection',
                        options=module_options,
                        value=['differential_expression', 'survival', 'network'],
                        multi=True,
                        placeholder="请选择要运行的分析模块..."
                    )
                ], style={'marginBottom': '20px'}),
                
                # Start button
                html.Button([
                    html.I(className="fas fa-play"),
                    " 开始批量分析"
                ], id='start-batch-analysis', className='primary-button',
                   style={'marginTop': '20px', 'width': '100%'}),
                
                # Status display
                html.Div(id='batch-job-status', style={'marginTop': '20px'})
            ], className="card"),
            
            # Job history
            html.Div([
                html.H4("批量处理历史"),
                html.Div([
                    html.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("作业ID"),
                                html.Th("状态"),
                                html.Th("数据集数"),
                                html.Th("模块数"),
                                html.Th("创建时间"),
                                html.Th("操作")
                            ])
                        ]),
                        html.Tbody([
                            html.Tr([
                                html.Td(job['job_id'][:8] + "..."),
                                html.Td(
                                    html.Span(
                                        job['status'],
                                        style={
                                            'color': '#27ae60' if job['status'] == 'completed' else
                                                    '#3498db' if job['status'] == 'running' else
                                                    '#e74c3c' if job['status'] == 'failed' else '#7f8c8d'
                                        }
                                    )
                                ),
                                html.Td(str(job.get('datasets', 0))),
                                html.Td(str(job.get('modules', 0))),
                                html.Td(job.get('created_at', 'Unknown')[:19]),
                                html.Td(
                                    html.Button(
                                        "查看结果",
                                        id={'type': 'view-batch-result', 'index': job['job_id']},
                                        className='small-button',
                                        disabled=job['status'] != 'completed'
                                    )
                                )
                            ]) for job in batch_jobs[:10]  # Show latest 10 jobs
                        ])
                    ], className="data-table")
                ], style={'overflowX': 'auto'})
            ], className="card", style={'marginTop': '20px'}),
            
            # Result viewer modal
            html.Div(
                id='batch-result-modal',
                children=[
                    html.Div([
                        html.Button("×", id='close-batch-result', 
                                  style={'float': 'right', 'fontSize': '24px', 
                                        'background': 'none', 'border': 'none'}),
                        html.H3("批量分析结果"),
                        html.Div(id='batch-result-content', style={'marginTop': '20px'})
                    ], style={'background': 'white', 'padding': '20px', 'borderRadius': '10px',
                             'maxWidth': '90%', 'maxHeight': '80vh', 'overflow': 'auto',
                             'margin': '50px auto', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ], style={'display': 'none', 'position': 'fixed', 'top': '0', 'left': '0', 
                         'right': '0', 'bottom': '0', 'backgroundColor': 'rgba(0,0,0,0.5)', 
                         'zIndex': '1000'}
            ),
            
            # Progress tracking
            dcc.Interval(
                id='batch-progress-interval',
                interval=2000,  # Update every 2 seconds
                disabled=True
            ),
            
            # Hidden store for current batch job
            dcc.Store(id='current-batch-job-id', data=None)
        ])
    
    def create_taskqueue_content(self):
        """Create task queue management content"""
        # Import task queue manager
        try:
            from src.analysis.task_queue import task_queue
            queue_info = task_queue.get_queue_info()
            task_history = task_queue.get_task_history(limit=20)
        except:
            queue_info = {
                'celery_available': False,
                'queued_tasks': 0,
                'active_tasks': 0,
                'scheduled_tasks': 0,
                'failed_tasks': 0
            }
            task_history = []
        
        return html.Div([
            # Header
            html.Div([
                html.H2([html.I(className="fas fa-tasks"), " 任务队列管理中心"], 
                       className="card-title"),
                html.P("监控和管理分析任务队列"),
            ], className="card"),
            
            # Queue Status Cards
            html.Div([
                html.Div([
                    html.Div([
                        html.H3(str(queue_info['queued_tasks']), 
                               style={'fontSize': '2rem', 'marginBottom': '5px'}),
                        html.P("排队中", style={'marginBottom': '0'})
                    ], className="status-card queued"),
                    
                    html.Div([
                        html.H3(str(queue_info['active_tasks']), 
                               style={'fontSize': '2rem', 'marginBottom': '5px'}),
                        html.P("运行中", style={'marginBottom': '0'})
                    ], className="status-card active"),
                    
                    html.Div([
                        html.H3(str(queue_info['scheduled_tasks']), 
                               style={'fontSize': '2rem', 'marginBottom': '5px'}),
                        html.P("已计划", style={'marginBottom': '0'})
                    ], className="status-card scheduled"),
                    
                    html.Div([
                        html.H3(str(queue_info['failed_tasks']), 
                               style={'fontSize': '2rem', 'marginBottom': '5px'}),
                        html.P("失败", style={'marginBottom': '0'})
                    ], className="status-card failed")
                ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 
                         'gap': '20px', 'marginBottom': '30px'})
            ], className="card"),
            
            # Celery Status
            html.Div([
                html.H4([
                    html.I(className="fas fa-info-circle"),
                    " 队列系统状态"
                ]),
                html.Div([
                    html.Span("Celery状态: ", style={'fontWeight': 'bold'}),
                    html.Span(
                        "可用" if queue_info['celery_available'] else "不可用 (使用文件队列)",
                        style={'color': '#27ae60' if queue_info['celery_available'] else '#e74c3c'}
                    )
                ], style={'marginBottom': '10px'}),
                
                html.Div([
                    html.P("提示: 安装Celery和Redis以启用高性能任务队列:", 
                          style={'marginBottom': '5px'}),
                    html.Code("pip install celery[redis] redis flower", 
                             style={'backgroundColor': '#f4f4f4', 'padding': '5px', 
                                   'borderRadius': '3px', 'display': 'block', 'marginBottom': '10px'}),
                    html.P("启动worker: ", style={'marginBottom': '5px', 'display': 'inline'}),
                    html.Code("python -m src.analysis.task_queue start_worker",
                             style={'backgroundColor': '#f4f4f4', 'padding': '5px', 
                                   'borderRadius': '3px'})
                ] if not queue_info['celery_available'] else []),
            ], className="card", style={'backgroundColor': '#f8f9fa'}),
            
            # Task History
            html.Div([
                html.H4("任务历史"),
                html.Div([
                    html.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("任务ID"),
                                html.Th("类型"),
                                html.Th("数据集"),
                                html.Th("状态"),
                                html.Th("提交时间"),
                                html.Th("优先级"),
                                html.Th("操作")
                            ])
                        ]),
                        html.Tbody([
                            html.Tr([
                                html.Td(task.get('task_id', task.get('celery_task_id', 'N/A'))[:8] + "..."),
                                html.Td(task.get('type', 'analysis')),
                                html.Td(task.get('dataset_id', 'Multiple') if task.get('type') != 'batch' 
                                       else f"{len(task.get('dataset_ids', []))} datasets"),
                                html.Td(
                                    html.Span(
                                        task.get('status', 'unknown'),
                                        style={
                                            'color': {
                                                'queued': '#7f8c8d',
                                                'running': '#3498db',
                                                'completed': '#27ae60',
                                                'failed': '#e74c3c',
                                                'cancelled': '#95a5a6'
                                            }.get(task.get('status', 'unknown'), '#7f8c8d')
                                        }
                                    )
                                ),
                                html.Td(task.get('submitted_at', 'N/A')[:19] if task.get('submitted_at') else 'N/A'),
                                html.Td(str(task.get('priority', 1))),
                                html.Td(
                                    html.Button(
                                        "取消" if task.get('status') in ['queued', 'running'] else "查看",
                                        id={'type': 'task-action', 'index': task.get('task_id', str(i))},
                                        className='small-button',
                                        disabled=task.get('status') not in ['queued', 'running', 'completed']
                                    )
                                )
                            ]) for i, task in enumerate(task_history[:20])
                        ])
                    ], className="data-table")
                ], style={'overflowX': 'auto'})
            ], className="card"),
            
            # Refresh button
            html.Div([
                html.Button([
                    html.I(className="fas fa-sync"),
                    " 刷新队列状态"
                ], id='refresh-taskqueue', className='primary-button', 
                   style={'width': '100%'})
            ], style={'marginTop': '20px'}),
            
            # Auto-refresh interval
            dcc.Interval(
                id='taskqueue-refresh-interval',
                interval=5000,  # Refresh every 5 seconds
                disabled=False
            ),
            
            # Hidden store for selected task
            dcc.Store(id='selected-task-id', data=None)
        ])
    
    def create_data_management_content(self):
        """Create data management content with upload functionality"""
        return html.Div([
            # Header Card
            html.Div([
                html.H2([html.I(className="fas fa-database"), " 数据管理中心"], 
                       className="card-title"),
                html.P("上传、验证和管理您的多组学数据进行LIHC分析", 
                      style={'marginBottom': '20px'}),
            ], className="card"),
            
            # Template Download Section
            html.Div([
                html.H3([html.I(className="fas fa-download"), " 第一步：下载数据模板"], 
                       style={'marginBottom': '20px'}),
                html.P("请先下载数据模板，按照格式要求准备您的数据：", 
                      style={'marginBottom': '15px'}),
                
                html.Div([
                    html.Button([
                        html.I(className="fas fa-file-excel"),
                        " 下载临床数据模板"
                    ], id="download-clinical-template", className="btn btn-primary", 
                       style={'marginRight': '10px'}),
                    
                    html.Button([
                        html.I(className="fas fa-file-excel"),
                        " 下载表达数据模板"
                    ], id="download-expression-template", className="btn btn-primary",
                       style={'marginRight': '10px'}),
                    
                    html.Button([
                        html.I(className="fas fa-file-excel"),
                        " 下载突变数据模板"
                    ], id="download-mutation-template", className="btn btn-primary",
                       style={'marginRight': '10px'}),
                    
                    html.Button([
                        html.I(className="fas fa-file-archive"),
                        " 下载全部模板 (ZIP)"
                    ], id="download-all-templates", className="btn btn-success"),
                ], style={'marginBottom': '30px'}),
                
                # Download links (hidden)
                dcc.Download(id="download-clinical"),
                dcc.Download(id="download-expression"),
                dcc.Download(id="download-mutation"),
                dcc.Download(id="download-templates-zip"),
                
            ], className="card"),
            
            # Upload Section
            html.Div([
                html.H3([html.I(className="fas fa-upload"), " 第二步：上传您的数据"], 
                       style={'marginBottom': '20px'}),
                
                # Dataset naming
                html.Div([
                    html.Label("数据集名称（可选）：", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='dataset-name-input',
                        type='text',
                        placeholder='例如：肝癌患者队列2025',
                        style={'width': '100%', 'marginBottom': '10px'},
                        className='form-control'
                    ),
                    html.Small("如不填写，系统将自动生成名称", className="text-muted")
                ], style={'marginBottom': '20px'}),
                
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        html.I(className="fas fa-cloud-upload-alt", 
                              style={'fontSize': '48px', 'marginBottom': '10px'}),
                        html.Br(),
                        '拖拽文件到此处或 ',
                        html.A('点击选择文件', style={'color': '#007bff', 'cursor': 'pointer'})
                    ]),
                    style={
                        'width': '100%',
                        'height': '150px',
                        'lineHeight': '60px',
                        'borderWidth': '2px',
                        'borderStyle': 'dashed',
                        'borderRadius': '10px',
                        'textAlign': 'center',
                        'marginBottom': '20px',
                        'backgroundColor': '#f8f9fa',
                        'cursor': 'pointer'
                    },
                    multiple=True,
                    accept='.csv,.tsv,.txt,.xlsx,.zip'
                ),
                
                html.Div([
                    html.Small("支持格式：CSV, TSV, TXT, XLSX, ZIP", className="text-muted"),
                    html.Br(),
                    html.Small("建议将所有文件打包成ZIP上传", className="text-muted")
                ], style={'marginBottom': '20px'}),
                
                # Upload status
                html.Div(id='upload-status', style={'marginTop': '20px'}),
                
            ], className="card"),
            
            # Validation Results Section
            html.Div(id='validation-results', style={'display': 'none'}, children=[
                html.H3([html.I(className="fas fa-check-circle"), " 第三步：数据验证结果"], 
                       style={'marginBottom': '20px'}),
                html.Div(id='validation-content')
            ], className="card"),
            
            # Analysis Section
            html.Div(id='analysis-section', style={'display': 'none'}, children=[
                html.H3([html.I(className="fas fa-chart-line"), " 第四步：开始分析"], 
                       style={'marginBottom': '20px'}),
                
                html.P("数据验证通过！请选择要运行的分析模块：", 
                      style={'marginBottom': '20px'}),
                
                dcc.Checklist(
                    id='analysis-modules',
                    options=[
                        {'label': ' Stage 1: 多维度生物学分析', 'value': 'stage1'},
                        {'label': ' Stage 2: 跨维度网络分析', 'value': 'stage2'},
                        {'label': ' Stage 3: Linchpin基因识别', 'value': 'stage3'},
                        {'label': ' 精准医学分析（全部5个模块）', 'value': 'precision'}
                    ],
                    value=['stage1', 'stage2', 'stage3', 'precision'],
                    style={'marginBottom': '20px'}
                ),
                
                html.Button([
                    html.I(className="fas fa-play"),
                    " 开始分析"
                ], id="start-analysis", className="btn btn-lg btn-success",
                   style={'marginRight': '10px'}, n_clicks=0),
                
                html.Button([
                    html.I(className="fas fa-redo"),
                    " 重新上传"
                ], id="reset-upload", className="btn btn-lg btn-secondary"),
                
                # Analysis progress
                html.Div(id='analysis-progress', style={'marginTop': '30px'}),
                
            ], className="card"),
            
            # Batch Processing Section
            html.Div([
                html.H3([html.I(className="fas fa-layer-group"), " 批量数据处理"], 
                       style={'marginBottom': '20px'}),
                html.P("选择多个数据集进行批量分析处理", 
                      style={'marginBottom': '20px'}),
                
                # Dataset selection
                html.Div([
                    html.Label("选择数据集:", style={'fontWeight': 'bold'}),
                    dcc.Checklist(
                        id='batch-dataset-selection',
                        options=[],  # Will be populated by callback
                        value=[],
                        style={'marginBottom': '20px'},
                        inputStyle={'marginRight': '8px'}
                    ),
                ], style={'marginBottom': '20px'}),
                
                # Module selection
                html.Div([
                    html.Label("选择分析模块:", style={'fontWeight': 'bold'}),
                    dcc.Checklist(
                        id='batch-modules-selection',
                        options=[
                            {'label': ' Stage 1: 多维度生物学分析', 'value': 'stage1'},
                            {'label': ' Stage 2: 跨维度网络分析', 'value': 'stage2'},
                            {'label': ' Stage 3: Linchpin基因识别', 'value': 'stage3'},
                            {'label': ' 精准医学分析（全部5个模块）', 'value': 'precision'}
                        ],
                        value=['stage1', 'stage2'],
                        style={'marginBottom': '20px'},
                        inputStyle={'marginRight': '8px'}
                    ),
                ], style={'marginBottom': '20px'}),
                
                # Batch processing controls
                html.Div([
                    html.Button([
                        html.I(className="fas fa-rocket"),
                        " 开始批量处理"
                    ], id="start-batch-analysis", className="btn btn-lg btn-primary",
                       style={'marginRight': '10px'}, n_clicks=0),
                    
                    html.Button([
                        html.I(className="fas fa-list"),
                        " 查看批量任务"
                    ], id="view-batch-jobs", className="btn btn-lg btn-secondary",
                       n_clicks=0),
                ], style={'marginBottom': '20px'}),
                
                # Batch job status
                html.Div(id='batch-job-status', style={'marginTop': '20px'}),
                
                # Store for batch job ID
                dcc.Store(id='batch-job-id'),
                
            ], className="card", style={'display': 'block'}),  # Always show batch processing
            
            # Batch Jobs List Modal (custom implementation without dbc)
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.H3("批量处理任务列表", style={'margin': '0'}),
                            html.Button("×", id="close-batch-jobs", 
                                      style={'background': 'none', 'border': 'none', 
                                             'fontSize': '28px', 'cursor': 'pointer'})
                        ], style={'display': 'flex', 'justifyContent': 'space-between', 
                                 'alignItems': 'center', 'padding': '20px', 
                                 'borderBottom': '1px solid #dee2e6'}),
                        
                        html.Div(id='batch-jobs-list', 
                               style={'padding': '20px', 'maxHeight': '60vh', 
                                     'overflowY': 'auto'}),
                        
                        html.Div([
                            html.Button("关闭", id="close-batch-jobs-footer", 
                                      className="btn btn-secondary")
                        ], style={'padding': '20px', 'borderTop': '1px solid #dee2e6', 
                                 'textAlign': 'right'})
                    ], style={'background': 'white', 'borderRadius': '8px', 
                             'maxWidth': '800px', 'margin': '50px auto', 
                             'boxShadow': '0 5px 15px rgba(0,0,0,.5)'})
                ], style={'position': 'fixed', 'top': '0', 'left': '0', 'right': '0', 
                         'bottom': '0', 'background': 'rgba(0,0,0,0.5)', 'zIndex': '1050'})
            ], id="batch-jobs-modal", style={'display': 'none'}),
            
            # Hidden stores
            dcc.Store(id='user-session-id'),
            dcc.Store(id='upload-manager-data'),
            
        ])
    
    def create_dataset_management_content(self):
        """Create advanced dataset management content"""
        try:
            from src.analysis.dataset_manager import dataset_manager
            from src.pages.dataset_management_page import create_dataset_management_page
            return create_dataset_management_page()
        except ImportError as e:
            # Fallback if the new modules are not available
            return html.Div([
                html.H2([html.I(className="fas fa-database"), " 数据集管理中心"], 
                       className="card-title"),
                html.P("数据集管理功能正在加载中...", style={'padding': '40px', 'textAlign': 'center'}),
                html.P(f"导入错误: {e}", style={'color': '#666', 'fontSize': '0.8rem'})
            ], className="card")
    
    def create_demo_content(self):
        """Create demo content with rich visualizations"""
        return html.Div([
            # Header
            html.Div([
                html.H2([html.I(className="fas fa-flask"), " TCGA-LIHC Demo分析结果"], 
                       className="card-title"),
                html.P("基于200例肝癌患者的多维度分析展示", style={'marginBottom': '20px'}),
            ], className="card"),
            
            # Key Metrics Cards
            html.Div([
                html.Div([
                    html.Div([
                        html.H5("患者数量", style={'color': '#7f8c8d'}),
                        html.H3(f"{len(self.clinical_data)}", style={'color': '#3498db'}),
                        html.P("TCGA样本", style={'fontSize': '0.9rem'})
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H5("分析基因", style={'color': '#7f8c8d'}),
                        html.H3(f"{len(self.expression_data)}", style={'color': '#27ae60'}),
                        html.P("多维度筛选", style={'fontSize': '0.9rem'})
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H5("关键靶点", style={'color': '#7f8c8d'}),
                        html.H3(f"{len(self.linchpin_data)}", style={'color': '#e74c3c'}),
                        html.P("Linchpin识别", style={'fontSize': '0.9rem'})
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H5("可成药靶点", style={'color': '#7f8c8d'}),
                        html.H3(f"{self.linchpin_data['druggable'].sum()}", style={'color': '#f39c12'}),
                        html.P("药物开发潜力", style={'fontSize': '0.9rem'})
                    ], className="metric-card"),
                ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '20px', 'marginBottom': '30px'})
            ]),
            
            # Top Linchpin Targets
            html.Div([
                html.H3([html.I(className="fas fa-crosshairs"), " Top 10 Linchpin靶点"], 
                       style={'marginBottom': '20px'}),
                dcc.Graph(
                    id='linchpin-bar-chart',
                    figure=self.create_linchpin_bar_chart(),
                    style={'height': '450px'}
                )
            ], className="card"),
            
            # Multi-dimensional Analysis
            html.Div([
                html.Div([
                    html.Div([
                        html.H3([html.I(className="fas fa-chart-radar"), " 多维度评分雷达图"]),
                        dcc.Graph(
                            id='radar-chart',
                            figure=self.create_radar_chart(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1', 'minWidth': '0'}),
                    
                    html.Div([
                        html.H3([html.I(className="fas fa-project-diagram"), " 网络中心性分布"]),
                        dcc.Graph(
                            id='network-scatter',
                            figure=self.create_network_scatter(),
                            style={'height': '400px'},
                            config={'displayModeBar': False}
                        )
                    ], style={'flex': '1', 'minWidth': '0'}),
                ], style={'display': 'flex', 'gap': '20px'})
            ], className="card"),
            
            # Survival Analysis Preview
            html.Div([
                html.H3([html.I(className="fas fa-chart-line"), " 生存分析预览"]),
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='survival-preview',
                            figure=self.create_survival_preview(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1', 'minWidth': '0'}),
                    
                    html.Div([
                        html.H4("分期分布"),
                        dcc.Graph(
                            id='stage-distribution',
                            figure=self.create_stage_distribution(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1', 'minWidth': '0'}),
                ], style={'display': 'flex', 'gap': '20px'})
            ], className="card"),
            
            # Interactive Table
            html.Div([
                html.H3([html.I(className="fas fa-table"), " Linchpin靶点详细信息"]),
                html.Div([
                    dash_table.DataTable(
                        id='linchpin-table',
                        columns=[
                            {'name': '基因', 'id': 'gene_id'},
                            {'name': 'Linchpin评分', 'id': 'linchpin_score', 'type': 'numeric', 'format': {'specifier': '.3f'}},
                            {'name': '预后评分', 'id': 'prognostic_score', 'type': 'numeric', 'format': {'specifier': '.3f'}},
                            {'name': '网络评分', 'id': 'network_hub_score', 'type': 'numeric', 'format': {'specifier': '.3f'}},
                            {'name': '可成药', 'id': 'druggable'},
                        ],
                        data=self.linchpin_data.head(10).to_dict('records'),
                        style_cell={'textAlign': 'center'},
                        style_data_conditional=[
                            {
                                'if': {'filter_query': '{druggable} = True'},
                                'backgroundColor': '#d4edda',
                                'color': 'black',
                            },
                            {
                                'if': {'column_id': 'linchpin_score', 'filter_query': '{linchpin_score} > 0.8'},
                                'backgroundColor': '#3498db',
                                'color': 'white',
                            }
                        ],
                        sort_action="native",
                        filter_action="native",
                    )
                ], style={'marginTop': '20px'})
            ], className="card"),
        ])
    
    def create_settings_content(self):
        """Create settings content"""
        return html.Div([
            # Header
            html.Div([
                html.H2([html.I(className="fas fa-cog"), " 系统设置"], className="card-title"),
                html.P("配置平台参数和个性化设置"),
            ], className="card"),
            
            # Language settings
            html.Div([
                html.H3([html.I(className="fas fa-language"), " 语言设置"]),
                html.Div([
                    html.Label("界面语言:"),
                    dcc.RadioItems(
                        id="language-selector",
                        options=[
                            {'label': ' 中文', 'value': 'zh'},
                            {'label': ' English', 'value': 'en'}
                        ],
                        value='zh',
                        inline=True,
                        style={'marginTop': '10px'}
                    )
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.Label("报告语言:"),
                    dcc.RadioItems(
                        id="report-language",
                        options=[
                            {'label': ' 中文', 'value': 'zh'},
                            {'label': ' English', 'value': 'en'},
                            {'label': ' 中英双语', 'value': 'bilingual'}
                        ],
                        value='zh',
                        inline=True,
                        style={'marginTop': '10px'}
                    )
                ])
            ], className="card"),
            
            # Analysis parameters
            html.Div([
                html.H3([html.I(className="fas fa-sliders-h"), " 分析参数"]),
                
                html.Div([
                    html.Label("P-value 阈值:"),
                    dcc.Slider(
                        id="pvalue-threshold",
                        min=0.001, max=0.1, step=0.001,
                        value=0.05,
                        marks={0.001: '0.001', 0.01: '0.01', 0.05: '0.05', 0.1: '0.1'},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], style={'marginBottom': '30px'}),
                
                html.Div([
                    html.Label("Fold Change 阈值:"),
                    dcc.Slider(
                        id="foldchange-threshold",
                        min=1, max=4, step=0.5,
                        value=2,
                        marks={1: '1', 2: '2', 3: '3', 4: '4'},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], style={'marginBottom': '30px'}),
                
                html.Div([
                    html.Label("最小样本数:"),
                    dcc.Input(
                        id="min-samples",
                        type="number",
                        value=3,
                        min=1,
                        max=100,
                        style={'width': '100px'}
                    )
                ])
            ], className="card"),
            
            # Visualization settings
            html.Div([
                html.H3([html.I(className="fas fa-palette"), " 可视化设置"]),
                
                html.Div([
                    html.Label("颜色方案:"),
                    dcc.Dropdown(
                        id="color-scheme",
                        options=[
                            {'label': '默认', 'value': 'default'},
                            {'label': '科研风格', 'value': 'scientific'},
                            {'label': '温和色调', 'value': 'warm'},
                            {'label': '冷色调', 'value': 'cool'},
                            {'label': '高对比度', 'value': 'high_contrast'}
                        ],
                        value='default',
                        style={'width': '200px'}
                    )
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.Label("图表大小:"),
                    dcc.RadioItems(
                        id="chart-size",
                        options=[
                            {'label': ' 小', 'value': 'small'},
                            {'label': ' 中', 'value': 'medium'},
                            {'label': ' 大', 'value': 'large'}
                        ],
                        value='medium',
                        inline=True
                    )
                ])
            ], className="card"),
            
            # System settings
            html.Div([
                html.H3([html.I(className="fas fa-server"), " 系统配置"]),
                
                html.Div([
                    html.Label("数据存储路径:"),
                    dcc.Input(
                        id="data-path",
                        type="text",
                        value="data/",
                        style={'width': '300px'},
                        disabled=True
                    ),
                    html.Small(" (仅管理员可修改)", style={'color': '#666'})
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    dcc.Checklist(
                        id="system-options",
                        options=[
                            {'label': ' 启用自动保存', 'value': 'autosave'},
                            {'label': ' 启用分析缓存', 'value': 'cache'},
                            {'label': ' 启用调试模式', 'value': 'debug'},
                            {'label': ' 启用并行计算', 'value': 'parallel'}
                        ],
                        value=['autosave', 'cache'],
                        inline=False
                    )
                ])
            ], className="card"),
            
            # Save settings
            html.Div([
                html.Button([
                    html.I(className="fas fa-save"),
                    " 保存设置"
                ], id="save-settings", className="btn btn-primary", style={'marginRight': '10px'}),
                
                html.Button([
                    html.I(className="fas fa-undo"),
                    " 恢复默认"
                ], id="reset-settings", className="btn btn-secondary")
            ], style={'marginTop': '20px'}),
            
            # Settings status
            html.Div(id="settings-status", style={'marginTop': '20px'})
        ])
    
    def create_linchpin_bar_chart(self):
        """Create bar chart for top linchpin targets"""
        top_genes = self.linchpin_data.head(10)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top_genes['gene_id'],
            y=top_genes['linchpin_score'],
            marker_color=top_genes['linchpin_score'].apply(
                lambda x: '#e74c3c' if x > 0.8 else '#3498db' if x > 0.7 else '#95a5a6'
            ),
            text=[f'{score:.3f}' for score in top_genes['linchpin_score']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Top 10 Linchpin靶点评分',
            xaxis_title='基因',
            yaxis_title='Linchpin Score',
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[0, 1])
        )
        
        return fig
    
    def create_radar_chart(self):
        """Create radar chart for multi-dimensional scores"""
        top_gene = self.linchpin_data.iloc[0]
        
        categories = ['Linchpin评分', '预后评分', '网络中心性', '跨维度连接', '调控潜力']
        values = [
            top_gene['linchpin_score'],
            top_gene['prognostic_score'],
            top_gene['network_hub_score'],
            top_gene['cross_domain_score'],
            top_gene['regulator_score']
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # Close the polygon
            theta=categories + [categories[0]],
            fill='toself',
            name=top_gene['gene_id'],
            fillcolor='rgba(52, 152, 219, 0.3)',
            line=dict(color='rgba(52, 152, 219, 1)', width=2)
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            title=f'{top_gene["gene_id"]} 多维度评分',
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_network_scatter(self):
        """Create scatter plot for network centrality"""
        # Load real network data if available, otherwise use mock data
        try:
            network_data = pd.read_csv('results/networks/network_centrality.csv')
            # Only take top 20 genes to avoid overcrowding
            top_genes = network_data.head(20)
        except:
            top_genes = self.network_data.head(20)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=top_genes['degree_centrality'],
            y=top_genes['betweenness_centrality'],
            mode='markers',
            marker=dict(
                size=top_genes['eigenvector_centrality'] * 20,
                color=top_genes['closeness_centrality'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Closeness')
            ),
            text=top_genes['gene_id'],
            hovertemplate='<b>%{text}</b><br>Degree: %{x:.3f}<br>Betweenness: %{y:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='基因网络中心性分布',
            xaxis_title='Degree Centrality (度中心性)',
            yaxis_title='Betweenness Centrality (介数中心性)',
            height=400,
            hovermode='closest',
            autosize=False,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    def create_survival_preview(self):
        """Create Kaplan-Meier survival curve preview"""
        # Simulate survival curves for high/low expression groups
        time_points = np.linspace(0, 3000, 100)
        
        # High expression group
        high_survival = np.exp(-time_points / 2000)
        # Low expression group
        low_survival = np.exp(-time_points / 1200)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=high_survival,
            mode='lines',
            name='High Expression',
            line=dict(color='#e74c3c', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=low_survival,
            mode='lines',
            name='Low Expression',
            line=dict(color='#3498db', width=3)
        ))
        
        fig.update_layout(
            title='VEGFR2基因表达与生存期关系',
            xaxis_title='Time (days)',
            yaxis_title='Survival Probability',
            height=400,
            hovermode='x unified',
            annotations=[
                dict(
                    x=1500, y=0.5,
                    text='P < 0.001',
                    showarrow=False,
                    font=dict(size=16, color='green')
                )
            ]
        )
        
        return fig
    
    def create_stage_distribution(self):
        """Create pie chart for stage distribution"""
        stage_counts = self.clinical_data['stage'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=stage_counts.index,
            values=stage_counts.values,
            hole=0.3,
            marker_colors=['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
        )])
        
        fig.update_layout(
            title='患者分期分布',
            height=400,
            showlegend=True,
            autosize=False,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    def create_risk_distribution(self):
        """Create risk score distribution histogram"""
        fig = go.Figure()
        
        # Risk score histogram
        fig.add_trace(go.Histogram(
            x=self.clinical_data['risk_score'],
            nbinsx=30,
            name='Risk Score Distribution',
            marker_color='#3498db',
            opacity=0.7
        ))
        
        # Add median line
        median_risk = self.clinical_data['risk_score'].median()
        fig.add_vline(x=median_risk, line_dash="dash", line_color="red",
                     annotation_text=f"Median: {median_risk:.2f}")
        
        fig.update_layout(
            title='风险评分分布',
            xaxis_title='Risk Score',
            yaxis_title='Count',
            height=400,
            hovermode='x unified',
            showlegend=False
        )
        
        return fig
    
    def create_stage_survival(self):
        """Create survival curves by stage"""
        fig = go.Figure()
        
        stages = ['I', 'II', 'III', 'IV']
        colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
        
        for stage, color in zip(stages, colors):
            # Simulate survival curve for each stage
            time_points = np.linspace(0, 3000, 100)
            base_survival = np.exp(-time_points / (2500 - 400 * stages.index(stage)))
            
            fig.add_trace(go.Scatter(
                x=time_points,
                y=base_survival,
                mode='lines',
                name=f'Stage {stage}',
                line=dict(color=color, width=3)
            ))
        
        fig.update_layout(
            title='各分期生存曲线',
            xaxis_title='Time (days)',
            yaxis_title='Survival Probability',
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    # Multi-omics integration methods
    def create_multiomics_heatmap(self):
        """Create multi-omics correlation heatmap"""
        # Calculate correlations between different omics layers
        n_genes = 20  # Top genes
        
        # Sample data from each omics layer
        expr_sample = self.expression_data.iloc[:n_genes, :50].mean(axis=1)
        cnv_sample = self.cnv_data.iloc[:n_genes, :50].mean(axis=1)
        meth_sample = self.methylation_data.iloc[:n_genes, :50].mean(axis=1)
        
        # Create correlation matrix
        omics_data = pd.DataFrame({
            'Expression': expr_sample,
            'CNV': cnv_sample,
            'Methylation': meth_sample
        })
        
        # Add mutation frequency
        mut_freq = self.mutations_data.groupby('gene_id').size()
        omics_data['Mutation_Freq'] = mut_freq.reindex(omics_data.index, fill_value=0)
        
        corr_matrix = omics_data.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title='Correlation')
        ))
        
        fig.update_layout(
            title='多组学数据层间相关性',
            height=500,
            xaxis_title='数据类型',
            yaxis_title='数据类型'
        )
        
        return fig
    
    def create_integration_scores(self):
        """Create integration scores visualization"""
        # Calculate integration scores for top genes
        top_genes = self.linchpin_data['gene_id'].head(15)
        
        # Simulate integration scores
        integration_data = []
        for gene in top_genes:
            integration_data.append({
                'gene': gene,
                'expression_score': np.random.uniform(0.5, 1),
                'cnv_score': np.random.uniform(0.3, 0.8),
                'methylation_score': np.random.uniform(0.4, 0.9),
                'mutation_score': np.random.uniform(0.2, 0.7),
                'integrated_score': np.random.uniform(0.6, 0.95)
            })
        
        df = pd.DataFrame(integration_data)
        
        fig = go.Figure()
        
        # Add traces for each score type
        fig.add_trace(go.Bar(name='Expression', x=df['gene'], y=df['expression_score']))
        fig.add_trace(go.Bar(name='CNV', x=df['gene'], y=df['cnv_score']))
        fig.add_trace(go.Bar(name='Methylation', x=df['gene'], y=df['methylation_score']))
        fig.add_trace(go.Bar(name='Mutation', x=df['gene'], y=df['mutation_score']))
        
        # Add integrated score as line
        fig.add_trace(go.Scatter(
            name='Integrated Score',
            x=df['gene'],
            y=df['integrated_score'],
            mode='lines+markers',
            line=dict(color='red', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='多组学整合评分',
            xaxis_title='基因',
            yaxis_title='组学评分',
            yaxis2=dict(
                title='整合评分',
                overlaying='y',
                side='right',
                range=[0, 1]
            ),
            barmode='group',
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def create_pathway_enrichment(self):
        """Create pathway enrichment visualization"""
        # Simulate pathway enrichment data
        pathways = [
            'Cell cycle', 'DNA repair', 'Apoptosis', 'PI3K-Akt signaling',
            'p53 signaling', 'MAPK signaling', 'Wnt signaling', 'JAK-STAT signaling',
            'TGF-beta signaling', 'mTOR signaling'
        ]
        
        enrichment_data = []
        for pathway in pathways:
            enrichment_data.append({
                'pathway': pathway,
                'pvalue': np.random.uniform(0.0001, 0.05),
                'gene_count': np.random.randint(5, 30),
                'fold_enrichment': np.random.uniform(1.5, 5)
            })
        
        df = pd.DataFrame(enrichment_data)
        df['-log10(p-value)'] = -np.log10(df['pvalue'])
        df = df.sort_values('-log10(p-value)', ascending=True)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['-log10(p-value)'],
            y=df['pathway'],
            orientation='h',
            marker=dict(
                color=df['fold_enrichment'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Fold Enrichment')
            ),
            text=[f'{count} genes' for count in df['gene_count']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='通路富集分析',
            xaxis_title='-log10(p-value)',
            yaxis_title='通路',
            height=400,
            margin=dict(l=150)
        )
        
        # Add significance line
        fig.add_vline(x=-np.log10(0.05), line_dash="dash", line_color="red",
                     annotation_text="p=0.05")
        
        return fig
    
    def create_mutation_landscape(self):
        """Create mutation landscape visualization"""
        # Get top mutated genes
        mut_counts = self.mutations_data.groupby('gene_id').size().sort_values(ascending=False).head(20)
        
        # Create mutation matrix
        mutation_matrix = []
        for gene in mut_counts.index:
            gene_muts = self.mutations_data[self.mutations_data['gene_id'] == gene]
            mut_types = gene_muts.groupby('mutation_type').size()
            mutation_matrix.append({
                'gene': gene,
                'missense': mut_types.get('missense', 0),
                'nonsense': mut_types.get('nonsense', 0),
                'frameshift': mut_types.get('frameshift', 0),
                'silent': mut_types.get('silent', 0),
                'total': len(gene_muts)
            })
        
        df = pd.DataFrame(mutation_matrix)
        
        fig = go.Figure()
        
        # Add stacked bars for mutation types
        fig.add_trace(go.Bar(name='Missense', x=df['gene'], y=df['missense'], marker_color='#3498db'))
        fig.add_trace(go.Bar(name='Nonsense', x=df['gene'], y=df['nonsense'], marker_color='#e74c3c'))
        fig.add_trace(go.Bar(name='Frameshift', x=df['gene'], y=df['frameshift'], marker_color='#f39c12'))
        fig.add_trace(go.Bar(name='Silent', x=df['gene'], y=df['silent'], marker_color='#95a5a6'))
        
        fig.update_layout(
            title='突变景观图',
            xaxis_title='基因',
            yaxis_title='突变数量',
            barmode='stack',
            height=450,
            hovermode='x unified'
        )
        
        return fig
    
    # ClosedLoop analysis methods
    def create_causal_network(self):
        """Create causal network visualization"""
        # Create network nodes and edges
        nodes = ['TP53', 'EGFR', 'KRAS', 'PIK3CA', 'PTEN', 'AKT1', 'MTOR', 'MYC', 'VEGFR2', 'IL6']
        
        # Create edge list with evidence weights
        edges = [
            ('TP53', 'PTEN', 0.8), ('EGFR', 'KRAS', 0.9), ('KRAS', 'PIK3CA', 0.7),
            ('PIK3CA', 'AKT1', 0.85), ('PTEN', 'AKT1', -0.7), ('AKT1', 'MTOR', 0.9),
            ('MTOR', 'MYC', 0.6), ('MYC', 'VEGFR2', 0.5), ('EGFR', 'IL6', 0.4),
            ('IL6', 'VEGFR2', 0.6), ('TP53', 'MYC', -0.5)
        ]
        
        # Create Sankey diagram for causal flow
        source_indices = [nodes.index(e[0]) for e in edges]
        target_indices = [nodes.index(e[1]) for e in edges]
        values = [abs(e[2]) * 10 for e in edges]
        colors = ['rgba(231, 76, 60, 0.4)' if e[2] < 0 else 'rgba(52, 152, 219, 0.4)' for e in edges]
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=nodes,
                color=['#3498db', '#e74c3c', '#f39c12', '#2ecc71', '#9b59b6',
                      '#1abc9c', '#34495e', '#e67e22', '#7f8c8d', '#27ae60']
            ),
            link=dict(
                source=source_indices,
                target=target_indices,
                value=values,
                color=colors,
                label=[f'Evidence: {e[2]:.2f}' for e in edges]
            )
        )])
        
        fig.update_layout(
            title='因果关系网络',
            height=600,
            font_size=12
        )
        
        return fig
    
    def create_evidence_weights(self):
        """Create evidence weights distribution"""
        # Simulate evidence types and weights
        evidence_types = ['Literature', 'Experiment', 'Database', 'Prediction', 'Clinical']
        
        evidence_data = []
        for evidence_type in evidence_types:
            n_evidences = np.random.randint(20, 50)
            weights = np.random.beta(5, 2, n_evidences)
            for weight in weights:
                evidence_data.append({
                    'type': evidence_type,
                    'weight': weight
                })
        
        df = pd.DataFrame(evidence_data)
        
        fig = go.Figure()
        
        for evidence_type in evidence_types:
            type_data = df[df['type'] == evidence_type]['weight']
            fig.add_trace(go.Violin(
                x=[evidence_type] * len(type_data),
                y=type_data,
                name=evidence_type,
                box_visible=True,
                meanline_visible=True
            ))
        
        fig.update_layout(
            title='证据权重分布',
            xaxis_title='证据类型',
            yaxis_title='权重值',
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_inference_confidence(self):
        """Create inference confidence visualization"""
        # Simulate confidence scores for different inference types
        inference_types = ['Direct', 'Indirect', 'Transitive', 'Negative', 'Complex']
        
        confidence_data = []
        for inf_type in inference_types:
            confidence_data.append({
                'type': inf_type,
                'mean_confidence': np.random.uniform(0.6, 0.95),
                'std_confidence': np.random.uniform(0.05, 0.15),
                'n_inferences': np.random.randint(10, 100)
            })
        
        df = pd.DataFrame(confidence_data)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['type'],
            y=df['mean_confidence'],
            error_y=dict(
                type='data',
                array=df['std_confidence'],
                visible=True
            ),
            marker_color=df['mean_confidence'],
            marker_colorscale='Viridis',
            text=[f'n={n}' for n in df['n_inferences']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='推理置信度分析',
            xaxis_title='推理类型',
            yaxis_title='平均置信度',
            height=400,
            yaxis_range=[0, 1.1]
        )
        
        # Add confidence threshold line
        fig.add_hline(y=0.8, line_dash="dash", line_color="red",
                     annotation_text="高置信度阈值")
        
        return fig
    
    def create_feedback_loops(self):
        """Create feedback loops visualization"""
        # Define feedback loops
        loops = [
            {'name': 'PI3K-AKT-MTOR', 'strength': 0.85, 'type': 'Positive', 'genes': 5},
            {'name': 'p53-MDM2', 'strength': -0.9, 'type': 'Negative', 'genes': 3},
            {'name': 'EGFR-RAS-RAF', 'strength': 0.75, 'type': 'Positive', 'genes': 4},
            {'name': 'Wnt-βcatenin', 'strength': 0.7, 'type': 'Positive', 'genes': 6},
            {'name': 'NF-κB-IκB', 'strength': -0.8, 'type': 'Negative', 'genes': 4}
        ]
        
        df = pd.DataFrame(loops)
        df['abs_strength'] = df['strength'].abs()
        
        fig = go.Figure()
        
        # Create bubble chart
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['abs_strength'],
            mode='markers+text',
            marker=dict(
                size=df['genes'] * 15,
                color=df['strength'],
                colorscale='RdBu',
                cmid=0,
                showscale=True,
                colorbar=dict(title='Loop Strength')
            ),
            text=df['name'],
            textposition='top center'
        ))
        
        # Add loop type annotations
        for idx, row in df.iterrows():
            fig.add_annotation(
                x=idx,
                y=row['abs_strength'] - 0.05,
                text=row['type'],
                showarrow=False,
                font=dict(size=10)
            )
        
        fig.update_layout(
            title='关键反馈环路识别',
            xaxis_title='反馈环路',
            yaxis_title='环路强度（绝对值）',
            height=450,
            xaxis=dict(showticklabels=False),
            yaxis_range=[0, 1.1]
        )
        
        return fig
    
    # Comprehensive charts methods
    def create_comprehensive_radar(self):
        """Create comprehensive scores radar chart"""
        # Define evaluation dimensions
        dimensions = ['生存预后', '网络中心性', '多组学整合', '因果关联', '可成药性', '临床相关性']
        
        # Create data for top 3 genes
        top_genes = self.linchpin_data.head(3)
        
        fig = go.Figure()
        
        for idx, gene in enumerate(top_genes['gene_id']):
            scores = np.random.uniform(0.6, 0.95, len(dimensions))
            
            fig.add_trace(go.Scatterpolar(
                r=scores.tolist() + [scores[0]],  # Close the polygon
                theta=dimensions + [dimensions[0]],
                fill='toself',
                name=gene,
                fillcolor=f'rgba({50+idx*50}, {100+idx*30}, {200-idx*40}, 0.2)',
                line=dict(width=2)
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            title='综合评分雷达图',
            height=500,
            showlegend=True
        )
        
        return fig
    
    def create_multidim_scatter(self):
        """Create multi-dimensional scatter plot"""
        # Use PCA-like coordinates for visualization
        n_genes = 50
        
        # Simulate multi-dimensional data
        scatter_data = []
        for i in range(n_genes):
            scatter_data.append({
                'gene': f'Gene_{i:03d}',
                'dim1': np.random.normal(0, 1),
                'dim2': np.random.normal(0, 1),
                'cluster': np.random.choice(['Cluster A', 'Cluster B', 'Cluster C']),
                'importance': np.random.uniform(0.3, 1)
            })
        
        df = pd.DataFrame(scatter_data)
        
        fig = px.scatter(
            df, x='dim1', y='dim2',
            color='cluster',
            size='importance',
            hover_data=['gene'],
            title='多维度数据降维可视化'
        )
        
        fig.update_layout(
            xaxis_title='主成分 1',
            yaxis_title='主成分 2',
            height=450
        )
        
        return fig
    
    def create_cluster_analysis(self):
        """Create cluster analysis visualization"""
        # Simulate clustering results
        n_samples = 100
        
        # Generate clustered data
        cluster_data = []
        for cluster in range(3):
            cluster_center = np.random.randn(2) * 2
            for _ in range(n_samples // 3):
                point = cluster_center + np.random.randn(2) * 0.5
                cluster_data.append({
                    'x': point[0],
                    'y': point[1],
                    'cluster': f'Cluster {cluster + 1}',
                    'sample': f'S{len(cluster_data)}'
                })
        
        df = pd.DataFrame(cluster_data)
        
        fig = go.Figure()
        
        # Add scatter points
        for cluster in df['cluster'].unique():
            cluster_df = df[df['cluster'] == cluster]
            fig.add_trace(go.Scatter(
                x=cluster_df['x'],
                y=cluster_df['y'],
                mode='markers',
                name=cluster,
                marker=dict(size=8)
            ))
        
        # Add cluster centers
        for cluster in df['cluster'].unique():
            cluster_df = df[df['cluster'] == cluster]
            center_x = cluster_df['x'].mean()
            center_y = cluster_df['y'].mean()
            fig.add_trace(go.Scatter(
                x=[center_x],
                y=[center_y],
                mode='markers',
                marker=dict(size=20, symbol='x'),
                showlegend=False,
                name=f'{cluster} Center'
            ))
        
        fig.update_layout(
            title='样本聚类分析',
            xaxis_title='特征 1',
            yaxis_title='特征 2',
            height=450
        )
        
        return fig
    
    def create_integrated_heatmap(self):
        """Create integrated analysis heatmap"""
        # Select top genes and samples
        top_genes = self.linchpin_data['gene_id'].head(20)
        samples = self.clinical_data.index[:30]
        
        # Create integrated score matrix
        integrated_matrix = np.random.randn(len(top_genes), len(samples))
        
        # Add patterns
        integrated_matrix[:5, :10] += 2  # High expression cluster
        integrated_matrix[10:15, 15:25] -= 2  # Low expression cluster
        
        fig = go.Figure(data=go.Heatmap(
            z=integrated_matrix,
            x=samples,
            y=top_genes,
            colorscale='RdBu',
            zmid=0,
            colorbar=dict(title='Integrated Score')
        ))
        
        fig.update_layout(
            title='整合分析热图',
            xaxis_title='样本',
            yaxis_title='基因',
            height=600,
            xaxis=dict(tickangle=-45)
        )
        
        return fig
    
    # Precision Medicine Analysis Methods
    def create_immune_content(self):
        """Create immune microenvironment analysis content"""
        # Import dataset selector
        try:
            from src.components.dataset_selector import create_dataset_selector, create_data_source_indicator
            dataset_selector = create_dataset_selector(self.dataset_manager, 'immune-dataset-selector')
            current_dataset = self.dataset_manager.get_current_dataset() if self.dataset_manager else {'name': 'Demo', 'type': 'demo'}
            data_indicator = create_data_source_indicator(current_dataset)
        except:
            dataset_selector = html.Div()
            data_indicator = html.Div()
            
        return html.Div([
            # Dataset selector at top
            dataset_selector,
            
            # Header
            html.Div([
                data_indicator,  # Data source indicator
                html.H2([html.I(className="fas fa-shield-alt"), " 免疫微环境分析"], className="card-title"),
                html.P("肿瘤免疫微环境综合评估与免疫治疗响应预测"),
            ], className="card", style={'position': 'relative'}),
            
            # Analysis content container
            html.Div(id='immune-analysis-content'),
            
            # Immune cell infiltration
            html.Div([
                html.H3([html.I(className="fas fa-users"), " 免疫细胞浸润评分"]),
                dcc.Graph(
                    id='immune-infiltration',
                    figure=self.create_immune_infiltration(),
                    style={'height': '500px'}
                )
            ], className="card"),
            
            # Immune checkpoint expression
            html.Div([
                html.Div([
                    html.Div([
                        html.H3([html.I(className="fas fa-lock"), " 免疫检查点表达"]),
                        dcc.Graph(
                            id='checkpoint-expression',
                            figure=self.create_checkpoint_expression(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'}),
                    
                    html.Div([
                        html.H3([html.I(className="fas fa-chart-pie"), " 免疫亚型分布"]),
                        dcc.Graph(
                            id='immune-subtypes',
                            figure=self.create_immune_subtypes(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px'})
            ], className="card"),
            
            # Immunotherapy response prediction
            html.Div([
                html.H3([html.I(className="fas fa-chart-line"), " 免疫治疗响应预测"]),
                dcc.Graph(
                    id='immunotherapy-prediction',
                    figure=self.create_immunotherapy_prediction(),
                    style={'height': '450px'}
                )
            ], className="card")
        ])
    
    def create_drug_content(self):
        """Create drug response analysis content"""
        # Import dataset selector
        try:
            from src.components.dataset_selector import create_dataset_selector, create_data_source_indicator
            dataset_selector = create_dataset_selector(self.dataset_manager, 'drug-dataset-selector')
            current_dataset = self.dataset_manager.get_current_dataset() if self.dataset_manager else {'name': 'Demo', 'type': 'demo'}
            data_indicator = create_data_source_indicator(current_dataset)
        except:
            dataset_selector = html.Div()
            data_indicator = html.Div()
            
        return html.Div([
            # Dataset selector at top
            dataset_selector,
            
            # Header
            html.Div([
                data_indicator,  # Data source indicator
                html.H2([html.I(className="fas fa-pills"), " 药物响应与耐药分析"], className="card-title"),
                html.P("个体化药物敏感性预测与耐药机制识别"),
            ], className="card", style={'position': 'relative'}),
            
            # Analysis content container
            html.Div(id='drug-analysis-content'),
            
            # Drug sensitivity prediction
            html.Div([
                html.H3([html.I(className="fas fa-vial"), " 药物敏感性预测"]),
                dcc.Graph(
                    id='drug-sensitivity',
                    figure=self.create_drug_sensitivity(),
                    style={'height': '500px'}
                )
            ], className="card"),
            
            # Resistance mechanisms
            html.Div([
                html.Div([
                    html.Div([
                        html.H3([html.I(className="fas fa-dna"), " 耐药机制分析"]),
                        dcc.Graph(
                            id='resistance-mechanisms',
                            figure=self.create_resistance_mechanisms(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'}),
                    
                    html.Div([
                        html.H3([html.I(className="fas fa-tablets"), " 联合用药优化"]),
                        dcc.Graph(
                            id='drug-combinations',
                            figure=self.create_drug_combinations(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px'})
            ], className="card"),
            
            # Personalized treatment
            html.Div([
                html.H3([html.I(className="fas fa-user-md"), " 个体化治疗方案"]),
                dcc.Graph(
                    id='personalized-treatment',
                    figure=self.create_personalized_treatment(),
                    style={'height': '450px'}
                )
            ], className="card")
        ])
    
    def create_subtype_content(self):
        """Create molecular subtype analysis content"""
        # Import dataset selector
        try:
            from src.components.dataset_selector import create_dataset_selector, create_data_source_indicator
            dataset_selector = create_dataset_selector(self.dataset_manager, 'subtype-dataset-selector')
            current_dataset = self.dataset_manager.get_current_dataset() if self.dataset_manager else {'name': 'Demo', 'type': 'demo'}
            data_indicator = create_data_source_indicator(current_dataset)
        except:
            dataset_selector = html.Div()
            data_indicator = html.Div()
            
        return html.Div([
            # Dataset selector at top
            dataset_selector,
            
            # Header
            html.Div([
                data_indicator,  # Data source indicator
                html.H2([html.I(className="fas fa-layer-group"), " 分子亚型精细分类"], className="card-title"),
                html.P("基于多组学数据的肿瘤分子亚型识别与特征分析"),
            ], className="card", style={'position': 'relative'}),
            
            # Analysis content container
            html.Div(id='subtype-analysis-content'),
            
            # Subtype clustering
            html.Div([
                html.H3([html.I(className="fas fa-project-diagram"), " 无监督聚类分型"]),
                dcc.Graph(
                    id='subtype-clustering',
                    figure=self.create_subtype_clustering(),
                    style={'height': '500px'}
                )
            ], className="card"),
            
            # Subtype characteristics
            html.Div([
                html.Div([
                    html.Div([
                        html.H3([html.I(className="fas fa-fingerprint"), " 亚型特征图谱"]),
                        dcc.Graph(
                            id='subtype-features',
                            figure=self.create_subtype_features(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'}),
                    
                    html.Div([
                        html.H3([html.I(className="fas fa-chart-bar"), " 亚型生存差异"]),
                        dcc.Graph(
                            id='subtype-survival',
                            figure=self.create_subtype_survival(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px'})
            ], className="card"),
            
            # Subtype drivers
            html.Div([
                html.H3([html.I(className="fas fa-cogs"), " 亚型驱动事件"]),
                dcc.Graph(
                    id='subtype-drivers',
                    figure=self.create_subtype_drivers(),
                    style={'height': '450px'}
                )
            ], className="card")
        ])
    
    def create_metabolism_content(self):
        """Create metabolism analysis content"""
        # Import dataset selector
        try:
            from src.components.dataset_selector import create_dataset_selector, create_data_source_indicator
            dataset_selector = create_dataset_selector(self.dataset_manager, 'metabolism-dataset-selector')
            current_dataset = self.dataset_manager.get_current_dataset() if self.dataset_manager else {'name': 'Demo', 'type': 'demo'}
            data_indicator = create_data_source_indicator(current_dataset)
        except:
            dataset_selector = html.Div()
            data_indicator = html.Div()
            
        return html.Div([
            # Dataset selector at top
            dataset_selector,
            
            # Header
            html.Div([
                data_indicator,  # Data source indicator
                html.H2([html.I(className="fas fa-fire"), " 代谢重编程分析"], className="card-title"),
                html.P("肿瘤代谢通路活性评估与代谢靶向治疗机会识别"),
            ], className="card", style={'position': 'relative'}),
            
            # Analysis content container
            html.Div(id='metabolism-analysis-content'),
            
            # Metabolic pathway activity
            html.Div([
                html.H3([html.I(className="fas fa-burn"), " 代谢通路活性"]),
                dcc.Graph(
                    id='metabolic-activity',
                    figure=self.create_metabolic_activity(),
                    style={'height': '500px'}
                )
            ], className="card"),
            
            # Metabolic dependencies
            html.Div([
                html.Div([
                    html.Div([
                        html.H3([html.I(className="fas fa-battery-half"), " 代谢依赖性"]),
                        dcc.Graph(
                            id='metabolic-dependencies',
                            figure=self.create_metabolic_dependencies(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'}),
                    
                    html.Div([
                        html.H3([html.I(className="fas fa-exchange-alt"), " 代谢-免疫串扰"]),
                        dcc.Graph(
                            id='metabolic-immune',
                            figure=self.create_metabolic_immune(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px'})
            ], className="card"),
            
            # Metabolic targets
            html.Div([
                html.H3([html.I(className="fas fa-crosshairs"), " 代谢靶向机会"]),
                dcc.Graph(
                    id='metabolic-targets',
                    figure=self.create_metabolic_targets(),
                    style={'height': '450px'}
                )
            ], className="card")
        ])
    
    def create_heterogeneity_content(self):
        """Create tumor heterogeneity analysis content"""
        # Import dataset selector
        try:
            from src.components.dataset_selector import create_dataset_selector, create_data_source_indicator
            dataset_selector = create_dataset_selector(self.dataset_manager, 'heterogeneity-dataset-selector')
            current_dataset = self.dataset_manager.get_current_dataset() if self.dataset_manager else {'name': 'Demo', 'type': 'demo'}
            data_indicator = create_data_source_indicator(current_dataset)
        except:
            dataset_selector = html.Div()
            data_indicator = html.Div()
            
        return html.Div([
            # Dataset selector at top
            dataset_selector,
            
            # Header
            html.Div([
                data_indicator,  # Data source indicator
                html.H2([html.I(className="fas fa-code-branch"), " 肿瘤异质性与进化分析"], className="card-title"),
                html.P("肿瘤克隆结构、进化轨迹与时空异质性综合分析"),
            ], className="card", style={'position': 'relative'}),
            
            # Analysis content container
            html.Div(id='heterogeneity-analysis-content'),
            
            # Clonal structure
            html.Div([
                html.H3([html.I(className="fas fa-sitemap"), " 克隆结构分析"]),
                dcc.Graph(
                    id='clonal-structure',
                    figure=self.create_clonal_structure(),
                    style={'height': '500px'}
                )
            ], className="card"),
            
            # Evolution and heterogeneity
            html.Div([
                html.Div([
                    html.Div([
                        html.H3([html.I(className="fas fa-history"), " 进化轨迹"]),
                        dcc.Graph(
                            id='evolution-trajectory',
                            figure=self.create_evolution_trajectory(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'}),
                    
                    html.Div([
                        html.H3([html.I(className="fas fa-globe"), " 空间异质性"]),
                        dcc.Graph(
                            id='spatial-heterogeneity',
                            figure=self.create_spatial_heterogeneity(),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px'})
            ], className="card"),
            
            # Temporal dynamics
            html.Div([
                html.H3([html.I(className="fas fa-clock"), " 时间动态变化"]),
                dcc.Graph(
                    id='temporal-dynamics',
                    figure=self.create_temporal_dynamics(),
                    style={'height': '450px'}
                )
            ], className="card")
        ])
    
    # Immune analysis visualization methods
    def create_immune_infiltration(self):
        """Create immune cell infiltration heatmap"""
        # Define immune cell types
        immune_cells = [
            'CD8+ T cells', 'CD4+ T cells', 'Regulatory T cells', 'B cells',
            'NK cells', 'Macrophages M1', 'Macrophages M2', 'Dendritic cells',
            'Neutrophils', 'Monocytes', 'Mast cells', 'Eosinophils'
        ]
        
        # Simulate infiltration scores for top samples
        samples = self.clinical_data.index[:30]
        infiltration_matrix = np.random.beta(2, 5, (len(immune_cells), len(samples)))
        
        # Add patterns
        infiltration_matrix[0:2, :10] += 0.3  # High T cell infiltration
        infiltration_matrix[5:7, 15:25] += 0.4  # High macrophage infiltration
        
        fig = go.Figure(data=go.Heatmap(
            z=infiltration_matrix,
            x=samples,
            y=immune_cells,
            colorscale='Viridis',
            colorbar=dict(title='Infiltration Score')
        ))
        
        fig.update_layout(
            title='免疫细胞浸润评分热图',
            xaxis_title='样本',
            yaxis_title='免疫细胞类型',
            height=500,
            xaxis=dict(tickangle=-45)
        )
        
        return fig
    
    def create_checkpoint_expression(self):
        """Create immune checkpoint expression visualization"""
        checkpoints = ['PD-1', 'PD-L1', 'CTLA-4', 'LAG-3', 'TIM-3', 'TIGIT', 'VISTA', 'B7-H3']
        
        # Simulate expression data
        expression_data = []
        for checkpoint in checkpoints:
            expression_data.append({
                'checkpoint': checkpoint,
                'mean_expression': np.random.uniform(0.3, 0.9),
                'std_expression': np.random.uniform(0.1, 0.3),
                'positive_rate': np.random.uniform(0.2, 0.8)
            })
        
        df = pd.DataFrame(expression_data)
        
        fig = go.Figure()
        
        # Add bar chart with error bars
        fig.add_trace(go.Bar(
            x=df['checkpoint'],
            y=df['mean_expression'],
            error_y=dict(
                type='data',
                array=df['std_expression'],
                visible=True
            ),
            marker_color=df['positive_rate'],
            marker_colorscale='RdBu',
            text=[f'{rate:.1%}' for rate in df['positive_rate']],
            textposition='outside',
            name='Expression Level'
        ))
        
        fig.update_layout(
            title='免疫检查点表达谱',
            xaxis_title='免疫检查点',
            yaxis_title='平均表达水平',
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_immune_subtypes(self):
        """Create immune subtype distribution"""
        # Define immune subtypes
        subtypes = {
            'Immune Hot': 25,
            'Immune Warm': 35,
            'Immune Cold': 30,
            'Immune Excluded': 10
        }
        
        colors = ['#e74c3c', '#f39c12', '#3498db', '#95a5a6']
        
        fig = go.Figure(data=[go.Pie(
            labels=list(subtypes.keys()),
            values=list(subtypes.values()),
            hole=0.3,
            marker_colors=colors,
            textinfo='label+percent'
        )])
        
        fig.update_layout(
            title='免疫亚型分布',
            height=400,
            annotations=[dict(text='N=100', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        return fig
    
    def create_immunotherapy_prediction(self):
        """Create immunotherapy response prediction"""
        # Simulate prediction scores
        biomarkers = ['TMB Score', 'MSI Status', 'PD-L1 Expression', 'Immune Score', 'IFN-γ Signature']
        
        # Create data for different response groups
        responders = np.random.beta(5, 2, len(biomarkers))
        non_responders = np.random.beta(2, 5, len(biomarkers))
        
        fig = go.Figure()
        
        # Add traces
        fig.add_trace(go.Scatter(
            x=biomarkers,
            y=responders,
            mode='lines+markers',
            name='Responders',
            line=dict(color='#27ae60', width=3),
            marker=dict(size=10)
        ))
        
        fig.add_trace(go.Scatter(
            x=biomarkers,
            y=non_responders,
            mode='lines+markers',
            name='Non-responders',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title='免疫治疗响应预测评分',
            xaxis_title='生物标志物',
            yaxis_title='标准化评分',
            height=450,
            yaxis_range=[0, 1]
        )
        
        return fig
    
    # Drug response visualization methods
    def create_drug_sensitivity(self):
        """Create drug sensitivity heatmap"""
        # Define drugs and samples
        drugs = [
            'Sorafenib', 'Lenvatinib', 'Regorafenib', 'Cabozantinib',
            'Atezolizumab', 'Bevacizumab', 'Ramucirumab', 'Nivolumab',
            'Pembrolizumab', 'Durvalumab', 'Tremelimumab', 'Ipilimumab'
        ]
        
        samples = self.clinical_data.index[:20]
        
        # Simulate IC50 values (log scale)
        ic50_matrix = np.random.normal(0, 2, (len(drugs), len(samples)))
        
        # Add patterns
        ic50_matrix[0:4, :5] -= 2  # Sensitive to kinase inhibitors
        ic50_matrix[4:8, 10:15] -= 1.5  # Sensitive to immunotherapy
        
        fig = go.Figure(data=go.Heatmap(
            z=ic50_matrix,
            x=samples,
            y=drugs,
            colorscale='RdBu_r',
            zmid=0,
            colorbar=dict(title='log(IC50)')
        ))
        
        fig.update_layout(
            title='药物敏感性预测热图',
            xaxis_title='患者样本',
            yaxis_title='药物',
            height=500,
            xaxis=dict(tickangle=-45)
        )
        
        return fig
    
    def create_resistance_mechanisms(self):
        """Create resistance mechanisms visualization"""
        # Define resistance mechanisms
        mechanisms = {
            'ABC Transporters': np.random.uniform(0.3, 0.8, 5),
            'DNA Repair': np.random.uniform(0.4, 0.9, 5),
            'Apoptosis Evasion': np.random.uniform(0.5, 0.85, 5),
            'EMT Markers': np.random.uniform(0.2, 0.7, 5),
            'Stemness': np.random.uniform(0.3, 0.6, 5)
        }
        
        fig = go.Figure()
        
        for i, (mechanism, values) in enumerate(mechanisms.items()):
            fig.add_trace(go.Box(
                y=values,
                name=mechanism,
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8,
                marker_color=f'hsl({i*60}, 70%, 50%)'
            ))
        
        fig.update_layout(
            title='耐药机制活性评分',
            yaxis_title='活性评分',
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_drug_combinations(self):
        """Create drug combination synergy matrix"""
        # Define drugs for combination
        drugs = ['Sorafenib', 'Atezolizumab', 'Bevacizumab', 'Lenvatinib', 'Pembrolizumab']
        
        # Create synergy matrix
        n_drugs = len(drugs)
        synergy_matrix = np.random.uniform(-0.5, 1.5, (n_drugs, n_drugs))
        np.fill_diagonal(synergy_matrix, 0)
        
        # Make matrix symmetric
        synergy_matrix = (synergy_matrix + synergy_matrix.T) / 2
        
        fig = go.Figure(data=go.Heatmap(
            z=synergy_matrix,
            x=drugs,
            y=drugs,
            colorscale='RdBu',
            zmid=0,
            text=np.round(synergy_matrix, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title='Synergy Score')
        ))
        
        fig.update_layout(
            title='药物联合协同效应',
            height=400
        )
        
        return fig
    
    def create_personalized_treatment(self):
        """Create personalized treatment recommendation"""
        # Simulate treatment options with scores
        treatments = [
            {'name': 'Sorafenib + Atezolizumab', 'efficacy': 0.85, 'toxicity': 0.3, 'confidence': 0.9},
            {'name': 'Lenvatinib + Pembrolizumab', 'efficacy': 0.82, 'toxicity': 0.35, 'confidence': 0.85},
            {'name': 'Regorafenib monotherapy', 'efficacy': 0.65, 'toxicity': 0.25, 'confidence': 0.7},
            {'name': 'Cabozantinib + Nivolumab', 'efficacy': 0.78, 'toxicity': 0.4, 'confidence': 0.75},
            {'name': 'Best supportive care', 'efficacy': 0.3, 'toxicity': 0.1, 'confidence': 0.95}
        ]
        
        df = pd.DataFrame(treatments)
        
        fig = go.Figure()
        
        # Create bubble chart
        fig.add_trace(go.Scatter(
            x=df['toxicity'],
            y=df['efficacy'],
            mode='markers+text',
            marker=dict(
                size=df['confidence'] * 50,
                color=df['confidence'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Confidence')
            ),
            text=df['name'],
            textposition='top center'
        ))
        
        fig.update_layout(
            title='个体化治疗方案推荐',
            xaxis_title='毒性风险',
            yaxis_title='预期疗效',
            height=450,
            xaxis_range=[-0.1, 0.5],
            yaxis_range=[0, 1]
        )
        
        # Add quadrant lines
        fig.add_hline(y=0.7, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=0.3, line_dash="dash", line_color="gray", opacity=0.5)
        
        return fig
    
    # Molecular subtype visualization methods
    def create_subtype_clustering(self):
        """Create molecular subtype clustering visualization"""
        # Simulate t-SNE coordinates for samples
        n_samples = 200
        
        # Create clusters
        cluster_centers = [(-5, -5), (5, -5), (0, 5), (-3, 3), (3, 3)]
        cluster_labels = ['Metabolic', 'Proliferative', 'Immune', 'Mesenchymal', 'Mixed']
        cluster_colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
        
        scatter_data = []
        for i, (center, label) in enumerate(zip(cluster_centers, cluster_labels)):
            n_cluster = n_samples // len(cluster_centers)
            x = np.random.normal(center[0], 1.5, n_cluster)
            y = np.random.normal(center[1], 1.5, n_cluster)
            for j in range(n_cluster):
                scatter_data.append({
                    'x': x[j],
                    'y': y[j],
                    'subtype': label,
                    'sample_id': f'S{i*n_cluster+j}'
                })
        
        df = pd.DataFrame(scatter_data)
        
        fig = px.scatter(
            df, x='x', y='y',
            color='subtype',
            color_discrete_sequence=cluster_colors,
            title='分子亚型聚类分析 (t-SNE)'
        )
        
        fig.update_layout(
            xaxis_title='t-SNE 1',
            yaxis_title='t-SNE 2',
            height=500
        )
        
        return fig
    
    def create_subtype_features(self):
        """Create subtype feature heatmap"""
        # Define features and subtypes
        features = [
            'Cell Cycle', 'DNA Repair', 'Angiogenesis', 'EMT',
            'Immune Response', 'Metabolism', 'Stemness', 'Hypoxia'
        ]
        subtypes = ['Metabolic', 'Proliferative', 'Immune', 'Mesenchymal', 'Mixed']
        
        # Create feature matrix
        feature_matrix = np.random.randn(len(features), len(subtypes))
        
        # Add subtype-specific patterns
        feature_matrix[5, 0] = 2.5  # Metabolic subtype
        feature_matrix[0:2, 1] = 2  # Proliferative subtype
        feature_matrix[4, 2] = 2.5  # Immune subtype
        feature_matrix[3, 3] = 2.5  # Mesenchymal subtype
        
        fig = go.Figure(data=go.Heatmap(
            z=feature_matrix,
            x=subtypes,
            y=features,
            colorscale='RdBu',
            zmid=0,
            colorbar=dict(title='Enrichment Score')
        ))
        
        fig.update_layout(
            title='亚型特征富集评分',
            xaxis_title='分子亚型',
            yaxis_title='生物学特征',
            height=400
        )
        
        return fig
    
    def create_subtype_survival(self):
        """Create survival curves by subtype"""
        subtypes = ['Metabolic', 'Proliferative', 'Immune', 'Mesenchymal', 'Mixed']
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
        
        fig = go.Figure()
        
        time_points = np.linspace(0, 3000, 100)
        
        for i, (subtype, color) in enumerate(zip(subtypes, colors)):
            # Different survival rates for subtypes
            if subtype == 'Immune':
                survival = np.exp(-time_points / 2500)  # Best survival
            elif subtype == 'Mesenchymal':
                survival = np.exp(-time_points / 1000)  # Worst survival
            else:
                survival = np.exp(-time_points / (1500 + i * 200))
            
            fig.add_trace(go.Scatter(
                x=time_points,
                y=survival,
                mode='lines',
                name=subtype,
                line=dict(color=color, width=3)
            ))
        
        fig.update_layout(
            title='各分子亚型生存曲线',
            xaxis_title='Time (days)',
            yaxis_title='Survival Probability',
            height=400,
            hovermode='x unified'
        )
        
        # Add p-value annotation
        fig.add_annotation(
            x=1500, y=0.8,
            text='P < 0.001',
            showarrow=False,
            font=dict(size=14, color='green')
        )
        
        return fig
    
    def create_subtype_drivers(self):
        """Create subtype-specific driver events"""
        # Define driver events for each subtype
        driver_data = []
        
        subtypes = ['Metabolic', 'Proliferative', 'Immune', 'Mesenchymal', 'Mixed']
        
        # Metabolic drivers
        for gene in ['IDH1', 'IDH2', 'FH', 'SDH']:
            driver_data.append({'subtype': 'Metabolic', 'gene': gene, 'frequency': np.random.uniform(0.2, 0.4)})
        
        # Proliferative drivers
        for gene in ['MYC', 'CCND1', 'CDK4', 'RB1']:
            driver_data.append({'subtype': 'Proliferative', 'gene': gene, 'frequency': np.random.uniform(0.3, 0.5)})
        
        # Immune drivers
        for gene in ['B2M', 'HLA-A', 'JAK1', 'JAK2']:
            driver_data.append({'subtype': 'Immune', 'gene': gene, 'frequency': np.random.uniform(0.15, 0.35)})
        
        # Mesenchymal drivers
        for gene in ['ZEB1', 'SNAI1', 'TWIST1', 'VIM']:
            driver_data.append({'subtype': 'Mesenchymal', 'gene': gene, 'frequency': np.random.uniform(0.25, 0.45)})
        
        # Mixed drivers
        for gene in ['TP53', 'CTNNB1', 'AXIN1', 'ARID1A']:
            driver_data.append({'subtype': 'Mixed', 'gene': gene, 'frequency': np.random.uniform(0.2, 0.6)})
        
        df = pd.DataFrame(driver_data)
        
        fig = px.bar(
            df, x='gene', y='frequency',
            color='subtype',
            title='亚型特异性驱动基因',
            color_discrete_sequence=['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
        )
        
        fig.update_layout(
            xaxis_title='驱动基因',
            yaxis_title='突变频率',
            height=450,
            xaxis_tickangle=-45
        )
        
        return fig
    
    # Metabolism analysis visualization methods
    def create_metabolic_activity(self):
        """Create metabolic pathway activity heatmap"""
        # Define metabolic pathways
        pathways = [
            'Glycolysis', 'Oxidative Phosphorylation', 'Fatty Acid Oxidation',
            'Fatty Acid Synthesis', 'Glutaminolysis', 'One Carbon Metabolism',
            'Pentose Phosphate Pathway', 'TCA Cycle', 'Urea Cycle',
            'Amino Acid Metabolism', 'Nucleotide Metabolism', 'Cholesterol Metabolism'
        ]
        
        # Sample subset
        samples = self.clinical_data.index[:25]
        
        # Create activity matrix
        activity_matrix = np.random.randn(len(pathways), len(samples))
        
        # Add metabolic patterns
        activity_matrix[0, :10] += 2  # High glycolysis
        activity_matrix[1, 10:20] += 1.5  # High OXPHOS
        activity_matrix[4, 15:25] += 1.8  # High glutaminolysis
        
        fig = go.Figure(data=go.Heatmap(
            z=activity_matrix,
            x=samples,
            y=pathways,
            colorscale='RdBu',
            zmid=0,
            colorbar=dict(title='Pathway Activity')
        ))
        
        fig.update_layout(
            title='代谢通路活性热图',
            xaxis_title='样本',
            yaxis_title='代谢通路',
            height=500,
            xaxis=dict(tickangle=-45)
        )
        
        return fig
    
    def create_metabolic_dependencies(self):
        """Create metabolic dependencies visualization"""
        # Define metabolites and their dependencies
        metabolites = ['Glucose', 'Glutamine', 'Fatty Acids', 'Lactate', 'ATP', 'NADPH']
        
        dependency_data = []
        for metabolite in metabolites:
            dependency_data.append({
                'metabolite': metabolite,
                'dependency_score': np.random.uniform(0.3, 0.9),
                'essentiality': np.random.uniform(0.4, 1.0),
                'targetability': np.random.uniform(0.2, 0.8)
            })
        
        df = pd.DataFrame(dependency_data)
        
        fig = go.Figure()
        
        # Create radar chart
        categories = ['Dependency', 'Essentiality', 'Targetability']
        
        for idx, row in df.iterrows():
            values = [row['dependency_score'], row['essentiality'], row['targetability']]
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name=row['metabolite'],
                opacity=0.6
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            title='代谢依赖性分析',
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_metabolic_immune(self):
        """Create metabolic-immune crosstalk visualization"""
        # Define metabolic factors and immune effects
        metabolic_factors = ['Lactate', 'Adenosine', 'Kynurenine', 'PGE2', 'Arginine depletion']
        immune_effects = ['T cell suppression', 'Treg induction', 'M2 polarization', 
                         'DC dysfunction', 'NK inhibition']
        
        # Create interaction matrix
        interaction_matrix = np.random.uniform(0.2, 0.9, (len(metabolic_factors), len(immune_effects)))
        
        fig = go.Figure(data=go.Heatmap(
            z=interaction_matrix,
            x=immune_effects,
            y=metabolic_factors,
            colorscale='Reds',
            text=np.round(interaction_matrix, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title='Effect Strength')
        ))
        
        fig.update_layout(
            title='代谢-免疫相互作用',
            xaxis_title='免疫抑制效应',
            yaxis_title='代谢因子',
            height=400
        )
        
        return fig
    
    def create_metabolic_targets(self):
        """Create metabolic targeting opportunities"""
        # Define metabolic targets
        targets = [
            {'name': 'HK2', 'pathway': 'Glycolysis', 'druggability': 0.8, 'efficacy': 0.7},
            {'name': 'LDHA', 'pathway': 'Glycolysis', 'druggability': 0.9, 'efficacy': 0.65},
            {'name': 'GLS', 'pathway': 'Glutaminolysis', 'druggability': 0.85, 'efficacy': 0.75},
            {'name': 'FASN', 'pathway': 'Lipogenesis', 'druggability': 0.7, 'efficacy': 0.6},
            {'name': 'IDH1', 'pathway': 'TCA Cycle', 'druggability': 0.95, 'efficacy': 0.85},
            {'name': 'MTHFR', 'pathway': 'One Carbon', 'druggability': 0.6, 'efficacy': 0.5}
        ]
        
        df = pd.DataFrame(targets)
        
        fig = px.scatter(
            df, x='druggability', y='efficacy',
            size=[50]*len(df),
            color='pathway',
            text='name',
            title='代谢靶点药物开发潜力'
        )
        
        fig.update_traces(textposition='top center')
        
        fig.update_layout(
            xaxis_title='可成药性',
            yaxis_title='预期疗效',
            height=450,
            xaxis_range=[0.5, 1],
            yaxis_range=[0.4, 0.9]
        )
        
        # Add quadrants
        fig.add_hline(y=0.7, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=0.8, line_dash="dash", line_color="gray", opacity=0.5)
        
        return fig
    
    # Heterogeneity analysis visualization methods
    def create_clonal_structure(self):
        """Create clonal structure visualization"""
        # Create phylogenetic tree data
        import plotly.figure_factory as ff
        
        # Define clones and their relationships
        clones = ['Founding', 'Clone A', 'Clone B', 'Clone A1', 'Clone A2', 'Clone B1', 'Clone C']
        
        # Create hierarchy
        fig = go.Figure()
        
        # Define positions
        positions = {
            'Founding': (0, 0),
            'Clone A': (-2, -1),
            'Clone B': (2, -1),
            'Clone A1': (-3, -2),
            'Clone A2': (-1, -2),
            'Clone B1': (2, -2),
            'Clone C': (0, -2)
        }
        
        # Add edges
        edges = [
            ('Founding', 'Clone A'),
            ('Founding', 'Clone B'),
            ('Clone A', 'Clone A1'),
            ('Clone A', 'Clone A2'),
            ('Clone B', 'Clone B1'),
            ('Founding', 'Clone C')
        ]
        
        for parent, child in edges:
            x0, y0 = positions[parent]
            x1, y1 = positions[child]
            fig.add_trace(go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode='lines',
                line=dict(color='gray', width=2),
                showlegend=False
            ))
        
        # Add nodes
        for clone, (x, y) in positions.items():
            size = 40 if clone == 'Founding' else 30
            color = '#e74c3c' if clone == 'Founding' else '#3498db'
            
            fig.add_trace(go.Scatter(
                x=[x],
                y=[y],
                mode='markers+text',
                marker=dict(size=size, color=color),
                text=[clone],
                textposition='bottom center',
                showlegend=False
            ))
        
        fig.update_layout(
            title='肿瘤克隆进化树',
            height=500,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        return fig
    
    def create_evolution_trajectory(self):
        """Create tumor evolution trajectory"""
        # Simulate evolutionary time points
        time_points = ['Normal', 'Early', 'Intermediate', 'Advanced', 'Metastatic']
        
        # Track multiple features over time
        features = {
            'Mutation Burden': [0, 10, 50, 150, 300],
            'Chromosomal Instability': [0, 0.1, 0.3, 0.6, 0.8],
            'Immune Evasion': [0, 0.05, 0.2, 0.5, 0.9],
            'Metabolic Shift': [0, 0.15, 0.4, 0.7, 0.85]
        }
        
        fig = go.Figure()
        
        for feature, values in features.items():
            # Normalize values
            normalized = np.array(values) / max(values)
            fig.add_trace(go.Scatter(
                x=time_points,
                y=normalized,
                mode='lines+markers',
                name=feature,
                line=dict(width=3),
                marker=dict(size=10)
            ))
        
        fig.update_layout(
            title='肿瘤进化轨迹',
            xaxis_title='进化阶段',
            yaxis_title='标准化评分',
            height=400,
            yaxis_range=[0, 1]
        )
        
        return fig
    
    def create_spatial_heterogeneity(self):
        """Create spatial heterogeneity visualization"""
        # Simulate spatial regions
        regions = ['Center', 'Edge', 'Invasive Front', 'Necrotic Core', 'Perivascular']
        
        # Create heterogeneity metrics
        metrics = ['Genetic Diversity', 'Immune Infiltration', 'Hypoxia', 
                  'Proliferation', 'Drug Penetration']
        
        # Create data matrix
        spatial_matrix = np.random.randn(len(metrics), len(regions))
        
        # Add spatial patterns
        spatial_matrix[1, 2] = 2.5  # High immune at invasive front
        spatial_matrix[2, 3] = 3  # High hypoxia in necrotic core
        spatial_matrix[4, 0] = -2  # Low drug penetration in center
        
        fig = go.Figure(data=go.Heatmap(
            z=spatial_matrix,
            x=regions,
            y=metrics,
            colorscale='RdBu',
            zmid=0,
            colorbar=dict(title='Z-score')
        ))
        
        fig.update_layout(
            title='肿瘤空间异质性分析',
            xaxis_title='空间区域',
            yaxis_title='生物学特征',
            height=400
        )
        
        return fig
    
    def create_temporal_dynamics(self):
        """Create temporal dynamics visualization"""
        # Simulate longitudinal data
        time_points = ['Baseline', 'Week 4', 'Week 8', 'Week 12', 'Week 24']
        
        fig = go.Figure()
        
        # Track multiple clones over time
        clones = ['Clone A', 'Clone B', 'Clone C', 'Clone D']
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
        
        for clone, color in zip(clones, colors):
            # Simulate clone dynamics
            if clone == 'Clone A':
                frequencies = [0.4, 0.3, 0.2, 0.1, 0.05]  # Decreasing
            elif clone == 'Clone B':
                frequencies = [0.2, 0.3, 0.4, 0.5, 0.6]  # Increasing
            elif clone == 'Clone C':
                frequencies = [0.3, 0.25, 0.2, 0.25, 0.2]  # Stable
            else:
                frequencies = [0.1, 0.15, 0.2, 0.15, 0.15]  # Variable
            
            fig.add_trace(go.Scatter(
                x=time_points,
                y=frequencies,
                mode='lines+markers',
                name=clone,
                line=dict(color=color, width=3),
                marker=dict(size=10),
                stackgroup='one'
            ))
        
        fig.update_layout(
            title='克隆动态演化追踪',
            xaxis_title='治疗时间点',
            yaxis_title='克隆频率',
            height=450,
            yaxis_range=[0, 1],
            hovermode='x unified'
        )
        
        # Add treatment annotation
        fig.add_annotation(
            x='Week 8', y=0.9,
            text='Treatment Start',
            showarrow=True,
            arrowhead=2,
            arrowcolor='red'
        )
        
        return fig
    
    # Dynamic content creation methods using DataLoader
    def _create_dynamic_multidim_content(self, data: dict, dataset_info: dict):
        """Create dynamic multi-dimensional analysis content"""
        try:
            # Get top variable genes
            if 'expression' in data and not data['expression'].empty:
                top_genes = data_loader.get_top_genes(
                    dataset_info['id'], dataset_info, n=20
                )
                
                # Create gene variance plot
                fig_variance = go.Figure()
                fig_variance.add_trace(go.Bar(
                    x=top_genes['gene'],
                    y=top_genes['variance'],
                    marker_color='lightblue'
                ))
                fig_variance.update_layout(
                    title=f"Top Variable Genes - {dataset_info['name']}",
                    xaxis_title="Gene",
                    yaxis_title="Variance",
                    height=400
                )
                
                # Create expression heatmap
                expr_data = data['expression']
                top_gene_expr = expr_data.loc[top_genes['gene'][:10]]
                
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=top_gene_expr.values,
                    x=top_gene_expr.columns[:50],
                    y=top_gene_expr.index,
                    colorscale='RdBu'
                ))
                fig_heatmap.update_layout(
                    title=f"Gene Expression Heatmap - {dataset_info['name']}",
                    height=400
                )
                
                # Clinical summary if available
                clinical_summary = html.Div()
                if 'clinical' in data and not data['clinical'].empty:
                    clinical_df = data['clinical']
                    summary_stats = {
                        'Total Samples': len(clinical_df),
                        'Average Age': clinical_df['age'].mean() if 'age' in clinical_df else 'N/A',
                        'Gender Distribution': clinical_df['gender'].value_counts().to_dict() if 'gender' in clinical_df else 'N/A',
                        'Stage Distribution': clinical_df['stage'].value_counts().to_dict() if 'stage' in clinical_df else 'N/A'
                    }
                    
                    clinical_summary = html.Div([
                        html.H4("Clinical Data Summary"),
                        html.Ul([
                            html.Li(f"{key}: {value}")
                            for key, value in summary_stats.items()
                        ])
                    ])
                
                return html.Div([
                    html.H3(f"Multi-dimensional Analysis - {dataset_info['name']}"),
                    html.Hr(),
                    clinical_summary,
                    html.Div([
                        dcc.Graph(figure=fig_variance)
                    ], style={'marginBottom': '20px'}),
                    html.Div([
                        dcc.Graph(figure=fig_heatmap)
                    ])
                ])
            else:
                return html.Div([
                    html.H3("No Expression Data Available"),
                    html.P(f"The dataset '{dataset_info['name']}' does not contain expression data.")
                ])
                
        except Exception as e:
            return html.Div([
                html.H3("Error Loading Data"),
                html.P(f"Error: {str(e)}")
            ])
    
    def _create_dynamic_survival_content(self, data: dict, dataset_info: dict):
        """Create dynamic survival analysis content"""
        try:
            clinical_df, expression_df = data_loader.get_survival_data(
                dataset_info['id'], dataset_info
            )
            
            if clinical_df.empty:
                return html.Div([
                    html.H3("No Survival Data Available"),
                    html.P(f"The dataset '{dataset_info['name']}' does not contain survival data.")
                ])
            
            # Create Kaplan-Meier curve
            from lifelines import KaplanMeierFitter
            kmf = KaplanMeierFitter()
            
            fig = go.Figure()
            
            # Overall survival
            if 'os_time' in clinical_df and 'os_status' in clinical_df:
                kmf.fit(clinical_df['os_time'], clinical_df['os_status'])
                
                fig.add_trace(go.Scatter(
                    x=kmf.survival_function_.index,
                    y=kmf.survival_function_.iloc[:, 0],
                    mode='lines',
                    name='Overall Survival',
                    line=dict(width=3)
                ))
            
            # Stratified by stage if available
            if 'stage' in clinical_df:
                stages = clinical_df['stage'].unique()
                colors = px.colors.qualitative.Set1
                
                for i, stage in enumerate(stages):
                    stage_data = clinical_df[clinical_df['stage'] == stage]
                    if len(stage_data) > 5:  # Minimum samples
                        kmf.fit(stage_data['os_time'], stage_data['os_status'])
                        fig.add_trace(go.Scatter(
                            x=kmf.survival_function_.index,
                            y=kmf.survival_function_.iloc[:, 0],
                            mode='lines',
                            name=f'Stage {stage}',
                            line=dict(color=colors[i % len(colors)], width=2)
                        ))
            
            fig.update_layout(
                title=f"Survival Analysis - {dataset_info['name']}",
                xaxis_title="Time (days)",
                yaxis_title="Survival Probability",
                height=500
            )
            
            # Summary statistics
            median_survival = clinical_df['os_time'].median()
            event_rate = clinical_df['os_status'].mean() * 100
            
            return html.Div([
                html.H3(f"Survival Analysis - {dataset_info['name']}"),
                html.Hr(),
                html.Div([
                    html.H4("Summary Statistics"),
                    html.Ul([
                        html.Li(f"Total Patients: {len(clinical_df)}"),
                        html.Li(f"Median Follow-up: {median_survival:.0f} days"),
                        html.Li(f"Event Rate: {event_rate:.1f}%")
                    ])
                ]),
                dcc.Graph(figure=fig)
            ])
            
        except Exception as e:
            return html.Div([
                html.H3("Error in Survival Analysis"),
                html.P(f"Error: {str(e)}")
            ])
    
    def _create_dynamic_network_content(self, data: dict, dataset_info: dict):
        """Create dynamic network analysis content"""
        try:
            if 'expression' not in data or data['expression'].empty:
                return html.Div([
                    html.H3("No Expression Data for Network Analysis"),
                    html.P(f"The dataset '{dataset_info['name']}' does not contain expression data.")
                ])
            
            # Get top genes for network
            top_genes = data_loader.get_top_genes(
                dataset_info['id'], dataset_info, n=30
            )
            
            expr_subset = data['expression'].loc[top_genes['gene']]
            
            # Calculate correlation matrix
            corr_matrix = expr_subset.T.corr()
            
            # Create correlation heatmap
            fig_corr = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.index,
                colorscale='RdBu',
                zmid=0
            ))
            fig_corr.update_layout(
                title=f"Gene Correlation Network - {dataset_info['name']}",
                height=600
            )
            
            # Network statistics
            high_corr_pairs = (corr_matrix.abs() > 0.7).sum().sum() / 2
            avg_corr = corr_matrix.abs().mean().mean()
            
            return html.Div([
                html.H3(f"Network Analysis - {dataset_info['name']}"),
                html.Hr(),
                html.Div([
                    html.H4("Network Statistics"),
                    html.Ul([
                        html.Li(f"Nodes (Genes): {len(top_genes)}"),
                        html.Li(f"High Correlation Pairs (|r| > 0.7): {int(high_corr_pairs)}"),
                        html.Li(f"Average Absolute Correlation: {avg_corr:.3f}")
                    ])
                ]),
                dcc.Graph(figure=fig_corr)
            ])
            
        except Exception as e:
            return html.Div([
                html.H3("Error in Network Analysis"),
                html.P(f"Error: {str(e)}")
            ])
    
    def _create_dynamic_linchpin_content(self, data: dict, dataset_info: dict):
        """Create dynamic linchpin analysis content"""
        try:
            if 'expression' not in data or data['expression'].empty:
                return html.Div([
                    html.H3("No Data for Linchpin Analysis"),
                    html.P(f"The dataset '{dataset_info['name']}' does not contain required data.")
                ])
            
            # Identify hub genes based on connectivity
            expr_data = data['expression']
            top_genes = data_loader.get_top_genes(
                dataset_info['id'], dataset_info, n=50
            )
            
            # Calculate gene connectivity
            gene_corr = expr_data.loc[top_genes['gene']].T.corr()
            connectivity = gene_corr.abs().sum(axis=1) - 1  # Subtract self-correlation
            
            # Get top hub genes
            hub_genes = connectivity.nlargest(20)
            
            # Create hub gene plot
            fig_hubs = go.Figure()
            fig_hubs.add_trace(go.Bar(
                x=hub_genes.index,
                y=hub_genes.values,
                marker_color='orange'
            ))
            fig_hubs.update_layout(
                title=f"Linchpin Genes by Connectivity - {dataset_info['name']}",
                xaxis_title="Gene",
                yaxis_title="Total Connectivity",
                height=400
            )
            
            # Clinical association if available
            clinical_associations = []
            if 'clinical' in data and 'os_status' in data['clinical']:
                for gene in hub_genes.index[:5]:
                    gene_expr = expr_data.loc[gene]
                    high_expr = gene_expr > gene_expr.median()
                    
                    # Simple survival difference
                    high_group_events = data['clinical'].loc[high_expr, 'os_status'].mean()
                    low_group_events = data['clinical'].loc[~high_expr, 'os_status'].mean()
                    
                    hazard_ratio = high_group_events / (low_group_events + 0.01)
                    
                    clinical_associations.append({
                        'Gene': gene,
                        'Hazard Ratio': f"{hazard_ratio:.2f}",
                        'Risk': 'High' if hazard_ratio > 1 else 'Low'
                    })
            
            clinical_table = html.Div()
            if clinical_associations:
                clinical_table = html.Div([
                    html.H4("Clinical Associations"),
                    html.Table([
                        html.Thead([
                            html.Tr([html.Th(col) for col in ['Gene', 'Hazard Ratio', 'Risk']])
                        ]),
                        html.Tbody([
                            html.Tr([
                                html.Td(assoc[col]) for col in ['Gene', 'Hazard Ratio', 'Risk']
                            ]) for assoc in clinical_associations
                        ])
                    ], className="table table-striped")
                ])
            
            return html.Div([
                html.H3(f"Linchpin Gene Analysis - {dataset_info['name']}"),
                html.Hr(),
                dcc.Graph(figure=fig_hubs),
                clinical_table
            ])
            
        except Exception as e:
            return html.Div([
                html.H3("Error in Linchpin Analysis"),
                html.P(f"Error: {str(e)}")
            ])
    
    def _create_dynamic_multiomics_content(self, data: dict, dataset_info: dict):
        """Create dynamic multi-omics integration content"""
        try:
            available_omics = []
            if 'expression' in data and not data['expression'].empty:
                available_omics.append('Expression')
            if 'mutations' in data and not data['mutations'].empty:
                available_omics.append('Mutations')
            if 'cnv' in data and not data.get('cnv', pd.DataFrame()).empty:
                available_omics.append('CNV')
            if 'methylation' in data and not data.get('methylation', pd.DataFrame()).empty:
                available_omics.append('Methylation')
            
            if len(available_omics) < 2:
                return html.Div([
                    html.H3("Insufficient Data for Multi-omics Analysis"),
                    html.P(f"The dataset '{dataset_info['name']}' contains only: {', '.join(available_omics)}")
                ])
            
            # Create integration visualization
            fig = go.Figure()
            
            # Example: Expression vs Mutation burden
            if 'expression' in data and 'mutations' in data:
                mutation_counts = data['mutations'].groupby('sample_id').size()
                common_samples = list(set(data['expression'].columns) & set(mutation_counts.index))
                
                if common_samples:
                    # Get a marker gene expression
                    marker_gene = data['expression'].index[0]
                    expr_values = data['expression'].loc[marker_gene, common_samples]
                    mut_values = mutation_counts[common_samples]
                    
                    fig.add_trace(go.Scatter(
                        x=expr_values,
                        y=mut_values,
                        mode='markers',
                        marker=dict(size=8, color='blue', opacity=0.6),
                        text=common_samples,
                        name='Samples'
                    ))
                    
                    fig.update_layout(
                        title=f"Multi-omics Integration - {dataset_info['name']}",
                        xaxis_title=f"{marker_gene} Expression",
                        yaxis_title="Mutation Count",
                        height=400
                    )
            
            return html.Div([
                html.H3(f"Multi-omics Integration - {dataset_info['name']}"),
                html.Hr(),
                html.Div([
                    html.H4("Available Data Types"),
                    html.Ul([html.Li(omics) for omics in available_omics])
                ]),
                dcc.Graph(figure=fig) if not fig.data == () else html.P("Unable to create integration plot")
            ])
            
        except Exception as e:
            return html.Div([
                html.H3("Error in Multi-omics Analysis"),
                html.P(f"Error: {str(e)}")
            ])
    
    def _create_dynamic_immune_content(self, data: dict, dataset_info: dict):
        """Create dynamic immune analysis content"""
        try:
            if 'expression' not in data or data['expression'].empty:
                return html.Div([
                    html.H3("No Expression Data for Immune Analysis"),
                    html.P(f"The dataset '{dataset_info['name']}' does not contain expression data.")
                ])
            
            # Define immune marker genes
            immune_markers = {
                'T cells': ['CD3D', 'CD3E', 'CD4', 'CD8A', 'CD8B'],
                'B cells': ['CD19', 'CD79A', 'MS4A1'],
                'NK cells': ['NCAM1', 'NKG7', 'GNLY'],
                'Macrophages': ['CD68', 'CD163', 'MSR1'],
                'Dendritic': ['ITGAX', 'CD1C', 'BATF3']
            }
            
            # Calculate immune scores
            immune_scores = {}
            expr_data = data['expression']
            
            for cell_type, markers in immune_markers.items():
                available_markers = [m for m in markers if m in expr_data.index]
                if available_markers:
                    scores = expr_data.loc[available_markers].mean(axis=0)
                else:
                    # Use proxy genes if markers not found
                    scores = expr_data.iloc[:len(markers)].mean(axis=0)
                immune_scores[cell_type] = scores
            
            # Create immune landscape heatmap
            immune_df = pd.DataFrame(immune_scores)
            
            fig_immune = go.Figure(data=go.Heatmap(
                z=immune_df.T.values,
                x=immune_df.index[:30],  # Show first 30 samples
                y=immune_df.columns,
                colorscale='Viridis'
            ))
            fig_immune.update_layout(
                title=f"Immune Cell Infiltration - {dataset_info['name']}",
                xaxis_title="Samples",
                yaxis_title="Cell Types",
                height=400
            )
            
            # Calculate immune subtypes
            from sklearn.preprocessing import StandardScaler
            from sklearn.cluster import KMeans
            
            scaler = StandardScaler()
            immune_scaled = scaler.fit_transform(immune_df.T)
            
            kmeans = KMeans(n_clusters=3, random_state=42)
            immune_subtypes = kmeans.fit_predict(immune_scaled)
            
            subtype_counts = pd.Series(immune_subtypes).value_counts()
            
            fig_subtypes = go.Figure(data=[
                go.Pie(
                    labels=[f'Immune Subtype {i+1}' for i in subtype_counts.index],
                    values=subtype_counts.values
                )
            ])
            fig_subtypes.update_layout(
                title="Immune Subtype Distribution"
            )
            
            return html.Div([
                html.H3(f"Immune Microenvironment Analysis - {dataset_info['name']}"),
                html.Hr(),
                html.Div([
                    html.H4("Immune Cell Infiltration"),
                    dcc.Graph(figure=fig_immune)
                ]),
                html.Div([
                    html.H4("Immune Subtypes"),
                    dcc.Graph(figure=fig_subtypes)
                ])
            ])
            
        except Exception as e:
            return html.Div([
                html.H3("Error in Immune Analysis"),
                html.P(f"Error: {str(e)}")
            ])
    
    def _create_dynamic_drug_content(self, data: dict, dataset_info: dict):
        """Create dynamic drug response analysis content"""
        try:
            if 'expression' not in data or data['expression'].empty:
                return html.Div([
                    html.H3("No Expression Data for Drug Analysis"),
                    html.P(f"The dataset '{dataset_info['name']}' does not contain expression data.")
                ])
            
            # Define drug target genes
            drug_targets = {
                'Sorafenib': ['RAF1', 'BRAF', 'VEGFR2', 'PDGFRB'],
                'Lenvatinib': ['VEGFR1', 'VEGFR2', 'VEGFR3', 'FGFR1'],
                'Regorafenib': ['VEGFR1', 'TIE2', 'PDGFRB', 'FGFR1'],
                'Cabozantinib': ['MET', 'VEGFR2', 'RET', 'AXL']
            }
            
            expr_data = data['expression']
            
            # Calculate drug sensitivity scores
            drug_scores = {}
            for drug, targets in drug_targets.items():
                available_targets = [t for t in targets if t in expr_data.index]
                if available_targets:
                    # Higher expression of targets = potentially more sensitive
                    scores = expr_data.loc[available_targets].mean(axis=0)
                    drug_scores[drug] = (scores - scores.mean()) / scores.std()
                else:
                    # Use random genes as proxy
                    proxy_genes = expr_data.index[:len(targets)]
                    scores = expr_data.loc[proxy_genes].mean(axis=0)
                    drug_scores[drug] = (scores - scores.mean()) / scores.std()
            
            drug_df = pd.DataFrame(drug_scores)
            
            # Create drug sensitivity heatmap
            fig_drugs = go.Figure(data=go.Heatmap(
                z=drug_df.T.values,
                x=drug_df.index[:20],  # Show first 20 samples
                y=drug_df.columns,
                colorscale='RdYlGn_r',
                zmid=0
            ))
            fig_drugs.update_layout(
                title=f"Predicted Drug Sensitivity - {dataset_info['name']}",
                xaxis_title="Samples",
                yaxis_title="Drugs",
                height=400
            )
            
            # Resistance mechanisms
            resistance_genes = ['ABCB1', 'ABCC1', 'ABCG2', 'CYP3A4']
            available_resistance = [g for g in resistance_genes if g in expr_data.index]
            
            if available_resistance:
                resistance_expr = expr_data.loc[available_resistance]
                
                fig_resistance = go.Figure()
                for gene in available_resistance:
                    fig_resistance.add_trace(go.Box(
                        y=resistance_expr.loc[gene],
                        name=gene
                    ))
                
                fig_resistance.update_layout(
                    title="Drug Resistance Gene Expression",
                    yaxis_title="Expression Level",
                    height=300
                )
            else:
                fig_resistance = None
            
            return html.Div([
                html.H3(f"Drug Response Analysis - {dataset_info['name']}"),
                html.Hr(),
                html.Div([
                    html.H4("Predicted Drug Sensitivity"),
                    dcc.Graph(figure=fig_drugs)
                ]),
                html.Div([
                    html.H4("Resistance Mechanisms"),
                    dcc.Graph(figure=fig_resistance)
                ]) if fig_resistance else html.Div()
            ])
            
        except Exception as e:
            return html.Div([
                html.H3("Error in Drug Analysis"),
                html.P(f"Error: {str(e)}")
            ])
    
    def _create_dynamic_subtype_content(self, data: dict, dataset_info: dict):
        """Create dynamic molecular subtype analysis content"""
        try:
            if 'expression' not in data or data['expression'].empty:
                return html.Div([
                    html.H3("No Expression Data for Subtype Analysis"),
                    html.P(f"The dataset '{dataset_info['name']}' does not contain expression data.")
                ])
            
            # Perform hierarchical clustering for subtyping
            from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
            from sklearn.preprocessing import StandardScaler
            
            # Get top variable genes
            top_genes = data_loader.get_top_genes(
                dataset_info['id'], dataset_info, n=100
            )
            
            expr_subset = data['expression'].loc[top_genes['gene']]
            
            # Standardize data
            scaler = StandardScaler()
            expr_scaled = scaler.fit_transform(expr_subset.T)
            
            # Perform clustering
            linkage_matrix = linkage(expr_scaled, method='ward')
            clusters = fcluster(linkage_matrix, t=5, criterion='maxclust')
            
            # Create dendrogram
            fig_dendro = go.Figure()
            dendro = dendrogram(linkage_matrix, no_plot=True)
            
            for i in range(len(dendro['dcoord'])):
                fig_dendro.add_trace(go.Scatter(
                    x=dendro['icoord'][i],
                    y=dendro['dcoord'][i],
                    mode='lines',
                    line=dict(color='black', width=1),
                    showlegend=False
                ))
            
            fig_dendro.update_layout(
                title=f"Hierarchical Clustering Dendrogram - {dataset_info['name']}",
                xaxis_title="Sample Index",
                yaxis_title="Distance",
                height=400
            )
            
            # Subtype distribution
            subtype_counts = pd.Series(clusters).value_counts()
            
            fig_dist = go.Figure(data=[
                go.Bar(
                    x=[f'Subtype {i}' for i in subtype_counts.index],
                    y=subtype_counts.values,
                    marker_color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6'][:len(subtype_counts)]
                )
            ])
            fig_dist.update_layout(
                title="Molecular Subtype Distribution",
                xaxis_title="Subtype",
                yaxis_title="Number of Samples",
                height=300
            )
            
            return html.Div([
                html.H3(f"Molecular Subtype Analysis - {dataset_info['name']}"),
                html.Hr(),
                html.Div([
                    html.H4("Hierarchical Clustering"),
                    dcc.Graph(figure=fig_dendro)
                ]),
                html.Div([
                    html.H4("Subtype Distribution"),
                    dcc.Graph(figure=fig_dist)
                ]),
                html.Div([
                    html.P(f"Identified {len(subtype_counts)} molecular subtypes using hierarchical clustering on top {len(top_genes)} variable genes.")
                ])
            ])
            
        except Exception as e:
            return html.Div([
                html.H3("Error in Subtype Analysis"),
                html.P(f"Error: {str(e)}")
            ])
    
    def _create_default_dataset_content(self, dataset_info: dict):
        """Create default content for dataset switch"""
        return html.Div([
            html.Div([
                html.I(className="fas fa-check-circle", style={'color': 'green', 'marginRight': '10px'}),
                html.Span(f"已切换到数据集: {dataset_info['name']}", style={'fontWeight': 'bold'})
            ], style={'backgroundColor': '#d4edda', 'padding': '10px', 'borderRadius': '5px', 
                     'marginBottom': '20px'}),
            
            html.H4("数据集信息"),
            html.Ul([
                html.Li(f"类型: {dataset_info['type']}"),
                html.Li(f"创建时间: {dataset_info.get('created', 'N/A')}"),
                html.Li(f"样本数: {dataset_info['features']['samples']}"),
                html.Li(f"基因数: {dataset_info['features']['genes']}"),
            ]),
            
            html.Hr(),
            
            html.P("分析功能将基于此数据集运行。请点击相应的分析按钮开始分析。"),
            
            html.Button([
                html.I(className="fas fa-play"),
                " 运行分析"
            ], className="btn btn-primary", id="run-analysis-from-dataset")
        ])
    
    def run(self, debug=True, port=8050):
        """Run the dashboard"""
        self.app.run(debug=debug, port=port, host='0.0.0.0')
    
    # Dynamic content creation methods
    def _create_dynamic_multidim_content(self, data, dataset_info):
        """Create dynamic multidimensional analysis content"""
        content = []
        
        # Dataset overview
        stats = data_loader.get_summary_statistics(dataset_info['id'], dataset_info)
        content.append(html.Div([
            html.H4("数据集概览"),
            html.Div([
                html.Div([
                    html.H3(stats['samples'], className="text-primary"),
                    html.P("样本数")
                ], className="col-md-3 text-center"),
                html.Div([
                    html.H3(stats['genes'], className="text-success"),
                    html.P("基因数")
                ], className="col-md-3 text-center"),
                html.Div([
                    html.H3(stats['mutations'], className="text-warning"),
                    html.P("突变数")
                ], className="col-md-3 text-center"),
                html.Div([
                    html.H3(f"{stats['survival_rate']:.1%}", className="text-info"),
                    html.P("生存率")
                ], className="col-md-3 text-center"),
            ], className="row", style={'marginBottom': '20px'})
        ]))
        
        # Top variable genes
        if 'expression' in data and not data['expression'].empty:
            top_genes = data_loader.get_top_genes(dataset_info['id'], dataset_info, 20)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=top_genes['gene'],
                y=top_genes['variance'],
                marker_color='lightblue'
            ))
            fig.update_layout(
                title='Top 20 高变异基因',
                xaxis_title='基因',
                yaxis_title='方差',
                height=400
            )
            
            content.append(html.Div([
                html.H4("基因变异分析"),
                dcc.Graph(figure=fig)
            ], style={'marginTop': '20px'}))
        
        return html.Div(content)
    
    def _create_dynamic_survival_content(self, data, dataset_info):
        """Create dynamic survival analysis content"""
        clinical, expression = data_loader.get_survival_data(dataset_info['id'], dataset_info)
        
        if clinical.empty:
            return html.Div([
                html.P("该数据集没有生存数据", className="text-warning")
            ])
        
        content = []
        
        # Kaplan-Meier curve by stage
        if 'stage' in clinical.columns:
            from lifelines import KaplanMeierFitter
            
            fig = go.Figure()
            stages = clinical['stage'].unique()
            colors = px.colors.qualitative.Set1
            
            for i, stage in enumerate(stages):
                mask = clinical['stage'] == stage
                stage_data = clinical[mask]
                
                kmf = KaplanMeierFitter()
                kmf.fit(stage_data['os_time'], stage_data['os_status'])
                
                fig.add_trace(go.Scatter(
                    x=kmf.survival_function_.index,
                    y=kmf.survival_function_.iloc[:, 0],
                    mode='lines',
                    name=f'Stage {stage}',
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
            
            fig.update_layout(
                title='分期生存曲线 (Kaplan-Meier)',
                xaxis_title='时间 (天)',
                yaxis_title='生存概率',
                height=500
            )
            
            content.append(dcc.Graph(figure=fig))
        
        # Survival statistics
        from lifelines.statistics import logrank_test
        
        if 'stage' in clinical.columns and len(clinical['stage'].unique()) > 1:
            # Compare early vs late stage
            early_stages = ['I', 'II']
            late_stages = ['III', 'IV']
            
            early_mask = clinical['stage'].isin(early_stages)
            late_mask = clinical['stage'].isin(late_stages)
            
            if early_mask.any() and late_mask.any():
                results = logrank_test(
                    clinical[early_mask]['os_time'],
                    clinical[late_mask]['os_time'],
                    clinical[early_mask]['os_status'],
                    clinical[late_mask]['os_status']
                )
                
                content.append(html.Div([
                    html.H4("生存分析统计"),
                    html.P(f"早期 vs 晚期 Log-rank检验: p值 = {results.p_value:.4f}"),
                    html.P("结论: " + ("存在显著差异" if results.p_value < 0.05 else "无显著差异"))
                ], style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': '#f8f9fa'}))
        
        return html.Div(content)
    
    def _create_dynamic_network_content(self, data, dataset_info):
        """Create dynamic network analysis content"""
        if 'expression' not in data or data['expression'].empty:
            return html.Div([
                html.P("该数据集没有表达数据", className="text-warning")
            ])
        
        # Gene correlation network
        top_genes = data_loader.get_top_genes(dataset_info['id'], dataset_info, 30)
        expr_subset = data['expression'].loc[top_genes['gene']]
        
        # Calculate correlation
        corr_matrix = expr_subset.T.corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix, 2),
            texttemplate='%{text}',
            textfont={"size": 8}
        ))
        
        fig.update_layout(
            title='基因相关性网络 (Top 30基因)',
            height=600,
            width=700
        )
        
        content = [
            html.H4("基因网络分析"),
            dcc.Graph(figure=fig),
            
            html.Div([
                html.H5("网络统计"),
                html.P(f"节点数: {len(corr_matrix)}"),
                html.P(f"强相关边数 (|r| > 0.7): {int((np.abs(corr_matrix) > 0.7).sum().sum() / 2)}"),
                html.P(f"平均相关系数: {np.abs(corr_matrix).mean().mean():.3f}")
            ], style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': '#f8f9fa'})
        ]
        
        return html.Div(content)
    
    def _create_dynamic_linchpin_content(self, data, dataset_info):
        """Create dynamic linchpin analysis content"""
        if 'expression' not in data or data['expression'].empty:
            return html.Div([
                html.P("该数据集没有表达数据", className="text-warning")
            ])
        
        # Calculate linchpin scores based on variance and connectivity
        top_genes = data_loader.get_top_genes(dataset_info['id'], dataset_info, 50)
        expr_subset = data['expression'].loc[top_genes['gene']]
        
        # Calculate connectivity (average absolute correlation)
        corr_matrix = expr_subset.T.corr()
        connectivity = np.abs(corr_matrix).mean(axis=0)
        
        # Combine variance and connectivity for linchpin score
        linchpin_scores = pd.DataFrame({
            'gene': top_genes['gene'],
            'variance': top_genes['variance'],
            'connectivity': connectivity.values,
            'linchpin_score': top_genes['variance'] * connectivity.values
        })
        
        linchpin_scores = linchpin_scores.nlargest(20, 'linchpin_score')
        
        # Create bar plot
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=linchpin_scores['gene'],
            y=linchpin_scores['linchpin_score'],
            marker_color='coral',
            text=np.round(linchpin_scores['linchpin_score'], 2),
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Linchpin基因候选 (基于方差和连接度)',
            xaxis_title='基因',
            yaxis_title='Linchpin评分',
            height=500
        )
        
        content = [
            html.H4("Linchpin基因识别"),
            dcc.Graph(figure=fig),
            
            html.Div([
                html.H5("Top 5 Linchpin基因"),
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("基因"),
                            html.Th("方差"),
                            html.Th("连接度"),
                            html.Th("Linchpin评分")
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(row['gene']),
                            html.Td(f"{row['variance']:.2f}"),
                            html.Td(f"{row['connectivity']:.3f}"),
                            html.Td(f"{row['linchpin_score']:.2f}")
                        ]) for _, row in linchpin_scores.head(5).iterrows()
                    ])
                ], className="table table-striped", style={'marginTop': '15px'})
            ])
        ]
        
        return html.Div(content)
    
    def _create_dynamic_multiomics_content(self, data, dataset_info):
        """Create dynamic multi-omics integration content"""
        available_omics = []
        if 'expression' in data and not data['expression'].empty:
            available_omics.append('Expression')
        if 'mutations' in data and not data['mutations'].empty:
            available_omics.append('Mutations')
        if 'clinical' in data and not data['clinical'].empty:
            available_omics.append('Clinical')
        
        if len(available_omics) < 2:
            return html.Div([
                html.P("需要至少两种组学数据进行整合分析", className="text-warning")
            ])
        
        content = [
            html.H4("多组学数据整合"),
            html.P(f"可用数据类型: {', '.join(available_omics)}"),
        ]
        
        # Create integration visualization
        if 'expression' in data and 'mutations' in data:
            # Find genes with both expression and mutation data
            expr_genes = set(data['expression'].index)
            mut_genes = set(data['mutations']['gene'].unique()) if 'gene' in data['mutations'].columns else set()
            
            common_genes = list(expr_genes.intersection(mut_genes))[:20]
            
            if common_genes:
                # Calculate mutation frequency
                mut_freq = data['mutations']['gene'].value_counts()
                
                # Get expression variance
                expr_var = data['expression'].loc[common_genes].var(axis=1)
                
                # Create scatter plot
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=[mut_freq.get(g, 0) for g in common_genes],
                    y=expr_var.values,
                    mode='markers+text',
                    text=common_genes,
                    textposition='top center',
                    marker=dict(size=10, color='blue')
                ))
                
                fig.update_layout(
                    title='表达变异 vs 突变频率',
                    xaxis_title='突变频率',
                    yaxis_title='表达方差',
                    height=500
                )
                
                content.append(dcc.Graph(figure=fig))
        
        return html.Div(content)
    
    def _create_dynamic_immune_content(self, data, dataset_info):
        """Create dynamic immune microenvironment content"""
        if 'expression' not in data or data['expression'].empty:
            return html.Div([
                html.P("该数据集没有表达数据", className="text-warning")
            ])
        
        # Define immune cell markers
        immune_markers = {
            'T cells': ['CD3D', 'CD3E', 'CD3G'],
            'CD8+ T cells': ['CD8A', 'CD8B'],
            'CD4+ T cells': ['CD4'],
            'B cells': ['CD19', 'CD79A', 'MS4A1'],
            'NK cells': ['NCAM1', 'KLRB1'],
            'Macrophages': ['CD68', 'CD163', 'CSF1R'],
            'Dendritic cells': ['ITGAX', 'CD1C', 'BATF3']
        }
        
        # Calculate immune scores
        immune_scores = {}
        expr_genes = set(data['expression'].index)
        
        for cell_type, markers in immune_markers.items():
            available_markers = [m for m in markers if m in expr_genes]
            if available_markers:
                score = data['expression'].loc[available_markers].mean(axis=0).mean()
                immune_scores[cell_type] = score
        
        if not immune_scores:
            # Use surrogate markers
            top_genes = data['expression'].iloc[:50]
            for i, cell_type in enumerate(['T cells', 'B cells', 'NK cells', 'Macrophages']):
                immune_scores[cell_type] = top_genes.iloc[i*10:(i+1)*10].mean(axis=0).mean()
        
        # Create bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(immune_scores.keys()),
            y=list(immune_scores.values()),
            marker_color='lightgreen'
        ))
        
        fig.update_layout(
            title='免疫细胞浸润评分',
            xaxis_title='细胞类型',
            yaxis_title='浸润评分',
            height=400
        )
        
        content = [
            html.H4("免疫微环境分析"),
            dcc.Graph(figure=fig),
            
            html.Div([
                html.H5("免疫状态评估"),
                html.P(f"最高浸润: {max(immune_scores, key=immune_scores.get)}"),
                html.P(f"平均免疫评分: {np.mean(list(immune_scores.values())):.3f}")
            ], style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': '#f8f9fa'})
        ]
        
        return html.Div(content)
    
    def _create_dynamic_drug_content(self, data, dataset_info):
        """Create dynamic drug response content"""
        if 'expression' not in data or data['expression'].empty:
            return html.Div([
                html.P("该数据集没有表达数据", className="text-warning")
            ])
        
        # Drug target genes
        drug_targets = {
            'Sorafenib': ['RAF1', 'BRAF', 'KIT', 'FLT3', 'VEGFR2'],
            'Lenvatinib': ['VEGFR1', 'VEGFR2', 'VEGFR3', 'FGFR1', 'PDGFRA'],
            'Regorafenib': ['VEGFR1', 'VEGFR2', 'VEGFR3', 'TIE2', 'KIT'],
            'Cabozantinib': ['MET', 'VEGFR2', 'RET', 'KIT', 'AXL']
        }
        
        # Calculate drug sensitivity scores
        drug_scores = {}
        expr_genes = set(data['expression'].index)
        
        for drug, targets in drug_targets.items():
            available_targets = [t for t in targets if t in expr_genes]
            if available_targets:
                # High expression of targets suggests sensitivity
                score = data['expression'].loc[available_targets].mean(axis=0).mean()
                drug_scores[drug] = score
            else:
                # Use random genes as proxy
                drug_scores[drug] = data['expression'].iloc[:5].mean(axis=0).mean()
        
        # Create radar chart
        categories = list(drug_scores.keys())
        values = list(drug_scores.values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='药物敏感性'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) * 1.2]
                )),
            showlegend=False,
            title="预测药物敏感性",
            height=500
        )
        
        content = [
            html.H4("药物响应预测"),
            dcc.Graph(figure=fig),
            
            html.Div([
                html.H5("推荐药物"),
                html.P(f"最高敏感性: {max(drug_scores, key=drug_scores.get)}"),
                html.P(f"平均敏感性评分: {np.mean(list(drug_scores.values())):.3f}")
            ], style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': '#f8f9fa'})
        ]
        
        return html.Div(content)
    
    def _create_dynamic_subtype_content(self, data, dataset_info):
        """Create dynamic molecular subtype content"""
        if 'expression' not in data or data['expression'].empty:
            return html.Div([
                html.P("该数据集没有表达数据", className="text-warning")
            ])
        
        # Perform hierarchical clustering
        from scipy.cluster.hierarchy import dendrogram, linkage
        from sklearn.preprocessing import StandardScaler
        
        # Use top variable genes
        top_genes = data_loader.get_top_genes(dataset_info['id'], dataset_info, 50)
        expr_subset = data['expression'].loc[top_genes['gene']]
        
        # Standardize data
        scaler = StandardScaler()
        expr_scaled = scaler.fit_transform(expr_subset.T)
        
        # Perform clustering
        linkage_matrix = linkage(expr_scaled, method='ward')
        
        # Create dendrogram
        fig = go.Figure()
        dendro = dendrogram(linkage_matrix, no_plot=True)
        
        for i in range(len(dendro['icoord'])):
            fig.add_trace(go.Scatter(
                x=dendro['icoord'][i],
                y=dendro['dcoord'][i],
                mode='lines',
                line=dict(color='black', width=1),
                showlegend=False
            ))
        
        fig.update_layout(
            title='分子亚型聚类树状图',
            xaxis_title='样本索引',
            yaxis_title='距离',
            height=500
        )
        
        content = [
            html.H4("分子亚型分析"),
            dcc.Graph(figure=fig),
            
            html.Div([
                html.H5("聚类统计"),
                html.P(f"样本数: {expr_scaled.shape[0]}"),
                html.P(f"特征基因数: {expr_scaled.shape[1]}"),
                html.P("聚类方法: Ward层次聚类")
            ], style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': '#f8f9fa'})
        ]
        
        return html.Div(content)
    
    def _create_default_dataset_content(self, dataset_info):
        """Create default content when switching datasets"""
        return html.Div([
            html.Div([
                html.I(className="fas fa-check-circle", style={'color': 'green', 'marginRight': '10px'}),
                html.Span(f"已切换到数据集: {dataset_info['name']}", style={'fontWeight': 'bold'})
            ], style={'backgroundColor': '#d4edda', 'padding': '10px', 'borderRadius': '5px', 
                     'marginBottom': '20px'}),
            
            html.H4("数据集信息"),
            html.Ul([
                html.Li(f"类型: {dataset_info['type']}"),
                html.Li(f"创建时间: {dataset_info.get('created', 'N/A')}"),
                html.Li(f"样本数: {dataset_info['features']['samples']}"),
                html.Li(f"基因数: {dataset_info['features']['genes']}"),
            ]),
            
            html.Hr(),
            
            html.P("分析功能将基于此数据集运行。内容正在加载中..."),
        ])
    
    def setup_batch_callbacks(self):
        """Setup callbacks for batch processing"""
        # Start batch analysis callback
        @self.app.callback(
            [Output('batch-job-status', 'children'),
             Output('current-batch-job-id', 'data'),
             Output('batch-progress-interval', 'disabled')],
            [Input('start-batch-analysis', 'n_clicks')],
            [State('batch-dataset-selection', 'value'),
             State('batch-modules-selection', 'value')],
            prevent_initial_call=True
        )
        def start_batch_processing(n_clicks, selected_datasets, selected_modules):
            if not n_clicks or not selected_datasets or not selected_modules:
                return dash.no_update, dash.no_update, dash.no_update
            
            try:
                from src.analysis.batch_processor import batch_processor
                
                # Create batch job
                job_id = batch_processor.create_batch_job(
                    selected_datasets, 
                    selected_modules,
                    self.dataset_manager if hasattr(self, 'dataset_manager') else None
                )
                
                # Start processing in background thread
                import threading
                thread = threading.Thread(
                    target=batch_processor.process_batch,
                    args=(job_id, self.dataset_manager if hasattr(self, 'dataset_manager') else None)
                )
                thread.start()
                
                # Return status message
                status_msg = html.Div([
                    html.H4([
                        html.I(className="fas fa-spinner fa-spin"),
                        f" 批量处理作业已启动"
                    ], style={'color': '#3498db'}),
                    html.P(f"作业ID: {job_id[:8]}..."),
                    html.P(f"处理 {len(selected_datasets)} 个数据集"),
                    html.P(f"运行 {len(selected_modules)} 个分析模块"),
                    html.Hr(),
                    html.P("处理完成后可在批量结果页面查看详情。")
                ])
                
                return status_msg, job_id, False  # Enable progress interval
                
            except Exception as e:
                error_msg = html.Div([
                    html.H4([
                        html.I(className="fas fa-exclamation-circle"),
                        " 启动失败"
                    ], style={'color': '#e74c3c'}),
                    html.P(f"错误: {str(e)}")
                ])
                return error_msg, None, True
        
        # Progress update callback
        @self.app.callback(
            Output('batch-job-status', 'children', allow_duplicate=True),
            [Input('batch-progress-interval', 'n_intervals')],
            [State('current-batch-job-id', 'data')],
            prevent_initial_call=True
        )
        def update_batch_progress(n_intervals, job_id):
            if not job_id:
                return dash.no_update
            
            try:
                from src.analysis.batch_processor import batch_processor
                status = batch_processor.get_job_status(job_id)
                
                if status.get('error'):
                    return html.Div([
                        html.H4("作业未找到", style={'color': '#e74c3c'}),
                        html.P(status['error'])
                    ])
                
                # Create progress display
                status_color = {
                    'pending': '#7f8c8d',
                    'running': '#3498db',
                    'completed': '#27ae60',
                    'completed_with_errors': '#f39c12',
                    'failed': '#e74c3c'
                }.get(status['status'], '#7f8c8d')
                
                status_text = {
                    'pending': '等待中',
                    'running': '运行中',
                    'completed': '已完成',
                    'completed_with_errors': '部分完成',
                    'failed': '失败'
                }.get(status['status'], status['status'])
                
                return html.Div([
                    html.H4([
                        html.I(className="fas fa-info-circle" if status['status'] != 'running' 
                                        else "fas fa-spinner fa-spin"),
                        f" 作业状态: {status_text}"
                    ], style={'color': status_color}),
                    html.P(f"作业ID: {job_id[:8]}..."),
                    html.P(f"数据集数: {status['total_datasets']}"),
                    html.P(f"分析模块: {', '.join(status['modules'])}")
                ])
                
            except Exception as e:
                return html.Div([
                    html.P(f"无法获取状态: {str(e)}", style={'color': '#e74c3c'})
                ])
        
        # View batch result callback
        @self.app.callback(
            [Output('batch-result-modal', 'style'),
             Output('batch-result-content', 'children')],
            [Input({'type': 'view-batch-result', 'index': dash.dependencies.ALL}, 'n_clicks'),
             Input('close-batch-result', 'n_clicks')],
            [State({'type': 'view-batch-result', 'index': dash.dependencies.ALL}, 'id')],
            prevent_initial_call=True
        )
        def toggle_batch_result_modal(view_clicks, close_click, button_ids):
            ctx = dash.callback_context
            
            if not ctx.triggered:
                return {'display': 'none'}, ""
            
            trigger_id = ctx.triggered[0]['prop_id']
            
            # Close modal
            if 'close-batch-result' in trigger_id:
                return {'display': 'none'}, ""
            
            # Open modal with results
            if any(view_clicks):
                clicked_idx = next(i for i, clicks in enumerate(view_clicks) if clicks)
                job_id = button_ids[clicked_idx]['index']
                
                try:
                    from src.analysis.batch_processor import batch_processor
                    from pathlib import Path
                    
                    # Load batch report
                    report_file = Path(f"data/batch_results/{job_id}_report.html")
                    if report_file.exists():
                        with open(report_file, 'r', encoding='utf-8') as f:
                            report_html = f.read()
                        
                        return {
                            'display': 'block',
                            'position': 'fixed',
                            'top': '0',
                            'left': '0',
                            'right': '0',
                            'bottom': '0',
                            'backgroundColor': 'rgba(0,0,0,0.5)',
                            'zIndex': '1000'
                        }, html.Iframe(
                            srcDoc=report_html,
                            style={'width': '100%', 'height': '600px', 'border': 'none'}
                        )
                    else:
                        return {
                            'display': 'block',
                            'position': 'fixed',
                            'top': '0',
                            'left': '0',
                            'right': '0',
                            'bottom': '0',
                            'backgroundColor': 'rgba(0,0,0,0.5)',
                            'zIndex': '1000'
                        }, html.Div([
                            html.P("报告文件未找到", style={'color': '#e74c3c'}),
                            html.P(f"预期路径: {report_file}")
                        ])
                        
                except Exception as e:
                    return {
                        'display': 'block',
                        'position': 'fixed',
                        'top': '0',
                        'left': '0',
                        'right': '0',
                        'bottom': '0',
                        'backgroundColor': 'rgba(0,0,0,0.5)',
                        'zIndex': '1000'
                    }, html.Div([
                        html.P(f"加载报告失败: {str(e)}", style={'color': '#e74c3c'})
                    ])
            
            return {'display': 'none'}, ""
    
    def setup_taskqueue_callbacks(self):
        """Setup callbacks for task queue management"""
        # Simple refresh callback for task queue (without main-content output)
        @self.app.callback(
            Output('taskqueue-refresh-interval', 'disabled'),
            [Input('refresh-taskqueue', 'n_clicks'),
             Input('taskqueue-refresh-interval', 'n_intervals')],
            prevent_initial_call=True
        )
        def refresh_taskqueue_simple(manual_clicks, auto_intervals):
            # Simple callback to handle refresh button without content updates
            return False  # Keep interval enabled
        
        # Task action callback (cancel/view)
        @self.app.callback(
            Output('selected-task-id', 'data'),
            [Input({'type': 'task-action', 'index': dash.dependencies.ALL}, 'n_clicks')],
            [State({'type': 'task-action', 'index': dash.dependencies.ALL}, 'id'),
             State({'type': 'task-action', 'index': dash.dependencies.ALL}, 'children')],
            prevent_initial_call=True
        )
        def handle_task_action(n_clicks_list, id_list, labels):
            if not any(n_clicks_list):
                return dash.no_update
            
            # Find which button was clicked
            clicked_idx = next(i for i, clicks in enumerate(n_clicks_list) if clicks)
            task_id = id_list[clicked_idx]['index']
            action = labels[clicked_idx]
            
            try:
                from src.analysis.task_queue import task_queue
                
                if action == "取消":
                    # Cancel the task
                    success = task_queue.cancel_task(task_id)
                    if success:
                        return {'task_id': task_id, 'action': 'cancelled'}
                elif action == "查看":
                    # Get task details
                    status = task_queue.get_task_status(task_id)
                    return {'task_id': task_id, 'action': 'view', 'status': status}
                    
            except Exception as e:
                return {'error': str(e)}
            
            return dash.no_update


if __name__ == "__main__":
    dashboard = ProfessionalDashboard()
    dashboard.run()