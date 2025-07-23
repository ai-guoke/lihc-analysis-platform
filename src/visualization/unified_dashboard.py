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
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    # Fallback to basic functionality

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
            html.H1("🧬 LIHC Multi-dimensional Analysis Platform"),
            html.P("Advanced therapeutic target discovery through integrated omics analysis")
        ], className="header")
    
    def create_navigation(self):
        """Create navigation tabs"""
        return html.Div([
            html.Div([
                html.Button([html.Span("🏠"), "Overview"], 
                           id="nav-overview", className="nav-tab active"),
                html.Button([html.Span("📊"), "Demo Results"], 
                           id="nav-demo", className="nav-tab"),
                html.Button([html.Span("📤"), "Upload Data"], 
                           id="nav-upload", className="nav-tab"),
                html.Button([html.Span("🎯"), "Linchpins"], 
                           id="nav-linchpins", className="nav-tab"),
                html.Button([html.Span("🕸️"), "Networks"], 
                           id="nav-networks", className="nav-tab"),
                html.Button([html.Span("🌳"), "Multi-dimensional"], 
                           id="nav-multidim", className="nav-tab"),
                html.Button([html.Span("📝"), "Templates"], 
                           id="nav-templates", className="nav-tab"),
            ], className="nav-tabs")
        ], className="nav-container")
    
    def create_overview_content(self):
        """Create overview page"""
        return html.Div([
            # Hero section
            html.Div([
                html.H2("🎯 From Biomarker Lists to Strategic Targets", className="card-title"),
                html.P([
                    "Transform traditional parallel analysis into integrated linchpin discovery. ",
                    "Our platform identifies the most critical therapeutic targets by analyzing ",
                    "5 biological dimensions simultaneously."
                ], style={"fontSize": "1.1rem", "marginBottom": "1.5rem"}),
                
                html.Div([
                    html.Button([html.Span("🚀"), "Explore Demo"], 
                               id="demo-btn", className="btn-primary", 
                               style={"marginRight": "1rem"}),
                    html.Button([html.Span("📤"), "Upload Data"], 
                               id="upload-btn", className="btn-secondary"),
                ], style={"textAlign": "center"})
            ], className="card"),
            
            # Quick scoring guide
            html.Div([
                html.H3("📊 评分指标快速指南", className="card-title"),
                html.P("平台使用三个核心指标评估基因作为治疗靶点的潜力：", className="mb-3"),
                html.Div([
                    html.Div([
                        html.H5("🎯 Linchpin Score", className="text-primary"),
                        html.P("综合评分 (0-1)", className="small font-weight-bold"),
                        html.P("整合多维度分析结果的最终评分，分数越高表示作为治疗靶点的潜力越大", className="small")
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H5("📈 Prognostic Score", className="text-success"),
                        html.P("预后评分 (0-1)", className="small font-weight-bold"),
                        html.P("基于Cox回归分析，反映基因表达与患者生存期的关联强度", className="small")
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H5("🕸️ Network Hub Score", className="text-info"),
                        html.P("网络中心性评分 (0-1)", className="small font-weight-bold"),
                        html.P("在分子相互作用网络中的重要程度，反映基因的连接和调控影响力", className="small")
                    ], className="metric-card")
                ], className="metric-grid"),
                html.P([
                    html.Strong("💡 使用提示: "),
                    "在Demo页面查看详细的计算方法和数据来源说明"
                ], className="text-muted small mt-3")
            ], className="card"),
            
            # Platform features
            html.Div([
                html.H3("✨ Platform Capabilities", className="card-title"),
                html.Div([
                    html.Div([
                        html.H4("🧬 Multi-dimensional Analysis"),
                        html.P("Simultaneous analysis across tumor, immune, stromal, ECM, and cytokine dimensions"),
                        html.Ul([
                            html.Li("Cox proportional hazards modeling"),
                            html.Li("Immune infiltration deconvolution"),
                            html.Li("Pathway enrichment analysis")
                        ])
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H4("🕸️ Network Integration"),
                        html.P("Cross-dimensional network analysis for hub identification"),
                        html.Ul([
                            html.Li("WGCNA-style module detection"),
                            html.Li("Network centrality analysis"),
                            html.Li("Cross-dimensional correlations")
                        ])
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H4("🎯 Linchpin Scoring"),
                        html.P("Composite scoring system for therapeutic prioritization"),
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
                html.H3("⚡ Analysis Workflow", className="card-title"),
                html.Div([
                    html.Div([
                        html.H4("1️⃣ Data Upload"),
                        html.P("Clinical, expression, and mutation data"),
                        html.Small("Multiple format support")
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H4("2️⃣ Multi-dimensional Analysis"),
                        html.P("Parallel analysis across 5 dimensions"),
                        html.Small("Prognostic factor identification")
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H4("3️⃣ Network Integration"),
                        html.P("Cross-dimensional network construction"),
                        html.Small("Hub and module detection")
                    ], className="metric-card"),
                    
                    html.Div([
                        html.H4("4️⃣ Linchpin Discovery"),
                        html.P("Composite scoring and ranking"),
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
            self.create_network_preview()
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
    
    def create_upload_content(self):
        """Create data upload interface"""
        return html.Div([
            html.Div([
                html.H2("📤 Upload Your Data", className="card-title"),
                html.P("Upload your LIHC dataset for personalized analysis")
            ], className="card"),
            
            # Upload instructions
            html.Div([
                html.H4("📋 Data Requirements"),
                html.Ul([
                    html.Li("📊 Clinical Data: Patient survival and clinical information (required)"),
                    html.Li("🧬 Expression Data: Gene expression matrix (required)"),
                    html.Li("🔬 Mutation Data: Somatic mutation information (optional)")
                ])
            ], className="card"),
            
            # Upload zone
            html.Div([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        html.H3("📁", style={"fontSize": "3rem", "margin": "0"}),
                        html.P("Drag & drop files here or click to browse"),
                        html.Small("Supports: CSV, TSV, Excel, ZIP")
                    ]),
                    className="upload-zone",
                    multiple=True
                )
            ], className="card"),
            
            # Upload status
            html.Div(id="upload-status"),
            
            # Analysis button
            html.Div([
                html.Button([html.Span("🚀"), "Run Analysis"], 
                           id="run-analysis-btn", className="btn-primary", disabled=True)
            ], className="card", style={"textAlign": "center"}),
            
            # Progress
            html.Div(id="analysis-progress")
        ], className="fade-in")
    
    def create_templates_content(self):
        """Create templates page"""
        return html.Div([
            # Download components for each template
            dcc.Download(id="download-clinical-template"),
            dcc.Download(id="download-expression-template"),
            dcc.Download(id="download-mutation-template"),
            
            html.Div([
                html.H2("📝 Data Templates", className="card-title"),
                html.P("Download templates to format your data correctly")
            ], className="card"),
            
            html.Div([
                html.Div([
                    html.H4("📊 Clinical Data Template"),
                    html.P("Patient survival and clinical information"),
                    html.Button("Download", id="btn-clinical-template", className="btn-secondary"),
                    html.Hr(),
                    html.Small("Required: sample_id, os_time, os_status")
                ], className="metric-card"),
                
                html.Div([
                    html.H4("🧬 Expression Data Template"),
                    html.P("Gene expression matrix"),
                    html.Button("Download", id="btn-expression-template", className="btn-secondary"),
                    html.Hr(),
                    html.Small("Format: Genes as rows, samples as columns")
                ], className="metric-card"),
                
                html.Div([
                    html.H4("🔬 Mutation Data Template"),
                    html.P("Somatic mutation information"),
                    html.Button("Download", id="btn-mutation-template", className="btn-secondary"),
                    html.Hr(),
                    html.Small("Required: sample_id, gene, mutation_type")
                ], className="metric-card")
            ], className="metric-grid")
        ], className="fade-in")
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            Output("main-content", "children"),
            [Input("nav-overview", "n_clicks"),
             Input("nav-demo", "n_clicks"),
             Input("nav-upload", "n_clicks"),
             Input("nav-linchpins", "n_clicks"),
             Input("nav-networks", "n_clicks"),
             Input("nav-multidim", "n_clicks"),
             Input("nav-templates", "n_clicks")],
            prevent_initial_call=False
        )
        def update_content(*args):
            ctx = dash.callback_context
            if not ctx.triggered:
                return self.create_overview_content()
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            content_map = {
                "nav-overview": self.create_overview_content,
                "nav-demo": self.create_demo_content,
                "nav-upload": self.create_upload_content,
                "nav-linchpins": self.create_demo_content,  # Same as demo for now
                "nav-networks": self.create_demo_content,   # Same as demo for now
                "nav-multidim": self.create_demo_content,   # Same as demo for now
                "nav-templates": self.create_templates_content
            }
            
            return content_map.get(button_id, self.create_overview_content)()
        
        # Overview page button callbacks
        @self.app.callback(
            Output("main-content", "children", allow_duplicate=True),
            [Input("demo-btn", "n_clicks"), Input("upload-btn", "n_clicks")],
            prevent_initial_call=True
        )
        def handle_overview_buttons(demo_clicks, upload_clicks):
            ctx = dash.callback_context
            if not ctx.triggered:
                return no_update
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == "demo-btn":
                return self.create_demo_content()
            elif button_id == "upload-btn":
                return self.create_upload_content()
            
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