"""
Unified LIHC Dashboard
Combines the best features from all dashboard implementations
"""

import sys
from pathlib import Path
import uuid
import base64
import io
import json
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
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Import our utilities
try:
    from src.utils.common import PathManager, ResultsLoader, DataValidator, ConfigManager, ExceptionHandler
    from src.data_processing.data_upload_manager import DataUploadManager, UserDataAnalyzer
    from src.analysis.survival_analysis import SurvivalAnalyzer, create_demo_survival_data
    from src.utils.i18n import i18n
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    # Fallback to basic functionality
    # Create a minimal i18n fallback
    class MockI18n:
        def get_text(self, key, fallback=None):
            return fallback or key
        def set_language(self, lang):
            return True
        def get_current_language(self):
            return 'zh'
    i18n = MockI18n()

class UnifiedLIHCDashboard:
    """Unified dashboard combining all features"""
    
    def __init__(self, results_dir="results"):
        self.path_manager = PathManager()
        self.results_loader = ResultsLoader(results_dir)
        self.config_manager = ConfigManager()
        
        try:
            self.upload_manager = DataUploadManager()
        except:
            self.upload_manager = None
            print("Warning: Upload functionality not available")
        
        # Initialize survival analyzer
        try:
            self.survival_analyzer = SurvivalAnalyzer()
            # Load demo survival data
            self.demo_clinical, self.demo_expression = create_demo_survival_data()
        except:
            self.survival_analyzer = None
            self.demo_clinical = None
            self.demo_expression = None
            print("Warning: Survival analysis functionality not available")
        
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)
        self.user_sessions = {}
        
        # Load demo data
        self.demo_data = self.load_demo_data()
        
        # Setup app
        self.setup_styling()
        self.setup_layout()
        self.setup_callbacks()
    
    def load_demo_data(self):
        """Load demo analysis results"""
        try:
            return self.results_loader.load_all_results()
        except Exception as e:
            print(f"Warning: Could not load demo data: {e}")
            return {'stage1': {}, 'stage2': {}, 'stage3': {}}
    
    def setup_styling(self):
        """Setup modern CSS styling"""
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>LIHC Analysis Platform</title>
                {%favicon%}
                {%css%}
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
                <style>
                ''' + self.get_modern_css() + '''
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
    
    def get_modern_css(self):
        """Modern CSS with Apple-inspired design"""
        return """
        :root {
            --primary-color: #007AFF;
            --secondary-color: #5AC8FA;
            --success-color: #34C759;
            --warning-color: #FF9500;
            --error-color: #FF3B30;
            --background-primary: #F2F2F7;
            --background-secondary: #FFFFFF;
            --text-primary: #000000;
            --text-secondary: #3C3C43;
            --text-tertiary: #8E8E93;
            --border-color: #C6C6C8;
            --border-radius: 12px;
            --shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--background-primary);
            color: var(--text-primary);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }
        
        .app-container {
            max-width: 1400px;
            margin: 0 auto;
            background: var(--background-secondary);
            min-height: 100vh;
            box-shadow: var(--shadow);
        }
        
        .header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .nav-container {
            background: var(--background-secondary);
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        
        .nav-tabs {
            display: flex;
            overflow-x: auto;
            scrollbar-width: none;
        }
        
        .nav-tabs::-webkit-scrollbar {
            display: none;
        }
        
        .nav-tab {
            padding: 1rem 2rem;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .nav-tab:hover {
            color: var(--primary-color);
            background: var(--background-primary);
        }
        
        .nav-tab.active {
            color: var(--primary-color);
            border-bottom-color: var(--primary-color);
            font-weight: 600;
        }
        
        .main-content {
            padding: 2rem;
            min-height: 60vh;
        }
        
        .card {
            background: var(--background-secondary);
            border-radius: var(--border-radius);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            box-shadow: var(--shadow);
            transform: translateY(-2px);
        }
        
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-primary {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: var(--border-radius);
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-primary:hover {
            background: #0056CC;
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: var(--background-primary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 0.75rem 1.5rem;
            border-radius: var(--border-radius);
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-secondary:hover {
            background: var(--border-color);
        }
        
        .upload-zone {
            border: 2px dashed var(--border-color);
            border-radius: var(--border-radius);
            padding: 3rem 2rem;
            text-align: center;
            background: var(--background-primary);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .upload-zone:hover {
            border-color: var(--primary-color);
            background: rgba(0, 122, 255, 0.05);
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .metric-card {
            background: var(--background-secondary);
            padding: 1.5rem;
            border-radius: var(--border-radius);
            border: 1px solid var(--border-color);
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            color: var(--text-secondary);
            font-weight: 500;
        }
        
        .alert {
            padding: 1rem;
            border-radius: var(--border-radius);
            margin-bottom: 1rem;
            border-left: 4px solid;
        }
        
        .alert-success {
            background: rgba(52, 199, 89, 0.1);
            border-left-color: var(--success-color);
            color: #1B5E20;
        }
        
        .alert-warning {
            background: rgba(255, 149, 0, 0.1);
            border-left-color: var(--warning-color);
            color: #E65100;
        }
        
        .alert-error {
            background: rgba(255, 59, 48, 0.1);
            border-left-color: var(--error-color);
            color: #C62828;
        }
        
        .fade-in {
            animation: fadeIn 0.6s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @media (max-width: 768px) {
            .app-container {
                margin: 0;
                box-shadow: none;
            }
            
            .header {
                padding: 1.5rem 1rem;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .main-content {
                padding: 1rem;
            }
            
            .metric-grid {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            }
        }
        """
    
    def setup_layout(self):
        """Setup unified dashboard layout"""
        self.app.layout = html.Div([
            # Store components
            dcc.Store(id='user-session-store'),
            dcc.Store(id='upload-status-store'),
            dcc.Store(id='demo-data-store', data=self.serialize_demo_data()),
            dcc.Store(id='language-store', data='zh'),  # Default to Chinese
            
            # Main container
            html.Div([
                # Header
                self.create_header(),
                
                # Navigation
                self.create_navigation(),
                
                # Main content
                html.Div(id="main-content", className="main-content"),
                
            ], className="app-container")
        ])
    
    def serialize_demo_data(self):
        """Serialize demo data for client storage"""
        serialized = {}
        for stage, data in self.demo_data.items():
            if isinstance(data, dict):
                serialized[stage] = {}
                for key, value in data.items():
                    if isinstance(value, pd.DataFrame):
                        serialized[stage][key] = value.to_dict('records')
                    else:
                        serialized[stage][key] = value
            elif isinstance(data, pd.DataFrame):
                serialized[stage] = data.to_dict('records')
            else:
                serialized[stage] = data
        return serialized
    
    def create_header(self):
        """Create dashboard header"""
        return html.Div([
            html.Div([
                html.H1(id="header-title"),
                html.P(id="header-subtitle")
            ], style={'flex': '1'}),
            
            # Language switcher
            html.Div([
                html.Button([
                    html.Span("🌐", style={'marginRight': '5px'}),
                    html.Span(id="lang-button-text")
                ], id="language-switcher", className="btn-secondary", 
                   style={
                       'background': 'rgba(255,255,255,0.2)',
                       'border': '1px solid rgba(255,255,255,0.3)',
                       'color': 'white',
                       'fontSize': '0.9rem'
                   })
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], className="header", style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'})
    
    def create_navigation(self):
        """Create navigation tabs"""
        return html.Div([
            html.Div([
                html.Button([html.Span("🏠"), html.Span(id="nav-overview-text")], 
                           id="nav-overview", className="nav-tab active"),
                html.Button([html.Span("📊"), html.Span(id="nav-demo-text")], 
                           id="nav-demo", className="nav-tab"),
                html.Button([html.Span("📤"), html.Span(id="nav-upload-text")], 
                           id="nav-upload", className="nav-tab"),
                html.Button([html.Span("🎯"), html.Span(id="nav-linchpins-text")], 
                           id="nav-linchpins", className="nav-tab"),
                html.Button([html.Span("🕸️"), html.Span(id="nav-networks-text")], 
                           id="nav-networks", className="nav-tab"),
                html.Button([html.Span("🌳"), html.Span(id="nav-multidim-text")], 
                           id="nav-multidim", className="nav-tab"),
                html.Button([html.Span("📈"), html.Span(id="nav-survival-text")], 
                           id="nav-survival", className="nav-tab"),
                html.Button([html.Span("📝"), html.Span(id="nav-templates-text")], 
                           id="nav-templates", className="nav-tab"),
            ], className="nav-tabs")
        ], className="nav-container")
    
    def create_overview_content(self):
        """Create overview page"""
        return html.Div([
            # Hero section
            html.Div([
                html.H2(i18n.get_text('from_biomarker_to_targets'), className="card-title"),
                html.P([
                    i18n.get_text('platform_intro')
                ], style={"fontSize": "1.1rem", "marginBottom": "1.5rem"}),
                
                html.Div([
                    html.Button([html.Span("🚀"), i18n.get_text('explore_demo')], 
                               id="demo-btn", className="btn-primary", 
                               style={"marginRight": "1rem"}),
                    html.Button([html.Span("📤"), i18n.get_text('upload_data')], 
                               id="upload-btn", className="btn-secondary"),
                ], style={"textAlign": "center"})
            ], className="card"),
            
            # Quick scoring guide
            html.Div([
                html.H3(i18n.get_text('scoring_guide'), className="card-title"),
                html.P(i18n.get_text('scoring_intro'), className="mb-3"),
                html.Div([
                    html.Div([
                        html.H5([html.Span("🎯 "), i18n.get_text('linchpin_score')], className="text-primary"),
                        html.P(i18n.get_text('linchpin_desc'), className="small font-weight-bold"),
                        html.P(i18n.get_text('linchpin_detail'), className="small")
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H5([html.Span("📈 "), i18n.get_text('prognostic_score')], className="text-success"),
                        html.P(i18n.get_text('prognostic_desc'), className="small font-weight-bold"),
                        html.P(i18n.get_text('prognostic_detail'), className="small")
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H5([html.Span("🕸️ "), i18n.get_text('network_hub_score')], className="text-info"),
                        html.P(i18n.get_text('network_desc'), className="small font-weight-bold"),
                        html.P(i18n.get_text('network_detail'), className="small")
                    ], className="metric-card")
                ], className="metric-grid"),
                html.P([
                    html.Strong([html.Span("💡 "), i18n.get_text('usage_tip'), ": "]),
                    i18n.get_text('usage_detail')
                ], className="text-muted small mt-3")
            ], className="card"),
            
            # Platform features
            html.Div([
                html.H3([html.Span("✨ "), i18n.get_text('platform_capabilities')], className="card-title"),
                html.Div([
                    html.Div([
                        html.H4([html.Span("🧬 "), i18n.get_text('multidim_analysis')]),
                        html.P(i18n.get_text('multidim_desc')),
                        html.Ul([
                            html.Li("Cox proportional hazards modeling"),
                            html.Li("Immune infiltration deconvolution"),
                            html.Li("Pathway enrichment analysis")
                        ])
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H4([html.Span("🕸️ "), i18n.get_text('network_integration')]),
                        html.P(i18n.get_text('network_integration_desc')),
                        html.Ul([
                            html.Li("WGCNA-style module detection"),
                            html.Li("Network centrality analysis"),
                            html.Li("Cross-dimensional correlations")
                        ])
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H4([html.Span("🎯 "), i18n.get_text('linchpin_scoring')]),
                        html.P(i18n.get_text('linchpin_scoring_desc')),
                        html.Ul([
                            html.Li("Prognostic importance (40%)"),
                            html.Li("Network centrality (30%)"),
                            html.Li("Cross-dimensional impact (20%)"),
                            html.Li("Regulatory potential (10%)")
                        ])
                    ], className="metric-card"),
                ], className="metric-grid")
            ], className="card"),
            
            # Analysis workflow
            html.Div([
                html.H3([html.Span("⚡ "), i18n.get_text('analysis_workflow')], className="card-title"),
                html.Div([
                    html.Div([
                        html.H4("1️⃣ " + i18n.get_text('data_upload')),
                        html.P(i18n.get_text('data_upload_desc')),
                        html.Small(i18n.get_text('multiple_formats'))
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H4("2️⃣ " + i18n.get_text('multidim_analysis_step')),
                        html.P(i18n.get_text('multidim_desc_step')),
                        html.Small("Prognostic factor identification")
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H4("3️⃣ " + i18n.get_text('network_integration_step')),
                        html.P(i18n.get_text('network_desc_step')),
                        html.Small("Hub and module detection")
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H4("4️⃣ " + i18n.get_text('linchpin_discovery')),
                        html.P(i18n.get_text('linchpin_desc_step')),
                        html.Small("Therapeutic target prioritization")
                    ], className="metric-card"),
                ], className="metric-grid")
            ], className="card")
        ], className="fade-in")
    
    def create_demo_content(self):
        """Create demo results page"""
        linchpin_data = self.demo_data.get('stage3', {}).get('linchpin_scores', [])
        stage1_data = self.demo_data.get('stage1', {})
        
        return html.Div([
            html.Div([
                html.H2("📊 Demo Analysis Results", className="card-title"),
                html.P("Comprehensive TCGA-LIHC analysis demonstrating platform capabilities")
            ], className="card"),
            
            # Top linchpins
            self.create_linchpin_showcase(linchpin_data),
            
            # Multi-dimensional overview
            self.create_multidim_overview(stage1_data),
            
            # Network analysis preview
            self.create_network_preview(),
            
            # Survival analysis preview
            self.create_survival_preview(),
            
            # Add comprehensive chart-based comparative analysis
            self.create_score_comparison_charts(linchpin_data),
            self.create_multidim_charts(stage1_data),
            self.create_network_charts()
        ], className="fade-in")
    
    def create_linchpin_showcase(self, linchpin_data):
        """Create linchpin results showcase"""
        if linchpin_data is None or (hasattr(linchpin_data, 'empty') and linchpin_data.empty) or (isinstance(linchpin_data, list) and len(linchpin_data) == 0):
            return html.Div([
                html.H3("🎯 Top Linchpin Molecules", className="card-title"),
                html.P("No linchpin analysis results available. Run the complete pipeline to see results.")
            ], className="card")
        
        # Convert to DataFrame if needed
        if isinstance(linchpin_data, list):
            df = pd.DataFrame(linchpin_data)
        else:
            df = linchpin_data
        
        top_10 = df.head(10)
        
        return html.Div([
            # Add scoring explanation first
            html.Div([
                html.H4("📊 评分指标说明", className="mb-3"),
                
                # Linchpin Score explanation
                html.Div([
                    html.H6("🎯 Linchpin Score (关键节点评分)", className="text-primary"),
                    html.P([
                        "综合评分，整合多个维度的重要性指标。",
                        html.Br(),
                        html.Strong("计算公式: "),
                        "Linchpin Score = 0.4×预后评分 + 0.3×网络中心性评分 + 0.2×跨维度连接性 + 0.1×调控重要性"
                    ], className="small mb-2"),
                    html.P([
                        html.Strong("数据来源: "),
                        "多维度生物学分析整合结果"
                    ], className="small text-muted mb-3")
                ]),
                
                # Prognostic Score explanation  
                html.Div([
                    html.H6("📈 Prognostic Score (预后评分)", className="text-success"),
                    html.P([
                        "基于Cox回归分析的生存预测能力评分。",
                        html.Br(),
                        html.Strong("计算方法: "),
                        "Cox(survival_time, gene_expression) → hazard_ratio → normalized_score"
                    ], className="small mb-2"),
                    html.P([
                        html.Strong("数据来源: "),
                        "临床生存数据 + 基因表达数据的统计关联分析"
                    ], className="small text-muted mb-3")
                ]),
                
                # Network Hub Score explanation
                html.Div([
                    html.H6("🕸️ Network Hub Score (网络中心性评分)", className="text-info"),
                    html.P([
                        "在分子相互作用网络中的重要程度评分。",
                        html.Br(),
                        html.Strong("计算方法: "),
                        "degree_centrality + betweenness_centrality + closeness_centrality 综合标准化"
                    ], className="small mb-2"),
                    html.P([
                        html.Strong("数据来源: "),
                        "基因表达相关性网络 + 蛋白质相互作用网络(STRING数据库)"
                    ], className="small text-muted mb-3")
                ]),
                
                # Interpretation guide
                html.Div([
                    html.H6("📋 分数解读指南", className="text-warning"),
                    html.Ul([
                        html.Li("分数范围: 0.0 - 1.0 (分数越高，作为治疗靶点的潜力越大)"),
                        html.Li("🥇 优秀靶点 (≥0.8): 强烈推荐，具有强证据支持"),
                        html.Li("🥈 良好靶点 (0.6-0.8): 值得关注，证据较强"),
                        html.Li("🥉 潜在靶点 (0.4-0.6): 需要进一步验证"),
                        html.Li("❓ 证据不足 (<0.4): 不推荐作为治疗靶点")
                    ], className="small")
                ], className="mt-3")
                
            ], className="alert alert-light border p-3 mb-4"),
            
            html.H3("🎯 Top Linchpin Molecules", className="card-title"),
            
            # Top 3 highlight
            html.Div([
                html.Div([
                    html.H4("🥇 #1 Target"),
                    html.H5(str(top_10.iloc[0]['gene_id']) if len(top_10) > 0 else "N/A"),
                    html.P(f"Score: {top_10.iloc[0].get('linchpin_score', 0):.3f}" if len(top_10) > 0 else "N/A")
                ], className="metric-card"),
                
                html.Div([
                    html.H4("🥈 #2 Target"),
                    html.H5(str(top_10.iloc[1]['gene_id']) if len(top_10) > 1 else "N/A"),
                    html.P(f"Score: {top_10.iloc[1].get('linchpin_score', 0):.3f}" if len(top_10) > 1 else "N/A")
                ], className="metric-card"),
                
                html.Div([
                    html.H4("🥉 #3 Target"),
                    html.H5(str(top_10.iloc[2]['gene_id']) if len(top_10) > 2 else "N/A"),
                    html.P(f"Score: {top_10.iloc[2].get('linchpin_score', 0):.3f}" if len(top_10) > 2 else "N/A")
                ], className="metric-card")
            ], className="metric-grid"),
            
            # Full table with enhanced column descriptions
            dash_table.DataTable(
                data=top_10.to_dict('records'),
                columns=[
                    {
                        "name": ["Gene", "基因名称"], 
                        "id": "gene_id",
                        "presentation": "markdown"
                    },
                    {
                        "name": ["Linchpin Score", "关键节点评分 (综合评分)"], 
                        "id": "linchpin_score", 
                        "type": "numeric", 
                        "format": {"specifier": ".3f"}
                    },
                    {
                        "name": ["Prognostic Score", "预后评分 (生存预测)"], 
                        "id": "prognostic_score", 
                        "type": "numeric", 
                        "format": {"specifier": ".3f"}
                    },
                    {
                        "name": ["Network Hub Score", "网络中心性评分 (连接重要性)"], 
                        "id": "network_hub_score", 
                        "type": "numeric", 
                        "format": {"specifier": ".3f"}
                    }
                ],
                tooltip_data=[
                    {
                        "gene_id": {"value": f"基因符号: {row['gene_id']}", "type": "text"},
                        "linchpin_score": {"value": f"综合评分: {row.get('linchpin_score', 0):.3f}\n计算方法: 多维度指标加权平均\n权重: 预后40% + 网络30% + 连接20% + 调控10%", "type": "text"},
                        "prognostic_score": {"value": f"预后评分: {row.get('prognostic_score', 0):.3f}\n基于Cox回归分析\n反映基因表达与患者生存的关联强度", "type": "text"},
                        "network_hub_score": {"value": f"网络中心性: {row.get('network_hub_score', 0):.3f}\n基于网络拓扑分析\n度中心性 + 介数中心性 + 接近中心性", "type": "text"}
                    } for row in top_10.to_dict('records')
                ],
                tooltip_delay=0,
                tooltip_duration=None,
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'fontWeight': 'bold'},
                style_data_conditional=[
                    {
                        'if': {'row_index': 0},
                        'backgroundColor': 'rgba(0, 122, 255, 0.1)',
                        'fontWeight': 'bold'
                    }
                ]
            )
        ], className="card")
    
    def create_multidim_overview(self, stage1_data):
        """Create multi-dimensional analysis overview"""
        return html.Div([
            html.H3("🌳 Multi-dimensional Analysis", className="card-title"),
            html.Div([
                html.Div([
                    html.H4("🦠 Tumor Cells"),
                    html.P(f"{len(stage1_data.get('tumor_cells', []))} genes"),
                    html.Small("Oncogenes & suppressors")
                ], className="metric-card"),
                
                html.Div([
                    html.H4("🛡️ Immune Cells"),
                    html.P(f"{len(stage1_data.get('immune_cells', []))} factors"),
                    html.Small("Immune infiltration")
                ], className="metric-card"),
                
                html.Div([
                    html.H4("🧬 Stromal Cells"),
                    html.P(f"{len(stage1_data.get('stromal_cells', []))} genes"),
                    html.Small("Microenvironment")
                ], className="metric-card"),
                
                html.Div([
                    html.H4("🕸️ ECM"),
                    html.P(f"{len(stage1_data.get('ecm', []))} proteins"),
                    html.Small("Extracellular matrix")
                ], className="metric-card"),
                
                html.Div([
                    html.H4("💬 Cytokines"),
                    html.P(f"{len(stage1_data.get('cytokines', []))} signals"),
                    html.Small("Signaling molecules")
                ], className="metric-card")
            ], className="metric-grid")
        ], className="card")
    
    def create_network_preview(self):
        """Create network analysis preview"""
        network_data = self.demo_data.get('stage2', {}).get('centrality', [])
        
        return html.Div([
            html.H3("🕸️ Network Analysis", className="card-title"),
            html.Div([
                html.Div([
                    html.H4("Network Nodes"),
                    html.P(f"{len(network_data)}", className="metric-value"),
                    html.Small("Connected genes")
                ], className="metric-card"),
                
                html.Div([
                    html.H4("Hub Genes"),
                    html.P("15", className="metric-value"),
                    html.Small("High centrality")
                ], className="metric-card"),
                
                html.Div([
                    html.H4("Modules"),
                    html.P("8", className="metric-value"),
                    html.Small("Functional clusters")
                ], className="metric-card")
            ], className="metric-grid")
        ], className="card")
    
    def create_survival_preview(self):
        """Create survival analysis preview"""
        return html.Div([
            html.H3(["📈 ", i18n.get_text('survival_analysis')], className="card-title"),
            html.Div([
                html.Div([
                    html.H4(["🎯 ", i18n.get_text('target_genes')]),
                    html.P("8", className="metric-value"),
                    html.Small(i18n.get_text('available_for_analysis'))
                ], className="metric-card"),
                
                html.Div([
                    html.H4(["👥 ", i18n.get_text('patient_cohort')]),
                    html.P("200", className="metric-value"),
                    html.Small(i18n.get_text('tcga_samples'))
                ], className="metric-card"),
                
                html.Div([
                    html.H4(["📊 ", i18n.get_text('analysis_types')]),
                    html.P("2", className="metric-value"),
                    html.Small(i18n.get_text('os_rfs_endpoints'))
                ], className="metric-card"),
                
                html.Div([
                    html.H4(["📈 ", i18n.get_text('kaplan_meier')]),
                    html.P("✓", className="metric-value"),
                    html.Small(i18n.get_text('with_logrank_test'))
                ], className="metric-card")
            ], className="metric-grid"),
            
            html.Div([
                html.P([
                    "🔬 ", html.Strong([i18n.get_text('functional_features'), ":"], ), " ", i18n.get_text('survival_features_desc')
                ], className="small mb-2"),
                html.P([
                    "📊 ", html.Strong([i18n.get_text('analysis_method'), ":"], ), " ", i18n.get_text('analysis_method_desc')
                ], className="small mb-2"),
                html.Div([
                    html.Button([html.Span("📈"), i18n.get_text('try_survival_analysis')], 
                               id="survival-preview-btn", className="btn-primary btn-sm")
                ], style={'textAlign': 'center', 'marginTop': '15px'})
            ], style={'marginTop': '15px'})
        ], className="card")
    
    def create_score_comparison_charts(self, linchpin_data):
        """Create comprehensive score comparison charts"""
        if linchpin_data is None or (hasattr(linchpin_data, 'empty') and linchpin_data.empty) or (isinstance(linchpin_data, list) and len(linchpin_data) == 0):
            return html.Div()
        
        # Convert to DataFrame if needed
        if isinstance(linchpin_data, list):
            df = pd.DataFrame(linchpin_data)
        else:
            df = linchpin_data
        
        top_15 = df.head(15)
        
        return html.Div([
            html.Div([
                html.H3(["📊 ", i18n.get_text('score_comparison_analysis')], className="card-title"),
                html.P(i18n.get_text('professional_chart_desc'))
            ], className="card"),
            
            # Bar chart comparison
            html.Div([
                html.H4(["📈 ", i18n.get_text('score_comparison_bar')], className="card-title"),
                dcc.Graph(
                    figure=self._create_score_bar_chart(top_15),
                    config={'displayModeBar': True}
                )
            ], className="card"),
            
            # Radar chart for top 5
            html.Div([
                html.H4(["🕸️ ", i18n.get_text('multidim_radar')], className="card-title"),
                dcc.Graph(
                    figure=self._create_score_radar_chart(top_15.head(5)),
                    config={'displayModeBar': True}
                )
            ], className="card"),
            
            # Scatter plot analysis
            html.Div([
                html.H4(["🎯 ", i18n.get_text('score_correlation_scatter')], className="card-title"),
                dcc.Graph(
                    figure=self._create_score_scatter_plot(top_15),
                    config={'displayModeBar': True}
                )
            ], className="card")
        ])
    
    def create_multidim_charts(self, stage1_data):
        """Create multi-dimensional analysis charts"""
        if not stage1_data or len(stage1_data) == 0:
            return html.Div()
        
        return html.Div([
            html.Div([
                html.H3(["🌳 ", i18n.get_text('multidim_analysis_charts')], className="card-title"),
                html.P(i18n.get_text('comprehensive_viz'))  
            ], className="card"),
            
            # Dimension sizes pie chart
            html.Div([
                html.H4(["📊 ", i18n.get_text('dimension_distribution')], className="card-title"),
                dcc.Graph(
                    figure=self._create_dimension_pie_chart(stage1_data),
                    config={'displayModeBar': True}
                )
            ], className="card"),
            
            # Dimension comparison bar chart
            html.Div([
                html.H4(["📈 ", i18n.get_text('dimension_comparison')], className="card-title"),
                dcc.Graph(
                    figure=self._create_dimension_bar_chart(stage1_data),
                    config={'displayModeBar': True}
                )
            ], className="card")
        ])
    
    def create_network_charts(self):
        """Create network analysis charts"""
        network_data = self.demo_data.get('stage2', {}).get('centrality', [])
        
        # Fixed pandas DataFrame boolean evaluation issue
        if network_data is None or (hasattr(network_data, 'empty') and network_data.empty) or (isinstance(network_data, list) and len(network_data) == 0):
            return html.Div()
        
        return html.Div([
            html.Div([
                html.H3(["🕸️ ", i18n.get_text('network_analysis_charts')], className="card-title"),
                html.P(i18n.get_text('interactive_network_viz'))
            ], className="card"),
            
            # Network centrality comparison
            html.Div([
                html.H4(["📊 ", i18n.get_text('centrality_distribution')], className="card-title"),
                dcc.Graph(
                    figure=self._create_centrality_chart(network_data),
                    config={'displayModeBar': True}
                )
            ], className="card"),
            
            # Network topology overview
            html.Div([
                html.H4(["🕸️ Network Topology Overview"], className="card-title"),
                dcc.Graph(
                    figure=self._create_network_topology_chart(network_data),
                    config={'displayModeBar': True}
                )
            ], className="card")
        ])
    
    def _create_score_bar_chart(self, data):
        """Create score comparison bar chart"""
        fig = make_subplots(rows=1, cols=1)
        
        # Add bars for each score type
        fig.add_trace(go.Bar(
            name='Linchpin Score',
            x=data['gene_id'],
            y=data.get('linchpin_score', [0]*len(data)),
            marker_color='#007AFF',
            yaxis='y1'
        ))
        
        fig.add_trace(go.Bar(
            name='Prognostic Score',
            x=data['gene_id'],
            y=data.get('prognostic_score', [0]*len(data)),
            marker_color='#34C759',
            yaxis='y1'
        ))
        
        fig.add_trace(go.Bar(
            name='Network Hub Score',
            x=data['gene_id'],
            y=data.get('network_hub_score', [0]*len(data)),
            marker_color='#FF9500',
            yaxis='y1'
        ))
        
        fig.update_layout(
            title="Score Comparison Across Top Genes",
            xaxis_title="Genes",
            yaxis_title="Score",
            barmode='group',
            height=500,
            template="plotly_white"
        )
        
        return fig
    
    def _create_score_radar_chart(self, data):
        """Create radar chart for top genes"""
        if len(data) == 0:
            return go.Figure()
        
        fig = go.Figure()
        
        categories = ['Linchpin Score', 'Prognostic Score', 'Network Hub Score']
        
        for idx, row in data.iterrows():
            values = [
                row.get('linchpin_score', 0),
                row.get('prognostic_score', 0),
                row.get('network_hub_score', 0)
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=str(row['gene_id'])
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="Multi-dimensional Score Radar Chart (Top 5 Genes)",
            height=500
        )
        
        return fig
    
    def _create_score_scatter_plot(self, data):
        """Create scatter plot for score correlation"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data.get('prognostic_score', []),
            y=data.get('network_hub_score', []),
            mode='markers+text',
            text=data['gene_id'],
            textposition="top center",
            marker=dict(
                size=data.get('linchpin_score', [0]*len(data)) * 30 + 5,
                color=data.get('linchpin_score', []),
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Linchpin Score")
            ),
            name='Genes'
        ))
        
        fig.update_layout(
            title="Score Correlation Analysis",
            xaxis_title="Prognostic Score",
            yaxis_title="Network Hub Score",
            height=500,
            template="plotly_white"
        )
        
        return fig
    
    def _create_dimension_pie_chart(self, stage1_data):
        """Create pie chart for dimension distribution"""
        dimensions = []
        counts = []
        
        dim_map = {
            'tumor_cells': '🦠 Tumor Cells',
            'immune_cells': '🛡️ Immune Cells', 
            'stromal_cells': '🧬 Stromal Cells',
            'ecm': '🕸️ ECM',
            'cytokines': '💬 Cytokines'
        }
        
        for key, label in dim_map.items():
            count = len(stage1_data.get(key, []))
            if count > 0:
                dimensions.append(label)
                counts.append(count)
        
        fig = go.Figure(data=[go.Pie(
            labels=dimensions,
            values=counts,
            hole=0.3,
            textinfo='label+percent+value'
        )])
        
        fig.update_layout(
            title="Distribution of Genes Across Dimensions",
            height=400
        )
        
        return fig
    
    def _create_dimension_bar_chart(self, stage1_data):
        """Create bar chart for dimension comparison"""
        dimensions = []
        counts = []
        
        dim_map = {
            'tumor_cells': '🦠 Tumor Cells',
            'immune_cells': '🛡️ Immune Cells', 
            'stromal_cells': '🧬 Stromal Cells',
            'ecm': '🕸️ ECM',
            'cytokines': '💬 Cytokines'
        }
        
        for key, label in dim_map.items():
            dimensions.append(label)
            counts.append(len(stage1_data.get(key, [])))
        
        fig = go.Figure(data=[go.Bar(
            x=dimensions,
            y=counts,
            marker_color=['#FF3B30', '#007AFF', '#34C759', '#FF9500', '#5AC8FA']
        )])
        
        fig.update_layout(
            title="Gene Count by Biological Dimension",
            xaxis_title="Biological Dimensions",
            yaxis_title="Number of Genes",
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    def _create_centrality_chart(self, network_data):
        """Create centrality distribution chart"""
        if isinstance(network_data, list) and len(network_data) > 0:
            df = pd.DataFrame(network_data)
        elif hasattr(network_data, 'columns'):
            df = network_data
        else:
            return go.Figure()
        
        if len(df) == 0:
            return go.Figure()
        
        # Create subplots for different centrality measures
        from plotly.subplots import make_subplots
        
        # Check which centrality columns are available
        centrality_cols = {
            'degree_centrality': 'Degree Centrality',
            'betweenness_centrality': 'Betweenness Centrality', 
            'closeness_centrality': 'Closeness Centrality',
            'eigenvector_centrality': 'Eigenvector Centrality'
        }
        
        available_cols = [col for col in centrality_cols.keys() if col in df.columns]
        
        if not available_cols:
            return go.Figure()
        
        # Create a bar chart showing top genes by degree centrality
        if 'degree_centrality' in df.columns and 'gene_id' in df.columns:
            # Sort by degree centrality and take top 10
            top_genes = df.nlargest(10, 'degree_centrality')
            
            fig = go.Figure()
            
            # Add bars for each centrality measure
            colors = ['#007AFF', '#34C759', '#FF9500', '#FF3B30']
            
            for i, (col, label) in enumerate(centrality_cols.items()):
                if col in df.columns:
                    fig.add_trace(go.Bar(
                        name=label,
                        x=top_genes['gene_id'],
                        y=top_genes[col],
                        marker_color=colors[i % len(colors)],
                        opacity=0.8
                    ))
            
            fig.update_layout(
                title="Network Centrality Comparison (Top 10 Genes)",
                xaxis_title="Genes",
                yaxis_title="Centrality Score",
                barmode='group',
                height=500,
                template="plotly_white",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
        
        # Fallback: create a simple histogram if gene_id not available
        fig = go.Figure()
        
        if available_cols:
            fig.add_trace(go.Histogram(
                x=df[available_cols[0]],
                nbinsx=15,
                name=centrality_cols[available_cols[0]],
                marker_color='#007AFF'
            ))
        
        fig.update_layout(
            title="Network Centrality Distribution",
            xaxis_title="Centrality Score",
            yaxis_title="Frequency",
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    def _create_network_topology_chart(self, network_data):
        """Create network topology overview chart"""
        if isinstance(network_data, list) and len(network_data) > 0:
            df = pd.DataFrame(network_data)
        elif hasattr(network_data, 'columns'):
            df = network_data
        else:
            return go.Figure()
        
        if len(df) == 0 or 'gene_id' not in df.columns:
            return go.Figure()
        
        # Create a network-style scatter plot showing gene relationships
        fig = go.Figure()
        
        # Use degree centrality as main positioning factor
        if 'degree_centrality' in df.columns:
            # Create a circular layout based on degree centrality
            import numpy as np
            n_nodes = len(df)
            angles = np.linspace(0, 2*np.pi, n_nodes, endpoint=False)
            
            # Position nodes in circle, with size based on centrality
            x_pos = np.cos(angles) * (df['degree_centrality'] * 2 + 0.5)
            y_pos = np.sin(angles) * (df['degree_centrality'] * 2 + 0.5)
            
            # Add network nodes
            fig.add_trace(go.Scatter(
                x=x_pos,
                y=y_pos,
                mode='markers+text',
                text=df['gene_id'],
                textposition="middle center",
                marker=dict(
                    size=df['degree_centrality'] * 40 + 10,
                    color=df.get('betweenness_centrality', df['degree_centrality']),
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Centrality Score"),
                    line=dict(width=2, color='white')
                ),
                name='Network Nodes',
                hovertemplate=(
                    "<b>%{text}</b><br>" +
                    "Degree Centrality: %{marker.size}<br>" +
                    "Position: (%{x:.2f}, %{y:.2f})<br>" +
                    "<extra></extra>"
                )
            ))
            
            # Add some edges for top connected nodes
            top_nodes = df.nlargest(5, 'degree_centrality')
            edge_x = []
            edge_y = []
            
            for i in range(len(top_nodes)-1):
                edge_x.extend([x_pos[i], x_pos[i+1], None])
                edge_y.extend([y_pos[i], y_pos[i+1], None])
            
            # Add edges
            fig.add_trace(go.Scatter(
                x=edge_x,
                y=edge_y,
                mode='lines',
                line=dict(width=1, color='rgba(100,100,100,0.3)'),
                hoverinfo='none',
                name='Network Edges',
                showlegend=False
            ))
        
        fig.update_layout(
            title="Network Topology Overview",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=500,
            template="plotly_white",
            showlegend=True
        )
        
        return fig
    
    def create_upload_content(self):
        """Create data upload interface"""
        return html.Div([
            html.Div([
                html.H2(["📤 ", i18n.get_text('upload_title')], className="card-title"),
                html.P(i18n.get_text('upload_subtitle'))
            ], className="card"),
            
            # Upload instructions
            html.Div([
                html.H4(["📋 ", i18n.get_text('data_requirements')]),
                html.Ul([
                    html.Li(["📊 ", i18n.get_text('clinical_data'), ": ", i18n.get_text('clinical_desc')]),
                    html.Li(["🧬 ", i18n.get_text('expression_data'), ": ", i18n.get_text('expression_desc')]),
                    html.Li(["🔬 ", i18n.get_text('mutation_data'), ": ", i18n.get_text('mutation_desc')])
                ])
            ], className="card"),
            
            # Upload zone
            html.Div([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        html.H3("📁", style={"fontSize": "3rem", "margin": "0"}),
                        html.P(i18n.get_text('drag_drop_files')),
                        html.Small(i18n.get_text('supported_formats'))
                    ]),
                    className="upload-zone",
                    multiple=True
                )
            ], className="card"),
            
            # Upload status
            html.Div(id="upload-status"),
            
            # Analysis button
            html.Div([
                html.Button([html.Span("🚀"), i18n.get_text('run_analysis')], 
                           id="run-analysis-btn", className="btn-primary", disabled=True)
            ], className="card", style={"textAlign": "center"}),
            
            # Progress
            html.Div(id="analysis-progress")
        ], className="fade-in")
    
    def create_survival_content(self):
        """Create survival analysis page"""
        if not self.survival_analyzer:
            return html.Div([
                html.Div([
                    html.H2(["📈 ", i18n.get_text('survival_analysis')], className="card-title"),
                    html.P("Survival analysis functionality is not available", className="text-muted")
                ], className="card")
            ], className="fade-in")
        
        return html.Div([
            html.Div([
                html.H2(["📈 ", i18n.get_text('survival_analysis')], className="card-title"),
                html.P("Kaplan-Meier survival curves with Log-rank test for gene expression analysis")
            ], className="card"),
            
            # Gene selection interface
            html.Div([
                html.H4(["🎯 ", i18n.get_text('gene_selection')], className="card-title"),
                html.Div([
                    html.Div([
                        html.Label([i18n.get_text('target_gene'), ":"], className="form-label"),
                        dcc.Dropdown(
                            id="survival-gene-dropdown",
                            options=[
                                {'label': 'TP53 (Tumor Protein P53)', 'value': 'TP53'},
                                {'label': 'MYC (MYC Proto-Oncogene)', 'value': 'MYC'},
                                {'label': 'KRAS (Kirsten Rat Sarcoma)', 'value': 'KRAS'},
                                {'label': 'EGFR (Epidermal Growth Factor Receptor)', 'value': 'EGFR'},
                                {'label': 'VEGFA (Vascular Endothelial Growth Factor A)', 'value': 'VEGFA'},
                                {'label': 'PIK3CA (Phosphatidylinositol-4,5-Bisphosphate 3-Kinase)', 'value': 'PIK3CA'},
                                {'label': 'PTEN (Phosphatase and Tensin Homolog)', 'value': 'PTEN'},
                                {'label': 'CTNNB1 (Catenin Beta 1)', 'value': 'CTNNB1'}
                            ],
                            value='TP53',
                            placeholder="Select a gene for survival analysis",
                            style={'marginBottom': '15px'}
                        )
                    ], className="col-6"),
                    
                    html.Div([
                        html.Label([i18n.get_text('dataset'), ":"], className="form-label"),
                        dcc.Dropdown(
                            id="survival-dataset-dropdown",
                            options=[
                                {'label': 'TCGA-LIHC (Demo Data)', 'value': 'TCGA-LIHC'}
                            ],
                            value='TCGA-LIHC',
                            placeholder="Select dataset",
                            style={'marginBottom': '15px'}
                        )
                    ], className="col-6"),
                ], className="row"),
                
                html.Div([
                    html.Button([html.Span("📊"), i18n.get_text('generate_survival_curves')], 
                               id="run-survival-btn", className="btn-primary")
                ], style={'textAlign': 'center', 'marginTop': '20px'})
            ], className="card"),
            
            # Analysis explanation
            html.Div([
                html.H4(["📋 ", i18n.get_text('analysis_method')], className="card-title"),
                html.Div([
                    html.Div([
                        html.H6(["📊 ", i18n.get_text('grouping_strategy')], className="text-primary"),
                        html.P(i18n.get_text('grouping_desc'))
                    ], className="col-6"),
                    
                    html.Div([
                        html.H6(["📈 ", i18n.get_text('analysis_endpoints')], className="text-success"),
                        html.Ul([
                            html.Li([i18n.get_text('overall_survival'), ": ", i18n.get_text('os_desc')]),
                            html.Li([i18n.get_text('recurrence_free_survival'), ": ", i18n.get_text('rfs_desc')])
                        ])
                    ], className="col-6"),
                ], className="row"),
                
                html.Div([
                    html.Div([
                        html.H6(["📉 ", i18n.get_text('kaplan_meier_method')], className="text-info"),
                        html.P(i18n.get_text('km_desc'))
                    ], className="col-6"),
                    
                    html.Div([
                        html.H6(["📊 ", i18n.get_text('logrank_test')], className="text-warning"),
                        html.P(i18n.get_text('logrank_desc'))
                    ], className="col-6"),
                ], className="row")
            ], className="card"),
            
            # Results area
            html.Div(id="survival-results-container"),
            
        ], className="fade-in")
    
    def create_templates_content(self):
        """Create templates page"""
        return html.Div([
            # Download components for each template
            dcc.Download(id="download-clinical-template"),
            dcc.Download(id="download-expression-template"),
            dcc.Download(id="download-mutation-template"),
            
            html.Div([
                html.H2(["📝 ", i18n.get_text('templates_title')], className="card-title"),
                html.P(i18n.get_text('templates_subtitle'))
            ], className="card"),
            
            html.Div([
                html.Div([
                    html.H4(["📊 ", i18n.get_text('clinical_template')]),
                    html.P(i18n.get_text('clinical_template_desc')),
                    html.Button(i18n.get_text('download'), id="btn-clinical-template", className="btn-secondary"),
                    html.Hr(),
                    html.Small([i18n.get_text('required_fields'), ": sample_id, os_time, os_status"])
                ], className="metric-card"),
                
                html.Div([
                    html.H4(["🧬 ", i18n.get_text('expression_template')]),
                    html.P(i18n.get_text('expression_template_desc')),
                    html.Button(i18n.get_text('download'), id="btn-expression-template", className="btn-secondary"),
                    html.Hr(),
                    html.Small(i18n.get_text('format_desc'))
                ], className="metric-card"),
                
                html.Div([
                    html.H4(["🔬 ", i18n.get_text('mutation_template')]),
                    html.P(i18n.get_text('mutation_template_desc')),
                    html.Button(i18n.get_text('download'), id="btn-mutation-template", className="btn-secondary"),
                    html.Hr(),
                    html.Small([i18n.get_text('required_fields'), ": sample_id, gene, mutation_type"])
                ], className="metric-card")
            ], className="metric-grid")
        ], className="fade-in")
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        # Language switching callback
        @self.app.callback(
            [Output("language-store", "data"),
             Output("header-title", "children"),
             Output("header-subtitle", "children"),
             Output("lang-button-text", "children"),
             Output("nav-overview-text", "children"),
             Output("nav-demo-text", "children"),
             Output("nav-upload-text", "children"),
             Output("nav-linchpins-text", "children"),
             Output("nav-networks-text", "children"),
             Output("nav-multidim-text", "children"),
             Output("nav-survival-text", "children"),
             Output("nav-templates-text", "children")],
            [Input("language-switcher", "n_clicks")],
            [State("language-store", "data")],
            prevent_initial_call=False
        )
        def toggle_language(n_clicks, current_lang):
            # Initialize language on first load
            if n_clicks is None:
                i18n.set_language(current_lang or 'zh')
                current_lang = current_lang or 'zh'
            else:
                # Toggle language
                new_lang = 'en' if current_lang == 'zh' else 'zh'
                i18n.set_language(new_lang)
                current_lang = new_lang
            
            # Update all text elements
            if current_lang == 'zh':
                lang_button_text = "EN"
                header_title = "🧬 LIHC多维度预后分析系统"
                header_subtitle = "基于多维度网络分析的肝癌预后分析平台"
            else:
                lang_button_text = "中文"
                header_title = "🧬 LIHC Multi-dimensional Analysis Platform"
                header_subtitle = "Advanced therapeutic target discovery through integrated omics analysis"
            
            return (
                current_lang,
                header_title,
                header_subtitle,
                lang_button_text,
                i18n.get_text('nav_overview'),
                i18n.get_text('nav_demo'),
                i18n.get_text('nav_upload'),
                i18n.get_text('nav_linchpins'),
                i18n.get_text('nav_networks'),
                i18n.get_text('nav_multidim'),
                i18n.get_text('nav_survival'),
                i18n.get_text('nav_templates')
            )
        
        @self.app.callback(
            Output("main-content", "children"),
            [Input("nav-overview", "n_clicks"),
             Input("nav-demo", "n_clicks"),
             Input("nav-upload", "n_clicks"),
             Input("nav-linchpins", "n_clicks"),
             Input("nav-networks", "n_clicks"),
             Input("nav-multidim", "n_clicks"),
             Input("nav-survival", "n_clicks"),
             Input("nav-templates", "n_clicks"),
             Input("language-store", "data")],  # Add language as trigger
            prevent_initial_call=False
        )
        def update_content(*args):
            ctx = dash.callback_context
            current_lang = args[-1]  # Last argument is language
            i18n.set_language(current_lang or 'zh')
            
            if not ctx.triggered:
                return self.create_overview_content()
            
            # Check if language changed
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if trigger_id == 'language-store':
                # Language changed, refresh current page content
                # We need to determine which page we're currently on
                # For now, default to overview
                return self.create_overview_content()
            
            button_id = trigger_id
            
            content_map = {
                "nav-overview": self.create_overview_content,
                "nav-demo": self.create_demo_content,
                "nav-upload": self.create_upload_content,
                "nav-linchpins": self.create_demo_content,  # Same as demo for now
                "nav-networks": self.create_demo_content,   # Same as demo for now
                "nav-multidim": self.create_demo_content,   # Same as demo for now
                "nav-survival": self.create_survival_content,
                "nav-templates": self.create_templates_content
            }
            
            return content_map.get(button_id, self.create_overview_content)()
        
        # Overview page button callbacks
        @self.app.callback(
            Output("main-content", "children", allow_duplicate=True),
            [Input("demo-btn", "n_clicks"), Input("upload-btn", "n_clicks"), Input("survival-preview-btn", "n_clicks")],
            prevent_initial_call=True
        )
        def handle_overview_buttons(demo_clicks, upload_clicks, survival_clicks):
            ctx = dash.callback_context
            if not ctx.triggered:
                return no_update
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == "demo-btn":
                return self.create_demo_content()
            elif button_id == "upload-btn":
                return self.create_upload_content()
            elif button_id == "survival-preview-btn":
                return self.create_survival_content()
            
            return no_update
        
        # Upload functionality callbacks (only if upload manager is available)
        if self.upload_manager:
            @self.app.callback(
                [Output("upload-status", "children"),
                 Output("run-analysis-btn", "disabled")],
                Input("upload-data", "contents"),
                [State("upload-data", "filename")],
                prevent_initial_call=True
            )
            def handle_upload(contents_list, filename_list):
                if not contents_list:
                    return "No files uploaded.", True
                
                status_items = []
                all_valid = True
                
                for contents, filename in zip(contents_list, filename_list):
                    try:
                        # Simple validation
                        if filename.endswith(('.csv', '.tsv', '.xlsx', '.zip')):
                            status_items.append(
                                html.Div(f"✅ {filename} - Valid format", className="alert-success")
                            )
                        else:
                            status_items.append(
                                html.Div(f"❌ {filename} - Unsupported format", className="alert-error")
                            )
                            all_valid = False
                    except Exception as e:
                        status_items.append(
                            html.Div(f"❌ {filename} - Error: {str(e)}", className="alert-error")
                        )
                        all_valid = False
                
                return html.Div(status_items), not all_valid
        
        # Template download callbacks
        @self.app.callback(
            Output("download-clinical-template", "data"),
            [Input("btn-clinical-template", "n_clicks")],
            prevent_initial_call=True
        )
        def download_clinical_template(n_clicks):
            if n_clicks:
                template_path = self.path_manager.get_data_path('templates', 'clinical_template.csv')
                if template_path.exists():
                    return dcc.send_file(str(template_path), filename="clinical_template.csv")
            return dash.no_update
        
        @self.app.callback(
            Output("download-expression-template", "data"),
            [Input("btn-expression-template", "n_clicks")],
            prevent_initial_call=True
        )
        def download_expression_template(n_clicks):
            if n_clicks:
                template_path = self.path_manager.get_data_path('templates', 'expression_template.csv')
                if template_path.exists():
                    return dcc.send_file(str(template_path), filename="expression_template.csv")
            return dash.no_update
        
        @self.app.callback(
            Output("download-mutation-template", "data"),
            [Input("btn-mutation-template", "n_clicks")],
            prevent_initial_call=True
        )
        def download_mutation_template(n_clicks):
            if n_clicks:
                template_path = self.path_manager.get_data_path('templates', 'mutation_template.csv')
                if template_path.exists():
                    return dcc.send_file(str(template_path), filename="mutation_template.csv")
            return dash.no_update
        
        # Survival analysis callback
        if self.survival_analyzer:
            @self.app.callback(
                Output("survival-results-container", "children"),
                [Input("run-survival-btn", "n_clicks")],
                [State("survival-gene-dropdown", "value"),
                 State("survival-dataset-dropdown", "value")],
                prevent_initial_call=True
            )
            def generate_survival_analysis(n_clicks, gene_name, dataset_name):
                if not n_clicks or not gene_name:
                    return html.Div()
                
                try:
                    # Perform survival analysis
                    results = self.survival_analyzer.perform_survival_analysis(
                        self.demo_clinical, 
                        self.demo_expression, 
                        gene_name, 
                        dataset_name
                    )
                    
                    if results.get('error'):
                        return html.Div([
                            html.Div([
                                html.H4("❌ Analysis Error", className="text-danger"),
                                html.P(results['error'])
                            ], className="alert alert-error")
                        ])
                    
                    # Create survival plots
                    survival_fig = self.survival_analyzer.create_survival_plots(results)
                    
                    # Create results summary
                    summary_cards = []
                    
                    if results.get('os_analysis'):
                        os = results['os_analysis']
                        p_status = "Significant" if os['p_value'] < 0.05 else "Not Significant"
                        p_color = "text-success" if os['p_value'] < 0.05 else "text-muted"
                        
                        summary_cards.append(
                            html.Div([
                                html.H6("📊 Overall Survival", className="text-primary"),
                                html.P(f"Total Samples: {os['total_samples']}", className="small"),
                                html.P(f"High Expression: n={os['high_count']}", className="small"),
                                html.P(f"Low Expression: n={os['low_count']}", className="small"),
                                html.P(f"Log-rank p-value: {os['p_value']:.4f}", className="small font-weight-bold"),
                                html.P(f"Result: {p_status}", className=f"small {p_color}")
                            ], className="metric-card")
                        )
                    
                    if results.get('rfs_analysis'):
                        rfs = results['rfs_analysis']
                        p_status = "Significant" if rfs['p_value'] < 0.05 else "Not Significant"
                        p_color = "text-success" if rfs['p_value'] < 0.05 else "text-muted"
                        
                        summary_cards.append(
                            html.Div([
                                html.H6("📈 Recurrence-Free Survival", className="text-info"),
                                html.P(f"Total Samples: {rfs['total_samples']}", className="small"),
                                html.P(f"High Expression: n={rfs['high_count']}", className="small"),
                                html.P(f"Low Expression: n={rfs['low_count']}", className="small"),
                                html.P(f"Log-rank p-value: {rfs['p_value']:.4f}", className="small font-weight-bold"),
                                html.P(f"Result: {p_status}", className=f"small {p_color}")
                            ], className="metric-card")
                        )
                    
                    return html.Div([
                        # Results summary
                        html.Div([
                            html.H4(f"🎯 Analysis Results: {gene_name}", className="card-title"),
                            html.Div(summary_cards, className="metric-grid")
                        ], className="card"),
                        
                        # Survival plots
                        html.Div([
                            html.H4("📈 Kaplan-Meier Survival Curves", className="card-title"),
                            dcc.Graph(
                                figure=survival_fig, 
                                config={'displayModeBar': True, 'toImageButtonOptions': {
                                    'format': 'png',
                                    'filename': f'survival_analysis_{gene_name}',
                                    'height': 500,
                                    'width': 800,
                                    'scale': 2
                                }}
                            ),
                            html.Div([
                                html.P([
                                    html.Strong("🔍 Interpretation Guide:"), html.Br(),
                                    "• ", html.Strong("Red curve"), ": High expression group", html.Br(),
                                    "• ", html.Strong("Blue curve"), ": Low expression group", html.Br(),
                                    "• ", html.Strong("P < 0.05"), ": Statistically significant difference", html.Br(),
                                    "• ", html.Strong("Higher curve"), ": Better survival probability"
                                ], className="small text-muted")
                            ], style={'marginTop': '15px'})
                        ], className="card"),
                        
                        # Clinical interpretation
                        html.Div([
                            html.H4("🏥 Clinical Interpretation", className="card-title"),
                            html.Div([
                                html.Div([
                                    html.H6("📋 Prognostic Value", className="text-primary"),
                                    html.P(self._get_prognostic_interpretation(results), className="small")
                                ], className="col-6"),
                                
                                html.Div([
                                    html.H6("🎯 Therapeutic Implications", className="text-success"),
                                    html.P(self._get_therapeutic_interpretation(gene_name, results), className="small")
                                ], className="col-6"),
                            ], className="row")
                        ], className="card")
                    ])
                    
                except Exception as e:
                    return html.Div([
                        html.Div([
                            html.H4("❌ Analysis Failed", className="text-danger"),
                            html.P(f"Error: {str(e)}")
                        ], className="alert alert-error")
                    ])
            
    def _get_prognostic_interpretation(self, results):
        """Generate prognostic interpretation text"""
        interpretations = []
        
        if results.get('os_analysis'):
            os_p = results['os_analysis']['p_value']
            if os_p < 0.001:
                interpretations.append("Strong prognostic value for overall survival (p < 0.001)")
            elif os_p < 0.05:
                interpretations.append("Significant prognostic value for overall survival")
            else:
                interpretations.append("No significant prognostic value for overall survival")
        
        if results.get('rfs_analysis'):
            rfs_p = results['rfs_analysis']['p_value']
            if rfs_p < 0.001:
                interpretations.append("Strong prognostic value for recurrence-free survival (p < 0.001)")
            elif rfs_p < 0.05:
                interpretations.append("Significant prognostic value for recurrence-free survival")
            else:
                interpretations.append("No significant prognostic value for recurrence-free survival")
        
        return ". ".join(interpretations) + "."
    
    def _get_therapeutic_interpretation(self, gene_name, results):
        """Generate therapeutic interpretation text"""
        gene_info = {
            'TP53': 'As a tumor suppressor, TP53 alterations may indicate sensitivity to DNA damage-inducing therapies.',
            'MYC': 'MYC amplification suggests potential targets for MYC inhibitors or CDK4/6 inhibitors.',
            'KRAS': 'KRAS mutations may predict resistance to EGFR inhibitors but sensitivity to MEK inhibitors.',
            'EGFR': 'EGFR overexpression suggests potential benefit from EGFR-targeted therapies.',
            'VEGFA': 'High VEGFA expression indicates potential response to anti-angiogenic therapies.',
            'PIK3CA': 'PIK3CA mutations may predict sensitivity to PI3K/mTOR pathway inhibitors.',
            'PTEN': 'PTEN loss may indicate sensitivity to PI3K pathway inhibitors.',
            'CTNNB1': 'CTNNB1 mutations suggest involvement of Wnt pathway and potential targeted approaches.'
        }
        
        base_info = gene_info.get(gene_name, 'This gene may serve as a potential therapeutic target.')
        
        # Add prognostic context
        significant_endpoints = []
        if results.get('os_analysis', {}).get('p_value', 1) < 0.05:
            significant_endpoints.append('overall survival')
        if results.get('rfs_analysis', {}).get('p_value', 1) < 0.05:
            significant_endpoints.append('recurrence-free survival')
        
        if significant_endpoints:
            context = f" The significant association with {' and '.join(significant_endpoints)} supports its potential as a biomarker for patient stratification."
        else:
            context = " Further validation may be needed to establish clinical utility."
        
        return base_info + context
    
    def run(self, debug=False, port=8050, host='0.0.0.0'):
        """Run the unified dashboard"""
        print(f"🚀 Starting Unified LIHC Dashboard...")
        print(f"✨ Open http://localhost:{port} in your browser")
        print(f"📊 Features: Multi-dimensional analysis, Network integration, Linchpin discovery")
        
        self.app.run(debug=debug, port=port, host=host)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified LIHC Analysis Dashboard")
    parser.add_argument("--port", type=int, default=8050, help="Port to run dashboard")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--results-dir", default="results", help="Results directory")
    
    args = parser.parse_args()
    
    dashboard = UnifiedLIHCDashboard(results_dir=args.results_dir)
    dashboard.run(debug=args.debug, port=args.port)

if __name__ == "__main__":
    main()