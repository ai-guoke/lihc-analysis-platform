"""
User Guidance and Help System
用户导航和帮助系统 - 提供智能向导和上下文帮助
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TutorialStep:
    """教程步骤"""
    id: str
    title: str
    description: str
    target_element: str
    position: str = 'bottom'  # top, bottom, left, right
    action: str = None  # click, hover, input
    validation: str = None
    next_condition: str = None

@dataclass
class HelpContext:
    """帮助上下文"""
    page: str
    section: str
    user_level: str  # beginner, intermediate, advanced
    data_context: Dict
    analysis_context: Dict

class UserGuidanceSystem:
    """用户导航系统"""
    
    def __init__(self):
        self.tutorials = self._initialize_tutorials()
        self.help_content = self._initialize_help_content()
        self.user_progress = {}
        self.contextual_tips = self._initialize_contextual_tips()
        
    def _initialize_tutorials(self) -> Dict[str, List[TutorialStep]]:
        """初始化教程"""
        return {
            'first_time_user': [
                TutorialStep(
                    id='welcome',
                    title='欢迎使用LIHC分析平台',
                    description='这是一个专业的肝癌多组学数据分析平台。让我们一起开始您的第一次分析之旅！',
                    target_element='body',
                    position='center'
                ),
                TutorialStep(
                    id='navigation',
                    title='导航栏介绍',
                    description='顶部导航栏包含主要功能：数据上传、数据集管理、演示数据和系统设置。',
                    target_element='.top-nav',
                    position='bottom'
                ),
                TutorialStep(
                    id='sidebar',
                    title='分析功能菜单',
                    description='左侧菜单提供了所有分析功能，从基础的概览到高级的精准医学分析。',
                    target_element='.sidebar',
                    position='right'
                ),
                TutorialStep(
                    id='demo_data',
                    title='从演示数据开始',
                    description='建议先使用演示数据熟悉平台功能，然后再上传您自己的数据。',
                    target_element='#top-nav-demo',
                    position='bottom',
                    action='click'
                ),
                TutorialStep(
                    id='first_analysis',
                    title='开始第一个分析',
                    description='点击"多维度分析"开始您的第一个分析。这是了解数据特征的最佳起点。',
                    target_element='#sidebar-multidim',
                    position='right',
                    action='click'
                )
            ],
            
            'data_upload': [
                TutorialStep(
                    id='upload_intro',
                    title='数据上传向导',
                    description='上传您的多组学数据进行个性化分析。我们支持表达、临床、突变等多种数据类型。',
                    target_element='.upload-section',
                    position='top'
                ),
                TutorialStep(
                    id='template_download',
                    title='下载数据模板',
                    description='首先下载我们提供的数据模板，确保您的数据格式正确。',
                    target_element='#download-clinical-template',
                    position='bottom',
                    action='click'
                ),
                TutorialStep(
                    id='data_preparation',
                    title='数据准备提示',
                    description='请确保您的数据包含必需的列，样本ID在所有文件中保持一致。',
                    target_element='.upload-tips',
                    position='top'
                ),
                TutorialStep(
                    id='file_upload',
                    title='文件上传',
                    description='将您准备好的数据文件拖拽到这里，或点击选择文件。支持多种格式。',
                    target_element='#upload-data',
                    position='bottom'
                ),
                TutorialStep(
                    id='validation_check',
                    title='数据验证',
                    description='系统会自动验证您的数据质量和格式，确保分析的准确性。',
                    target_element='#validation-results',
                    position='top'
                )
            ],
            
            'analysis_workflow': [
                TutorialStep(
                    id='workflow_intro',
                    title='分析工作流程',
                    description='让我们了解推荐的分析顺序，从基础到高级，循序渐进。',
                    target_element='.analysis-content',
                    position='top'
                ),
                TutorialStep(
                    id='basic_analysis',
                    title='基础分析',
                    description='从概览和多维度分析开始，了解数据的基本特征和质量。',
                    target_element='#sidebar-overview',
                    position='right'
                ),
                TutorialStep(
                    id='intermediate_analysis',
                    title='中级分析',
                    description='进行网络分析和生存分析，探索基因间关系和临床意义。',
                    target_element='#sidebar-network',
                    position='right'
                ),
                TutorialStep(
                    id='advanced_analysis',
                    title='高级分析',
                    description='使用精准医学模块进行深度分析，获得个性化医疗洞察。',
                    target_element='#sidebar-immune',
                    position='right'
                ),
                TutorialStep(
                    id='results_interpretation',
                    title='结果解读',
                    description='每个分析都提供详细的结果解读和生物学意义说明。',
                    target_element='.result-interpretation',
                    position='top'
                )
            ],
            
            'advanced_features': [
                TutorialStep(
                    id='batch_processing',
                    title='批量处理',
                    description='对多个数据集同时进行分析，进行比较研究。',
                    target_element='#sidebar-batch',
                    position='right'
                ),
                TutorialStep(
                    id='task_queue',
                    title='任务队列管理',
                    description='监控和管理您的分析任务，支持后台运行和优先级设置。',
                    target_element='#sidebar-taskqueue',
                    position='right'
                ),
                TutorialStep(
                    id='dataset_management',
                    title='数据集管理',
                    description='管理您的所有数据集，包括版本控制和元数据管理。',
                    target_element='#top-nav-datasets',
                    position='bottom'
                ),
                TutorialStep(
                    id='export_results',
                    title='结果导出',
                    description='导出分析结果为多种格式，支持发表和报告需求。',
                    target_element='#sidebar-download',
                    position='right'
                )
            ]
        }
    
    def _initialize_help_content(self) -> Dict:
        """初始化帮助内容"""
        return {
            'getting_started': {
                'title': '快速开始',
                'content': {
                    'overview': '''
                    # 平台概述
                    
                    LIHC分析平台是一个专业的肝癌多组学数据分析工具，支持：
                    - 🧬 基因表达分析
                    - 🏥 临床数据关联
                    - 🔬 突变影响评估
                    - 🎯 精准医学应用
                    
                    ## 主要功能
                    1. **多维度生物学分析** - 全面的数据概览和质量评估
                    2. **网络分析** - 基因共表达和调控网络重构
                    3. **生存分析** - 预后标志物筛选和风险评估
                    4. **精准医学** - 免疫、药物、亚型等专业分析
                    ''',
                    
                    'data_requirements': '''
                    # 数据要求
                    
                    ## 必需数据
                    - **基因表达矩阵**: 基因×样本，推荐log2转换
                    - **临床信息**: 包含样本ID、生存时间、事件状态
                    
                    ## 可选数据
                    - **突变数据**: VCF格式或注释突变列表
                    - **甲基化数据**: beta值矩阵
                    - **拷贝数变异**: 片段水平CNV数据
                    
                    ## 数据格式
                    - 支持CSV、TSV、Excel格式
                    - 推荐压缩包批量上传
                    - 样本ID必须在所有文件中保持一致
                    ''',
                    
                    'first_analysis': '''
                    # 您的第一个分析
                    
                    ## 步骤1: 选择数据
                    - 新用户建议从演示数据开始
                    - 演示数据包含TCGA-LIHC的374个样本
                    
                    ## 步骤2: 选择分析类型
                    推荐顺序：
                    1. 多维度分析 - 了解数据特征
                    2. 生存分析 - 识别预后基因
                    3. 网络分析 - 探索基因关系
                    4. 精准医学 - 深度专业分析
                    
                    ## 步骤3: 解读结果
                    - 每个分析都有详细的结果说明
                    - 可以下载图表和数据
                    - 支持结果对比和整合
                    '''
                }
            },
            
            'analysis_guides': {
                'title': '分析指南',
                'content': {
                    'differential_expression': '''
                    # 差异表达分析指南
                    
                    ## 分析原理
                    通过统计学方法比较不同组间基因表达差异，识别疾病相关基因。
                    
                    ## 关键参数
                    - **Fold Change阈值**: 通常设为2倍（log2FC > 1）
                    - **P值阈值**: 推荐0.05，严格研究可用0.01
                    - **多重检验校正**: 默认使用FDR校正
                    
                    ## 结果解读
                    - **火山图**: 展示fold change vs p-value关系
                    - **热图**: 显示差异基因的表达模式
                    - **功能富集**: 差异基因的生物学功能
                    
                    ## 应用场景
                    - 肿瘤vs正常组织比较
                    - 药物处理前后对比
                    - 不同疾病分期比较
                    ''',
                    
                    'survival_analysis': '''
                    # 生存分析指南
                    
                    ## 分析方法
                    - **Kaplan-Meier**: 生存概率估计
                    - **Log-rank检验**: 组间生存差异检验
                    - **Cox回归**: 多因素预后分析
                    
                    ## 参数设置
                    - **分组策略**: 通常按中位数分为高低表达组
                    - **时间单位**: 月为单位更直观
                    - **删失处理**: 自动处理右删失数据
                    
                    ## 结果评估
                    - **P值 < 0.05**: 有统计学意义
                    - **风险比HR**: >1为高风险，<1为保护因素
                    - **置信区间**: 评估结果稳定性
                    
                    ## 临床意义
                    - 识别预后生物标志物
                    - 指导风险分层
                    - 支持治疗决策
                    '''
                }
            },
            
            'troubleshooting': {
                'title': '常见问题',
                'content': {
                    'data_upload_issues': '''
                    # 数据上传问题
                    
                    ## 文件格式问题
                    **问题**: 上传失败或格式错误
                    **解决**: 
                    - 检查文件编码（推荐UTF-8）
                    - 确认分隔符（CSV用逗号，TSV用制表符）
                    - 基因名不要包含特殊字符
                    
                    ## 样本ID不匹配
                    **问题**: 不同文件中样本ID不一致
                    **解决**:
                    - 确保所有文件使用相同的样本命名
                    - 避免ID中的空格和特殊字符
                    - 可以使用我们的ID标准化工具
                    
                    ## 文件过大
                    **问题**: 文件上传超时
                    **解决**:
                    - 压缩文件后上传
                    - 分批上传大型数据集
                    - 联系技术支持获得大文件传输方案
                    ''',
                    
                    'analysis_errors': '''
                    # 分析错误处理
                    
                    ## 样本数量不足
                    **问题**: 提示样本数量不够
                    **解决**:
                    - 检查数据完整性
                    - 某些分析有最小样本要求
                    - 考虑使用简化版分析
                    
                    ## 内存不足
                    **问题**: 分析过程中出现内存错误
                    **解决**:
                    - 减少同时运行的分析数量
                    - 使用特征筛选减少基因数量
                    - 尝试批量处理模式
                    
                    ## 结果异常
                    **问题**: 分析结果不符合预期
                    **解决**:
                    - 检查数据预处理步骤
                    - 验证参数设置
                    - 对比其他方法的结果
                    - 查看分析日志了解详情
                    '''
                }
            }
        }
    
    def _initialize_contextual_tips(self) -> Dict:
        """初始化上下文提示"""
        return {
            'data_upload': [
                "💡 首次使用建议先体验演示数据",
                "📁 支持将多个文件打包成ZIP上传",
                "✅ 上传前请检查数据格式和样本ID一致性",
                "⚡ 大文件建议压缩后上传以提高速度"
            ],
            
            'analysis_selection': [
                "🎯 新手推荐从多维度分析开始",
                "📊 样本数量少于10建议选择简化分析",
                "🔄 可以同时运行多个不同类型的分析",
                "⏱️ 高级分析耗时较长，建议使用任务队列"
            ],
            
            'result_interpretation': [
                "📈 注意查看统计显著性指标",
                "🔍 可以将鼠标悬停在图表上查看详细信息",
                "💾 及时保存重要的分析结果",
                "📋 使用导出功能获取可发表的图表"
            ],
            
            'performance_optimization': [
                "🚀 使用筛选功能减少计算量",
                "⚡ 批量分析适合处理多个相似数据集",
                "🔄 任务队列可以避免浏览器超时",
                "💻 建议在稳定网络环境下运行大型分析"
            ]
        }
    
    def create_tutorial_component(self, tutorial_name: str) -> html.Div:
        """创建教程组件"""
        
        tutorial_steps = self.tutorials.get(tutorial_name, [])
        
        return html.Div([
            # Tutorial overlay
            html.Div([
                html.Div([
                    # Tutorial content
                    html.Div([
                        html.Div(id=f'tutorial-content-{tutorial_name}', 
                                children=self._create_tutorial_step_content(tutorial_steps[0] if tutorial_steps else None)),
                        
                        # Navigation buttons
                        html.Div([
                            html.Button("跳过教程", id=f'tutorial-skip-{tutorial_name}', 
                                      className="btn btn-outline-secondary",
                                      style={'marginRight': '10px'}),
                            html.Button("上一步", id=f'tutorial-prev-{tutorial_name}', 
                                      className="btn btn-outline-primary",
                                      style={'marginRight': '10px'}),
                            html.Button("下一步", id=f'tutorial-next-{tutorial_name}', 
                                      className="btn btn-primary"),
                        ], style={'textAlign': 'right', 'marginTop': '20px'})
                    ], className="tutorial-popup")
                ], className="tutorial-overlay")
            ], id=f'tutorial-{tutorial_name}', style={'display': 'none'}),
            
            # Tutorial progress
            html.Div([
                html.Div([
                    html.Span(f"教程进度: "),
                    html.Span(id=f'tutorial-progress-{tutorial_name}', children="0/0"),
                    html.Div(id=f'tutorial-progress-bar-{tutorial_name}', 
                           className="progress-bar")
                ], className="tutorial-progress")
            ], id=f'tutorial-progress-container-{tutorial_name}', style={'display': 'none'}),
            
            # Hidden stores
            dcc.Store(id=f'tutorial-state-{tutorial_name}', data={'current_step': 0, 'active': False}),
        ])
    
    def create_help_panel(self) -> html.Div:
        """创建帮助面板"""
        
        return html.Div([
            # Help trigger button
            html.Button([
                html.I(className="fas fa-question-circle"),
                " 帮助"
            ], id="help-trigger", className="btn btn-info help-trigger",
               style={'position': 'fixed', 'bottom': '20px', 'right': '20px', 'zIndex': '1000'}),
            
            # Help panel
            html.Div([
                html.Div([
                    # Header
                    html.Div([
                        html.H4([
                            html.I(className="fas fa-question-circle"),
                            " 帮助中心"
                        ], style={'margin': '0'}),
                        html.Button("×", id="help-close", 
                                  style={'background': 'none', 'border': 'none', 
                                         'fontSize': '24px', 'cursor': 'pointer'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 
                             'alignItems': 'center', 'marginBottom': '20px',
                             'borderBottom': '1px solid #ddd', 'paddingBottom': '10px'}),
                    
                    # Search box
                    html.Div([
                        dcc.Input(
                            id='help-search',
                            type='text',
                            placeholder='搜索帮助内容...',
                            style={'width': '100%'},
                            className='form-control'
                        )
                    ], style={'marginBottom': '20px'}),
                    
                    # Help categories
                    html.Div([
                        html.H6("快速导航"),
                        html.Div([
                            html.Button("新手入门", id="help-cat-getting-started", 
                                      className="btn btn-outline-primary btn-sm",
                                      style={'marginRight': '5px', 'marginBottom': '5px'}),
                            html.Button("分析指南", id="help-cat-analysis-guides", 
                                      className="btn btn-outline-secondary btn-sm",
                                      style={'marginRight': '5px', 'marginBottom': '5px'}),
                            html.Button("常见问题", id="help-cat-troubleshooting", 
                                      className="btn btn-outline-warning btn-sm",
                                      style={'marginRight': '5px', 'marginBottom': '5px'}),
                            html.Button("开始教程", id="help-start-tutorial", 
                                      className="btn btn-outline-success btn-sm",
                                      style={'marginBottom': '5px'})
                        ])
                    ], style={'marginBottom': '20px'}),
                    
                    # Help content
                    html.Div(id='help-content', children=[
                        html.P("选择上方类别查看相关帮助内容，或使用搜索功能找到您需要的信息。")
                    ]),
                    
                    # Contextual tips
                    html.Div([
                        html.H6("💡 当前页面提示"),
                        html.Div(id='contextual-tips')
                    ], style={'marginTop': '30px', 'backgroundColor': '#f8f9fa', 
                             'padding': '15px', 'borderRadius': '5px'})
                    
                ], style={'backgroundColor': 'white', 'padding': '30px', 
                         'borderRadius': '10px', 'maxHeight': '80vh', 
                         'overflowY': 'auto', 'width': '500px'})
            ], id="help-panel", className="help-panel", 
               style={'display': 'none', 'position': 'fixed', 'top': '50%', 
                     'right': '20px', 'transform': 'translateY(-50%)', 
                     'zIndex': '1001', 'boxShadow': '0 10px 30px rgba(0,0,0,0.3)'})
        ])
    
    def create_contextual_help_tooltip(self, element_id: str, content: str, 
                                     position: str = 'top') -> html.Div:
        """创建上下文帮助提示"""
        
        return html.Div([
            html.I(className="fas fa-info-circle contextual-help-icon",
                  id=f'help-icon-{element_id}',
                  style={'marginLeft': '5px', 'color': '#007bff', 'cursor': 'pointer'}),
            
            dcc.Tooltip(
                content,
                target=f'help-icon-{element_id}',
                placement=position
            )
        ], style={'display': 'inline-block'})
    
    def create_smart_assistant(self) -> html.Div:
        """创建智能助手"""
        
        return html.Div([
            # Assistant trigger
            html.Button([
                html.I(className="fas fa-robot"),
                " 智能助手"
            ], id="assistant-trigger", className="btn btn-success assistant-trigger",
               style={'position': 'fixed', 'bottom': '80px', 'right': '20px', 'zIndex': '1000'}),
            
            # Assistant chat panel
            html.Div([
                html.Div([
                    # Header
                    html.Div([
                        html.H5([
                            html.I(className="fas fa-robot"),
                            " LIHC分析助手"
                        ], style={'margin': '0', 'color': 'white'}),
                        html.Button("×", id="assistant-close", 
                                  style={'background': 'none', 'border': 'none', 
                                         'color': 'white', 'fontSize': '20px', 'cursor': 'pointer'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 
                             'alignItems': 'center', 'backgroundColor': '#28a745',
                             'padding': '15px', 'borderRadius': '10px 10px 0 0'}),
                    
                    # Chat messages
                    html.Div([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-robot", style={'marginRight': '8px'}),
                                "您好！我是您的分析助手。我可以帮您："
                            ], className="assistant-message"),
                            html.Ul([
                                html.Li("🎯 推荐适合的分析方法"),
                                html.Li("📊 解释分析结果"),
                                html.Li("🔍 解决技术问题"),
                                html.Li("💡 提供优化建议")
                            ], style={'margin': '10px 0'})
                        ])
                    ], id='assistant-messages', 
                       style={'height': '300px', 'overflowY': 'auto', 'padding': '15px'}),
                    
                    # Input area
                    html.Div([
                        dcc.Input(
                            id='assistant-input',
                            type='text',
                            placeholder='输入您的问题...',
                            style={'width': '100%', 'marginBottom': '10px'},
                            className='form-control'
                        ),
                        html.Div([
                            html.Button("发送", id="assistant-send", 
                                      className="btn btn-primary btn-sm",
                                      style={'marginRight': '5px'}),
                            html.Button("清除", id="assistant-clear", 
                                      className="btn btn-outline-secondary btn-sm")
                        ])
                    ], style={'padding': '15px', 'borderTop': '1px solid #ddd'})
                    
                ], style={'backgroundColor': 'white', 'borderRadius': '10px', 
                         'boxShadow': '0 10px 30px rgba(0,0,0,0.3)', 'width': '400px'})
            ], id="assistant-panel", style={'display': 'none', 'position': 'fixed', 
                                          'bottom': '20px', 'right': '20px', 'zIndex': '1001'})
        ])
    
    def _create_tutorial_step_content(self, step: TutorialStep) -> List:
        """创建教程步骤内容"""
        
        if not step:
            return [html.P("教程已完成！")]
        
        return [
            html.H4(step.title, style={'color': '#007bff', 'marginBottom': '15px'}),
            html.P(step.description),
            
            # Step indicator
            html.Div([
                html.I(className="fas fa-lightbulb", style={'color': '#ffc107', 'marginRight': '8px'}),
                html.Strong("提示: "),
                html.Span(f"关注 {step.target_element} 区域")
            ], style={'backgroundColor': '#fff3cd', 'padding': '10px', 
                     'borderRadius': '5px', 'marginTop': '15px'})
        ]
    
    def get_contextual_tips(self, current_page: str, user_context: Dict = None) -> List[str]:
        """获取上下文相关的提示"""
        
        # 基础提示
        base_tips = self.contextual_tips.get(current_page, [])
        
        # 根据用户上下文添加特定提示
        context_tips = []
        
        if user_context:
            if user_context.get('is_first_visit', False):
                context_tips.append("🎉 欢迎首次使用！建议先查看新手教程")
            
            if user_context.get('data_uploaded', False):
                context_tips.append("✅ 数据已上传，可以开始分析了")
            
            if user_context.get('analysis_running', False):
                context_tips.append("⏳ 分析正在运行中，您可以在任务队列中查看进度")
        
        return base_tips + context_tips

# 全局实例
guidance_system = UserGuidanceSystem()