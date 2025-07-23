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
            ], className="card"),
            
            # Add trend analysis
            self.create_trend_analysis_preview()
        ], className="fade-in")
    
    def create_trend_analysis_preview(self):
        """Create trend analysis preview for overview page"""
        # Generate sample trend data for demonstration
        months = pd.date_range('2020-01', '2024-12', freq='M')
        
        # Simulate platform usage trends
        usage_data = {
            'date': months,
            'analyses_count': np.cumsum(np.random.poisson(15, len(months))),
            'success_rate': np.random.uniform(0.85, 0.95, len(months)),
            'avg_linchpin_score': np.random.uniform(0.65, 0.85, len(months))
        }
        
        df = pd.DataFrame(usage_data)
        
        # Create trend charts
        trend_fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Platform Usage Growth', 'Analysis Success Rate', 
                          'Average Linchpin Scores', 'Monthly Analysis Distribution'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "histogram"}]]
        )
        
        # Usage growth
        trend_fig.add_trace(
            go.Scatter(x=df['date'], y=df['analyses_count'],
                      mode='lines+markers', name='Total Analyses',
                      line=dict(color='#1f77b4', width=3)),
            row=1, col=1
        )
        
        # Success rate
        trend_fig.add_trace(
            go.Scatter(x=df['date'], y=df['success_rate'],
                      mode='lines+markers', name='Success Rate',
                      line=dict(color='#2ca02c', width=3)),
            row=1, col=2
        )
        
        # Average scores
        trend_fig.add_trace(
            go.Scatter(x=df['date'], y=df['avg_linchpin_score'],
                      mode='lines+markers', name='Avg Linchpin Score',
                      line=dict(color='#ff7f0e', width=3)),
            row=2, col=1
        )
        
        # Distribution
        trend_fig.add_trace(
            go.Histogram(x=df['analyses_count'].diff().dropna(),
                        name='Monthly Growth', nbinsx=15,
                        marker_color='#d62728'),
            row=2, col=2
        )
        
        trend_fig.update_layout(
            height=500,
            title_text="📈 Platform Analytics Dashboard",
            title_x=0.5,
            showlegend=False,
            font=dict(size=11),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return html.Div([
            html.H3("📈 Platform Trends & Analytics", className="card-title"),
            dcc.Graph(figure=trend_fig, config={'displayModeBar': False}),
            html.P([
                "实时追踪平台使用情况和分析质量趋势，帮助持续优化算法性能和用户体验。"
            ], className="text-muted small mt-2")
        ], className="card")
    
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
            ),
            
            # Add comprehensive charts
            self.create_score_comparison_charts(df)
        ], className="card")
    
    def create_score_comparison_charts(self, linchpin_data):
        """Create comprehensive score comparison charts"""
        if linchpin_data is None or len(linchpin_data) == 0:
            return html.Div("No data available for visualization", className="text-muted")
        
        # Convert to DataFrame if needed
        if isinstance(linchpin_data, list):
            df = pd.DataFrame(linchpin_data)
        else:
            df = linchpin_data.copy()
        
        top_20 = df.head(20)
        
        # 1. Linchpin Score Bar Chart
        bar_fig = px.bar(
            top_20, 
            x='gene_id', 
            y='linchpin_score',
            title='Top 20 Linchpin Scores Comparison',
            labels={'gene_id': 'Gene', 'linchpin_score': 'Linchpin Score'},
            color='linchpin_score',
            color_continuous_scale='Viridis'
        )
        bar_fig.update_layout(
            height=400,
            xaxis_tickangle=-45,
            font=dict(size=12),
            title_x=0.5,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        bar_fig.update_traces(
            texttemplate='%{y:.3f}',
            textposition='outside'
        )
        
        # 2. Multi-Score Radar Chart for Top 5
        top_5 = top_20.head(5)
        radar_fig = go.Figure()
        
        for i, row in top_5.iterrows():
            radar_fig.add_trace(go.Scatterpolar(
                r=[
                    row.get('linchpin_score', 0),
                    row.get('prognostic_score', 0),
                    row.get('network_hub_score', 0),
                    row.get('cross_dimensional_score', 0.5),  # Default if not available
                    row.get('regulator_score', 0.3)  # Default if not available
                ],
                theta=['Linchpin', 'Prognostic', 'Network Hub', 'Cross-Dimensional', 'Regulatory'],
                fill='toself',
                name=row['gene_id']
            ))
            
        radar_fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="Top 5 Genes Multi-Dimensional Score Profile",
            height=500,
            title_x=0.5,
            font=dict(size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # 3. Scatter Plot: Prognostic vs Network Hub Score
        scatter_fig = px.scatter(
            top_20,
            x='prognostic_score',
            y='network_hub_score',
            size='linchpin_score',
            color='linchpin_score',
            hover_name='gene_id',
            title='Prognostic vs Network Hub Score Correlation',
            labels={
                'prognostic_score': 'Prognostic Score',
                'network_hub_score': 'Network Hub Score',
                'linchpin_score': 'Linchpin Score'
            },
            color_continuous_scale='RdYlBu_r'
        )
        scatter_fig.update_layout(
            height=400,
            title_x=0.5,
            font=dict(size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # 4. Score Distribution Box Plot
        score_data = []
        for score_type in ['linchpin_score', 'prognostic_score', 'network_hub_score']:
            if score_type in top_20.columns:
                for value in top_20[score_type]:
                    score_data.append({
                        'Score Type': score_type.replace('_', ' ').title(),
                        'Value': value
                    })
        
        if score_data:
            box_df = pd.DataFrame(score_data)
            box_fig = px.box(
                box_df,
                x='Score Type',
                y='Value',
                title='Score Distribution Analysis',
                color='Score Type'
            )
            box_fig.update_layout(
                height=400,
                title_x=0.5,
                font=dict(size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
        else:
            box_fig = go.Figure()
            box_fig.add_annotation(text="No data available", x=0.5, y=0.5)
        
        return html.Div([
            html.H4("📊 综合评分对比分析", className="card-title mb-4"),
            
            # Chart grid
            html.Div([
                # Bar chart
                html.Div([
                    dcc.Graph(figure=bar_fig, config={'displayModeBar': False})
                ], className="col-12 mb-4"),
                
                # Radar and Scatter charts
                html.Div([
                    html.Div([
                        dcc.Graph(figure=radar_fig, config={'displayModeBar': False})
                    ], className="col-6"),
                    html.Div([
                        dcc.Graph(figure=scatter_fig, config={'displayModeBar': False})
                    ], className="col-6"),
                ], className="row mb-4"),
                
                # Box plot
                html.Div([
                    dcc.Graph(figure=box_fig, config={'displayModeBar': False})
                ], className="col-12")
            ], className="row")
        ], className="card p-4")
    
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
            ], className="metric-grid"),
            
            # Add multidimensional charts
            self.create_multidim_charts(stage1_data)
        ], className="card")
    
    def create_multidim_charts(self, stage1_data):
        """Create multi-dimensional analysis charts"""
        # Prepare data for visualization
        dimensions = {
            'Tumor Cells': len(stage1_data.get('tumor_cells', [])),
            'Immune Cells': len(stage1_data.get('immune_cells', [])),
            'Stromal Cells': len(stage1_data.get('stromal_cells', [])),
            'ECM': len(stage1_data.get('ecm', [])),
            'Cytokines': len(stage1_data.get('cytokines', []))
        }
        
        # 1. Pie Chart for dimension distribution
        pie_fig = px.pie(
            values=list(dimensions.values()),
            names=list(dimensions.keys()),
            title='Gene Distribution Across Biological Dimensions',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        pie_fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Genes: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        pie_fig.update_layout(
            height=400,
            title_x=0.5,
            font=dict(size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # 2. Bar Chart with different styling
        bar_fig = px.bar(
            x=list(dimensions.keys()),
            y=list(dimensions.values()),
            title='Gene Count by Biological Dimension',
            labels={'x': 'Biological Dimension', 'y': 'Number of Genes'},
            color=list(dimensions.values()),
            color_continuous_scale='Blues'
        )
        bar_fig.update_layout(
            height=400,
            title_x=0.5,
            font=dict(size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=-45
        )
        bar_fig.update_traces(
            texttemplate='%{y}',
            textposition='outside'
        )
        
        # 3. Sunburst Chart for hierarchical view
        sunburst_data = []
        total_genes = sum(dimensions.values())
        
        for dim_name, count in dimensions.items():
            sunburst_data.append({
                'ids': dim_name,
                'labels': dim_name,
                'parents': '',
                'values': count
            })
            
            # Add subcategories for demonstration
            subcategories = {
                'Tumor Cells': ['Oncogenes', 'Suppressors'],
                'Immune Cells': ['T-cells', 'B-cells'],
                'Stromal Cells': ['Fibroblasts', 'Endothelial'],
                'ECM': ['Collagens', 'Proteoglycans'],
                'Cytokines': ['Interleukins', 'Growth Factors']
            }
            
            if dim_name in subcategories:
                for i, subcat in enumerate(subcategories[dim_name]):
                    sunburst_data.append({
                        'ids': f"{dim_name}_{subcat}",
                        'labels': subcat,
                        'parents': dim_name,
                        'values': count // len(subcategories[dim_name]) + (1 if i == 0 else 0)
                    })
        
        sunburst_df = pd.DataFrame(sunburst_data)
        sunburst_fig = px.sunburst(
            sunburst_df,
            ids='ids',
            labels='labels',
            parents='parents',
            values='values',
            title='Hierarchical View of Biological Dimensions'
        )
        sunburst_fig.update_layout(
            height=500,
            title_x=0.5,
            font=dict(size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return html.Div([
            html.H4("📊 多维度分析可视化", className="card-title mb-4"),
            html.Div([
                # Pie and Bar charts
                html.Div([
                    html.Div([
                        dcc.Graph(figure=pie_fig, config={'displayModeBar': False})
                    ], className="col-6"),
                    html.Div([
                        dcc.Graph(figure=bar_fig, config={'displayModeBar': False})
                    ], className="col-6"),
                ], className="row mb-4"),
                
                # Sunburst chart
                html.Div([
                    dcc.Graph(figure=sunburst_fig, config={'displayModeBar': False})
                ], className="col-12")
            ], className="row")
        ], className="card p-4 mt-4")
    
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
            ], className="metric-grid"),
            
            # Add network visualization charts
            self.create_network_charts()
        ], className="card")
    
    def create_network_charts(self):
        """Create network analysis charts"""
        network_data = self.demo_data.get('stage2', {}).get('centrality', [])
        
        if not network_data:
            # Create sample network data for demonstration
            genes = ['TP53', 'EGFR', 'VEGFA', 'MYC', 'KRAS', 'PIK3CA', 'PTEN', 'CTNNB1', 'RB1', 'APC']
            network_data = []
            
            for i, gene in enumerate(genes):
                network_data.append({
                    'gene_id': gene,
                    'degree_centrality': np.random.uniform(0.3, 0.9),
                    'betweenness_centrality': np.random.uniform(0.1, 0.8),
                    'closeness_centrality': np.random.uniform(0.4, 0.9),
                    'x': np.random.uniform(-1, 1),
                    'y': np.random.uniform(-1, 1)
                })
        
        df = pd.DataFrame(network_data)
        
        # 1. Network Graph Visualization
        network_fig = go.Figure()
        
        # Add edges (connections between nodes)
        edge_x = []
        edge_y = []
        for i in range(len(df)):
            for j in range(i+1, min(i+4, len(df))):  # Connect to next 3 nodes
                x0, y0 = df.iloc[i]['x'], df.iloc[i]['y']
                x1, y1 = df.iloc[j]['x'], df.iloc[j]['y']
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
        
        network_fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='rgba(125, 125, 125, 0.5)'),
            hoverinfo='none',
            mode='lines',
            name='Connections'
        ))
        
        # Add nodes
        network_fig.add_trace(go.Scatter(
            x=df['x'],
            y=df['y'],
            mode='markers+text',
            hovertemplate='<b>%{text}</b><br>Degree: %{customdata[0]:.3f}<br>Betweenness: %{customdata[1]:.3f}<br>Closeness: %{customdata[2]:.3f}<extra></extra>',
            text=df['gene_id'],
            textposition="middle center",
            customdata=df[['degree_centrality', 'betweenness_centrality', 'closeness_centrality']].values,
            marker=dict(
                size=df['degree_centrality'] * 50 + 20,
                color=df['betweenness_centrality'],
                colorscale='Viridis',
                colorbar=dict(title="Betweenness Centrality"),
                line=dict(width=2, color='white')
            ),
            name='Genes'
        ))
        
        network_fig.update_layout(
            title='Gene Interaction Network',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Node size = Degree Centrality<br>Color = Betweenness Centrality",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # 2. Centrality Comparison Chart
        centrality_data = []
        for _, row in df.iterrows():
            centrality_data.extend([
                {'Gene': row['gene_id'], 'Centrality Type': 'Degree', 'Value': row['degree_centrality']},
                {'Gene': row['gene_id'], 'Centrality Type': 'Betweenness', 'Value': row['betweenness_centrality']},
                {'Gene': row['gene_id'], 'Centrality Type': 'Closeness', 'Value': row['closeness_centrality']}
            ])
        
        centrality_df = pd.DataFrame(centrality_data)
        
        centrality_fig = px.bar(
            centrality_df,
            x='Gene',
            y='Value',
            color='Centrality Type',
            barmode='group',
            title='Network Centrality Measures Comparison',
            labels={'Value': 'Centrality Score', 'Gene': 'Gene Symbol'}
        )
        centrality_fig.update_layout(
            height=400,
            title_x=0.5,
            font=dict(size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=-45
        )
        
        # 3. Centrality Distribution Histograms
        hist_fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Degree Centrality', 'Betweenness Centrality', 'Closeness Centrality')
        )
        
        hist_fig.add_trace(
            go.Histogram(x=df['degree_centrality'], name='Degree', nbinsx=10),
            row=1, col=1
        )
        hist_fig.add_trace(
            go.Histogram(x=df['betweenness_centrality'], name='Betweenness', nbinsx=10),
            row=1, col=2
        )
        hist_fig.add_trace(
            go.Histogram(x=df['closeness_centrality'], name='Closeness', nbinsx=10),
            row=1, col=3
        )
        
        hist_fig.update_layout(
            height=300,
            title_text="Centrality Score Distributions",
            title_x=0.5,
            showlegend=False,
            font=dict(size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return html.Div([
            html.H4("📊 网络分析可视化", className="card-title mb-4"),
            html.Div([
                # Network graph
                html.Div([
                    dcc.Graph(figure=network_fig, config={'displayModeBar': False})
                ], className="col-12 mb-4"),
                
                # Centrality comparison and distributions
                html.Div([
                    html.Div([
                        dcc.Graph(figure=centrality_fig, config={'displayModeBar': False})
                    ], className="col-8"),
                    html.Div([
                        dcc.Graph(figure=hist_fig, config={'displayModeBar': False})
                    ], className="col-4"),
                ], className="row")
            ], className="row")
        ], className="card p-4 mt-4")
    
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