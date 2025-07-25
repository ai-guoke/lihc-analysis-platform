"""
Enhanced Platform Integration
增强平台集成 - 整合所有高级功能，提供完整的用户体验
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context, no_update
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

# Import our enhanced components
from .interactive_charts import chart_enhancer, InteractiveChartEnhancer
from .chart_callbacks import register_chart_callbacks
from .smart_recommendations import recommendation_engine, AnalysisRecommendation
from .advanced_visualizations import bio_visualizer, AdvancedBioVisualizer
from .user_guidance import guidance_system, UserGuidanceSystem

class EnhancedPlatformIntegrator:
    """增强平台集成器 - 统一管理所有高级功能"""
    
    def __init__(self, app: dash.Dash, dataset_manager=None):
        self.app = app
        self.dataset_manager = dataset_manager
        self.chart_enhancer = chart_enhancer
        self.recommendation_engine = recommendation_engine
        self.bio_visualizer = bio_visualizer
        self.guidance_system = guidance_system
        
        # Integration state
        self.user_sessions = {}
        self.active_recommendations = {}
        self.chart_interactions = {}
        
        # Initialize enhanced features
        self._initialize_enhanced_platform()
    
    def _initialize_enhanced_platform(self):
        """初始化增强平台功能"""
        
        # Register chart interaction callbacks
        register_chart_callbacks(self.app)
        
        # Register recommendation callbacks
        self._register_recommendation_callbacks()
        
        # Register guidance callbacks
        self._register_guidance_callbacks()
        
        # Register platform integration callbacks
        self._register_integration_callbacks()
    
    def create_enhanced_dashboard_layout(self) -> html.Div:
        """创建增强的仪表盘布局"""
        
        return html.Div([
            # Enhanced header with recommendations
            self._create_enhanced_header(),
            
            # Smart recommendation panel
            self._create_smart_recommendation_panel(),
            
            # Enhanced main content area
            html.Div([
                # Sidebar with enhanced navigation
                self._create_enhanced_sidebar(),
                
                # Main content with chart enhancements
                html.Div([
                    # Context-aware help bar
                    self._create_context_help_bar(),
                    
                    # Main analysis content
                    html.Div(id='enhanced-main-content'),
                    
                    # Chart interaction panel
                    self._create_chart_interaction_panel()
                ], className="enhanced-main-content")
            ], className="enhanced-dashboard-body"),
            
            # User guidance components
            self.guidance_system.create_help_panel(),
            self.guidance_system.create_smart_assistant(),
            
            # Tutorial overlays
            html.Div(id='tutorial-overlays'),
            
            # Global stores and state management
            self._create_global_stores(),
            
            # Performance monitoring
            self._create_performance_monitor()
            
        ], className="enhanced-lihc-platform")
    
    def _create_enhanced_header(self) -> html.Div:
        """创建增强的头部"""
        
        return html.Div([
            # Main header
            html.Div([
                html.H1([
                    html.I(className="fas fa-dna", style={'marginRight': '15px', 'color': '#3498db'}),
                    "LIHC Analysis Platform",
                    html.Span("Pro", className="platform-version-badge")
                ], className="platform-title"),
                
                # Real-time system status
                html.Div([
                    html.Div(id='system-status-indicator'),
                    html.Div(id='active-analyses-count'),
                    html.Div(id='recommendation-badge')
                ], className="header-status-bar")
            ], className="main-header"),
            
            # Smart action bar
            html.Div([
                html.Div([
                    html.Button([
                        html.I(className="fas fa-magic"),
                        " 智能推荐"
                    ], id="toggle-recommendations", className="btn btn-primary",
                       style={'marginRight': '10px'}),
                    
                    html.Button([
                        html.I(className="fas fa-chart-line"),
                        " 高级图表"
                    ], id="toggle-advanced-charts", className="btn btn-info",
                       style={'marginRight': '10px'}),
                    
                    html.Button([
                        html.I(className="fas fa-graduation-cap"),
                        " 新手教程"
                    ], id="start-tutorial", className="btn btn-success",
                       style={'marginRight': '10px'}),
                    
                    html.Button([
                        html.I(className="fas fa-cog"),
                        " 个性化设置"
                    ], id="open-preferences", className="btn btn-outline-secondary")
                ], className="action-buttons"),
                
                # Quick access to recent analyses
                html.Div(id='recent-analyses-dropdown')
            ], className="smart-action-bar")
            
        ], className="enhanced-header")
    
    def _create_smart_recommendation_panel(self) -> html.Div:
        """创建智能推荐面板"""
        
        return html.Div([
            html.Div([
                html.Div([
                    html.H4([
                        html.I(className="fas fa-lightbulb", style={'marginRight': '10px'}),
                        "智能分析推荐"
                    ], style={'margin': '0', 'color': '#2c3e50'}),
                    
                    html.Button("×", id="close-recommendations", 
                              style={'background': 'none', 'border': 'none', 
                                     'fontSize': '20px', 'cursor': 'pointer', 'float': 'right'})
                ], style={'marginBottom': '20px', 'borderBottom': '1px solid #ecf0f1', 'paddingBottom': '10px'}),
                
                # Recommendation cards
                html.Div(id='recommendation-cards'),
                
                # Workflow suggestion
                html.Div([
                    html.H5([
                        html.I(className="fas fa-route", style={'marginRight': '8px'}),
                        "建议分析流程"
                    ]),
                    html.Div(id='workflow-suggestion')
                ], style={'marginTop': '20px', 'padding': '15px', 
                         'backgroundColor': '#f8f9fa', 'borderRadius': '8px'})
                
            ], style={'backgroundColor': 'white', 'padding': '25px', 
                     'borderRadius': '10px', 'boxShadow': '0 4px 15px rgba(0,0,0,0.1)',
                     'maxHeight': '80vh', 'overflowY': 'auto'})
        ], id="recommendation-panel", className="recommendation-panel",
           style={'display': 'none', 'position': 'fixed', 'top': '100px', 
                 'right': '20px', 'width': '400px', 'zIndex': '1000'})
    
    def _create_enhanced_sidebar(self) -> html.Div:
        """创建增强的侧边栏"""
        
        return html.Div([
            # Analysis categories with smart badges
            html.Div([
                html.H6("📊 基础分析", className="sidebar-category"),
                self._create_enhanced_nav_item("overview", "数据概览", "fas fa-chart-pie", badges=['智能']),
                self._create_enhanced_nav_item("multidim", "多维度分析", "fas fa-cube", badges=['推荐']),
                self._create_enhanced_nav_item("survival", "生存分析", "fas fa-heartbeat", badges=['高级']),
            ], className="sidebar-section"),
            
            html.Div([
                html.H6("🔬 高级分析", className="sidebar-category"),
                self._create_enhanced_nav_item("network", "网络分析", "fas fa-project-diagram", badges=['AI增强']),
                self._create_enhanced_nav_item("immune", "免疫分析", "fas fa-shield-alt", badges=['精准医学']),
                self._create_enhanced_nav_item("drug", "药物分析", "fas fa-pills", badges=['个性化']),
            ], className="sidebar-section"),
            
            html.Div([
                html.H6("🚀 平台功能", className="sidebar-category"),
                self._create_enhanced_nav_item("batch", "批量处理", "fas fa-layer-group", badges=['企业级']),
                self._create_enhanced_nav_item("taskqueue", "任务队列", "fas fa-tasks", badges=['实时']),
                self._create_enhanced_nav_item("history", "分析历史", "fas fa-history"),
            ], className="sidebar-section"),
            
            # Quick insights panel
            html.Div([
                html.H6("💡 实时洞察", className="sidebar-category"),
                html.Div(id='quick-insights-panel')
            ], className="sidebar-section quick-insights")
            
        ], className="enhanced-sidebar")
    
    def _create_enhanced_nav_item(self, item_id: str, title: str, icon: str, badges: List[str] = None) -> html.Div:
        """创建增强的导航项"""
        
        badges_html = []
        if badges:
            for badge in badges:
                badge_color = {
                    '智能': 'primary', '推荐': 'success', '高级': 'warning',
                    'AI增强': 'info', '精准医学': 'danger', '个性化': 'secondary',
                    '企业级': 'dark', '实时': 'success'
                }.get(badge, 'secondary')
                
                badges_html.append(
                    html.Span(badge, className=f"badge badge-{badge_color} nav-badge",
                             style={'marginLeft': '5px', 'fontSize': '0.6rem'})
                )
        
        return html.Div([
            html.I(className=icon, style={'marginRight': '10px', 'width': '20px'}),
            html.Span(title),
            html.Div(badges_html, style={'marginLeft': 'auto'})
        ], id=f"enhanced-nav-{item_id}", className="enhanced-nav-item",
           style={'display': 'flex', 'alignItems': 'center'})
    
    def _create_context_help_bar(self) -> html.Div:
        """创建上下文帮助栏"""
        
        return html.Div([
            html.Div([
                html.I(className="fas fa-info-circle", style={'marginRight': '8px'}),
                html.Span(id='context-help-text', children="选择分析功能开始您的研究")
            ], className="help-text"),
            
            html.Div([
                html.Button([
                    html.I(className="fas fa-question"),
                    " 帮助"
                ], id="context-help-btn", className="btn btn-sm btn-outline-info",
                   style={'marginRight': '5px'}),
                
                html.Button([
                    html.I(className="fas fa-video"),
                    " 视频教程"
                ], id="video-tutorial-btn", className="btn btn-sm btn-outline-success")
            ], className="help-actions")
            
        ], id="context-help-bar", className="context-help-bar",
           style={'display': 'flex', 'justifyContent': 'space-between', 
                 'alignItems': 'center', 'padding': '10px', 
                 'backgroundColor': '#e3f2fd', 'borderRadius': '5px', 
                 'marginBottom': '20px'})
    
    def _create_chart_interaction_panel(self) -> html.Div:
        """创建图表交互面板"""
        
        return html.Div([
            html.Div([
                html.H5([
                    html.I(className="fas fa-mouse-pointer", style={'marginRight': '8px'}),
                    "图表交互工具"
                ]),
                
                # Chart tools
                html.Div([
                    html.Button([
                        html.I(className="fas fa-search-plus"),
                        " 缩放"
                    ], id="chart-zoom-tool", className="btn btn-sm btn-outline-primary",
                       style={'marginRight': '5px', 'marginBottom': '5px'}),
                    
                    html.Button([
                        html.I(className="fas fa-hand-paper"),
                        " 选择"
                    ], id="chart-select-tool", className="btn btn-sm btn-outline-success",
                       style={'marginRight': '5px', 'marginBottom': '5px'}),
                    
                    html.Button([
                        html.I(className="fas fa-download"),
                        " 导出"
                    ], id="chart-export-tool", className="btn btn-sm btn-outline-info",
                       style={'marginRight': '5px', 'marginBottom': '5px'}),
                    
                    html.Button([
                        html.I(className="fas fa-link"),
                        " 联动"
                    ], id="chart-crossfilter-tool", className="btn btn-sm btn-outline-warning",
                       style={'marginBottom': '5px'})
                ], className="chart-tools"),
                
                # Selection statistics
                html.Div([
                    html.H6("选中数据统计", style={'marginTop': '15px'}),
                    html.Div(id='global-selection-stats')
                ]),
                
                # Crossfilter status
                html.Div([
                    html.H6("交叉筛选状态", style={'marginTop': '15px'}),
                    html.Div(id='crossfilter-status')
                ])
                
            ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 
                     'borderRadius': '8px', 'border': '1px solid #dee2e6'})
        ], id="chart-interaction-panel", className="chart-interaction-panel",
           style={'display': 'none', 'position': 'fixed', 'top': '50%', 
                 'left': '20px', 'transform': 'translateY(-50%)', 
                 'width': '280px', 'zIndex': '999'})
    
    def _create_global_stores(self) -> html.Div:
        """创建全局状态存储"""
        
        return html.Div([
            # User session and preferences
            dcc.Store(id='user-session', data={}),
            dcc.Store(id='user-preferences', data={'complexity_level': 'intermediate'}),
            
            # Analysis state
            dcc.Store(id='current-analysis-state', data={}),
            dcc.Store(id='recommendation-state', data={}),
            
            # Chart interaction state
            dcc.Store(id='chart-selection-state', data={}),
            dcc.Store(id='crossfilter-state', data={'enabled': False}),
            
            # Platform state
            dcc.Store(id='platform-state', data={'enhanced_mode': True}),
            
            # Performance metrics
            dcc.Store(id='performance-metrics', data={}),
            
            # Hidden download components
            dcc.Download(id='enhanced-download')
        ])
    
    def _create_performance_monitor(self) -> html.Div:
        """创建性能监控"""
        
        return html.Div([
            # Performance indicator
            html.Div([
                html.I(className="fas fa-tachometer-alt", 
                      style={'marginRight': '5px'}),
                html.Span(id='performance-indicator', children="系统正常")
            ], id="performance-status", className="performance-status",
               style={'position': 'fixed', 'bottom': '20px', 'left': '20px', 
                     'padding': '8px 12px', 'backgroundColor': '#28a745', 
                     'color': 'white', 'borderRadius': '20px', 'fontSize': '0.8rem',
                     'zIndex': '1000'}),
            
            # Performance interval
            dcc.Interval(
                id='performance-interval',
                interval=5000,  # 5 seconds
                n_intervals=0
            )
        ])
    
    def _register_recommendation_callbacks(self):
        """注册推荐系统回调"""
        
        @self.app.callback(
            [Output('recommendation-cards', 'children'),
             Output('workflow-suggestion', 'children')],
            [Input('user-session', 'data'),
             Input('current-analysis-state', 'data')],
            prevent_initial_call=True
        )
        def update_recommendations(user_session, analysis_state):
            """更新智能推荐"""
            
            if not self.dataset_manager:
                return [], []
            
            # Get current dataset info
            current_dataset = self.dataset_manager.get_current_dataset()
            if not current_dataset:
                return [], []
            
            dataset_info = {
                'samples': current_dataset.samples,
                'genes': current_dataset.genes,
                'features': current_dataset.features
            }
            
            # Generate recommendations
            recommendations = self.recommendation_engine.generate_recommendations(
                dataset_info, 
                user_session.get('preferences', {}),
                analysis_state.get('history', [])
            )
            
            # Create recommendation cards
            cards = []
            for rec in recommendations[:4]:  # Show top 4
                card = self._create_recommendation_card(rec)
                cards.append(card)
            
            # Generate workflow suggestion
            workflow = self.recommendation_engine.get_analysis_workflow_suggestion(recommendations)
            workflow_content = self._create_workflow_suggestion(workflow)
            
            return cards, workflow_content
        
        @self.app.callback(
            Output('recommendation-panel', 'style'),
            [Input('toggle-recommendations', 'n_clicks'),
             Input('close-recommendations', 'n_clicks')],
            [State('recommendation-panel', 'style')],
            prevent_initial_call=True
        )
        def toggle_recommendation_panel(show_clicks, close_clicks, current_style):
            """切换推荐面板显示"""
            
            ctx = callback_context
            if not ctx.triggered:
                return no_update
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'toggle-recommendations':
                current_style['display'] = 'block'
            elif button_id == 'close-recommendations':
                current_style['display'] = 'none'
            
            return current_style
    
    def _register_guidance_callbacks(self):
        """注册导航系统回调"""
        
        @self.app.callback(
            Output('context-help-text', 'children'),
            [Input('url', 'pathname'),
             Input('current-analysis-state', 'data')],
            prevent_initial_call=True
        )
        def update_context_help(pathname, analysis_state):
            """更新上下文帮助"""
            
            current_page = pathname.split('/')[-1] if pathname else 'overview'
            tips = self.guidance_system.get_contextual_tips(current_page, analysis_state)
            
            if tips:
                return tips[0]  # Show first tip
            else:
                return "选择分析功能开始您的研究"
    
    def _register_integration_callbacks(self):
        """注册集成回调"""
        
        @self.app.callback(
            Output('system-status-indicator', 'children'),
            [Input('performance-interval', 'n_intervals')],
            prevent_initial_call=True
        )
        def update_system_status(n_intervals):
            """更新系统状态"""
            
            # 简化的系统状态检查
            status_color = '#28a745'  # Green for normal
            status_text = "系统正常"
            
            return html.Div([
                html.I(className="fas fa-circle", 
                      style={'color': status_color, 'marginRight': '5px'}),
                html.Span(status_text)
            ], style={'fontSize': '0.8rem', 'color': '#666'})
    
    def _create_recommendation_card(self, recommendation: AnalysisRecommendation) -> html.Div:
        """创建推荐卡片"""
        
        confidence_color = {
            5: '#28a745', 4: '#17a2b8', 3: '#ffc107', 2: '#fd7e14', 1: '#dc3545'
        }.get(recommendation.priority, '#6c757d')
        
        return html.Div([
            html.Div([
                html.H6(recommendation.analysis_type.replace('_', ' ').title(), 
                       style={'margin': '0', 'color': '#2c3e50'}),
                html.Span(f"{recommendation.confidence:.0%}", 
                         className="confidence-badge",
                         style={'backgroundColor': confidence_color, 'color': 'white',
                               'padding': '2px 8px', 'borderRadius': '12px', 
                               'fontSize': '0.7rem', 'float': 'right'})
            ], style={'marginBottom': '10px'}),
            
            html.P(recommendation.description, 
                  style={'fontSize': '0.85rem', 'color': '#666', 'marginBottom': '10px'}),
            
            html.Div([
                html.Small([
                    html.I(className="fas fa-clock", style={'marginRight': '3px'}),
                    recommendation.estimated_time
                ], style={'marginRight': '15px'}),
                html.Small([
                    html.I(className="fas fa-star", style={'marginRight': '3px'}),
                    recommendation.complexity
                ])
            ], style={'marginBottom': '10px'}),
            
            html.Button([
                html.I(className="fas fa-play"),
                " 开始分析"
            ], id=f"start-{recommendation.analysis_type}", 
               className="btn btn-sm btn-primary",
               style={'width': '100%'})
            
        ], className="recommendation-card",
           style={'padding': '15px', 'border': '1px solid #dee2e6', 
                 'borderRadius': '8px', 'marginBottom': '15px',
                 'backgroundColor': 'white'})
    
    def _create_workflow_suggestion(self, workflow: Dict) -> List:
        """创建工作流程建议"""
        
        if not workflow.get('recommended_order'):
            return [html.P("暂无工作流程建议")]
        
        steps = []
        for i, analysis_type in enumerate(workflow['recommended_order']):
            steps.append(html.Div([
                html.Span(f"{i+1}.", className="workflow-step-number"),
                html.Span(analysis_type.replace('_', ' ').title())
            ], className="workflow-step"))
        
        return [
            html.P(f"⏱️ 预计总时间: {workflow.get('total_estimated_time', '未知')}"),
            html.Div(steps),
            html.Button([
                html.I(className="fas fa-rocket"),
                " 执行工作流程"
            ], id="execute-workflow", className="btn btn-success btn-sm",
               style={'marginTop': '10px', 'width': '100%'})
        ]

# Factory function for easy integration
def create_enhanced_platform(app: dash.Dash, dataset_manager=None) -> EnhancedPlatformIntegrator:
    """创建增强平台集成器"""
    return EnhancedPlatformIntegrator(app, dataset_manager)