"""
Intelligent User Guidance System
智能用户导航系统 - 提供自适应的用户引导和帮助
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context, no_update
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import uuid

@dataclass
class TutorialStep:
    """教程步骤"""
    id: str
    title: str
    description: str
    target_element: str  # CSS selector
    position: str = 'bottom'  # top, bottom, left, right
    action_required: bool = False
    next_step: Optional[str] = None
    prerequisites: List[str] = None
    tips: List[str] = None

@dataclass
class UserProgress:
    """用户进度"""
    user_id: str
    tutorial_progress: Dict[str, int]  # tutorial_id -> step_index
    completed_tutorials: List[str]
    skill_level: str  # 'beginner', 'intermediate', 'advanced'
    last_active: str
    total_analyses: int
    feature_usage: Dict[str, int]

class IntelligentGuidanceSystem:
    """智能引导系统"""
    
    def __init__(self):
        self.tutorials = self._create_tutorials()
        self.user_progress = {}
        self.contextual_help = self._create_contextual_help()
        self.tips_database = self._create_tips_database()
        
    def _create_tutorials(self) -> Dict[str, List[TutorialStep]]:
        """创建教程系统"""
        
        tutorials = {
            'platform_overview': [
                TutorialStep(
                    id='welcome',
                    title='欢迎使用 LIHC 分析平台！',
                    description='这是一个专业的肝癌多组学数据分析平台。让我们开始一个快速的导览吧！',
                    target_element='.page-header',
                    position='bottom'
                ),
                TutorialStep(
                    id='navigation',
                    title='平台导航',
                    description='顶部导航栏包含主要功能：数据上传、数据集管理、演示数据和系统设置。',
                    target_element='.top-nav',
                    position='bottom'
                ),
                TutorialStep(
                    id='sidebar',
                    title='分析模块',
                    description='左侧边栏包含所有分析模块，从基础的多维分析到高级的精准医学分析。',
                    target_element='.sidebar',
                    position='right'
                ),
                TutorialStep(
                    id='content_area',
                    title='主要内容区域',
                    description='这里显示分析结果、图表和数据表格。所有的交互和可视化都在这里进行。',
                    target_element='.main-content',
                    position='top'
                )
            ],
            
            'first_analysis': [
                TutorialStep(
                    id='data_upload',
                    title='第一步：上传数据',
                    description='点击"数据上传"开始上传您的多组学数据。我们支持表达、临床、突变等多种数据类型。',
                    target_element='#top-nav-data',
                    position='bottom',
                    action_required=True
                ),
                TutorialStep(
                    id='download_template',
                    title='下载数据模板',
                    description='如果这是您第一次使用，建议先下载数据模板了解正确的数据格式。',
                    target_element='#download-clinical-template',
                    position='right'
                ),
                TutorialStep(
                    id='upload_files',
                    title='上传文件',
                    description='将您的数据文件拖拽到上传区域，或点击选择文件。支持 CSV、Excel 和 ZIP 格式。',
                    target_element='#upload-data',
                    position='top',
                    action_required=True
                ),
                TutorialStep(
                    id='start_analysis',
                    title='开始分析',
                    description='数据验证通过后，选择要运行的分析模块，然后点击"开始分析"。',
                    target_element='#start-analysis',
                    position='top',
                    action_required=True
                ),
                TutorialStep(
                    id='view_results',
                    title='查看结果',
                    description='分析完成后，您可以在各个分析页面查看详细结果，包括图表、表格和下载报告。',
                    target_element='.sidebar-item',
                    position='right'
                )
            ],
            
            'advanced_features': [
                TutorialStep(
                    id='dataset_management',
                    title='数据集管理',
                    description='在数据集管理页面，您可以查看、编辑和组织所有的数据集。',
                    target_element='#top-nav-datasets',
                    position='bottom'
                ),
                TutorialStep(
                    id='batch_processing',
                    title='批量处理',
                    description='批量处理功能允许您同时分析多个数据集，进行对比研究。',
                    target_element='#sidebar-batch',
                    position='right'
                ),
                TutorialStep(
                    id='task_queue',
                    title='任务队列',
                    description='任务队列管理让您监控所有正在运行的分析任务。',
                    target_element='#sidebar-taskqueue',
                    position='right'
                ),
                TutorialStep(
                    id='interactive_charts',
                    title='交互式图表',
                    description='所有图表都支持缩放、平移、选择和导出。试试右键点击图表查看更多选项！',
                    target_element='.enhanced-chart-container',
                    position='top'
                )
            ],
            
            'chart_interactions': [
                TutorialStep(
                    id='chart_selection',
                    title='数据点选择',
                    description='在图表中拖拽选择数据点，可以查看详细统计信息。',
                    target_element='[id^="chart-"]',
                    position='bottom'
                ),
                TutorialStep(
                    id='chart_export',
                    title='图表导出',
                    description='点击导出按钮可以将图表保存为 PNG、SVG、PDF 或 HTML 格式。',
                    target_element='[id^="export-"]',
                    position='top'
                ),
                TutorialStep(
                    id='crossfilter',
                    title='交叉筛选',
                    description='在一个图表中的选择会影响其他图表，帮助您发现数据间的关联。',
                    target_element='#enable-crossfilter',
                    position='left'
                )
            ]
        }
        
        return tutorials
    
    def _create_contextual_help(self) -> Dict[str, Dict]:
        """创建上下文帮助"""
        
        return {
            'data-upload': {
                'title': '数据上传帮助',
                'content': [
                    '📁 支持的文件格式：CSV、TSV、Excel (.xlsx)、ZIP',
                    '📊 数据要求：至少需要基因表达数据',
                    '🧬 推荐包含：临床数据（生存信息）',
                    '🔢 样本数量：建议至少 10 个样本',
                    '📋 使用模板可以确保数据格式正确'
                ],
                'tips': [
                    '如果上传 ZIP 文件，请确保包含所有必需的数据文件',
                    '基因名称请使用标准的 HUGO 符号',
                    '临床数据中的 sample_id 必须与表达数据的列名匹配'
                ]
            },
            
            'survival-analysis': {
                'title': '生存分析指南',
                'content': [
                    '📈 Kaplan-Meier 生存曲线分析',
                    '🎯 基于基因表达的患者分组',
                    '📊 Log-rank 检验评估显著性',
                    '⚡ 需要包含生存数据的临床信息'
                ],
                'tips': [
                    'P < 0.05 表示基因表达对生存有显著影响',
                    '红色曲线通常表示高表达组，蓝色表示低表达组',
                    '曲线分离越大，预后差异越明显'
                ]
            },
            
            'network-analysis': {
                'title': '网络分析说明',
                'content': [
                    '🔗 基因共表达网络构建',
                    '🎯 关键调控基因识别',
                    '📊 网络中心性分析',
                    '🧬 功能模块检测'
                ],
                'tips': [
                    '节点大小表示基因的连接度（重要性）',
                    '边的粗细表示基因间相关性强度',
                    '密集连接的区域可能代表功能相关的基因群'
                ]
            }
        }
    
    def _create_tips_database(self) -> Dict[str, List[str]]:
        """创建提示数据库"""
        
        return {
            'general': [
                '💡 使用 Ctrl+鼠标滚轮可以快速缩放图表',
                '💾 记得保存重要的分析结果',
                '🔍 使用搜索功能快速找到目标基因',
                '📊 尝试不同的可视化方式来展示数据',
                '🎯 对比不同数据集的结果可以获得新洞察'
            ],
            
            'performance': [
                '⚡ 大数据集分析时，建议使用批量处理功能',
                '🚀 启用任务队列可以并行运行多个分析',
                '💻 关闭不必要的浏览器标签页可以提高性能',
                '📈 如果分析较慢，可以先用小样本测试'
            ],
            
            'analysis': [
                '🧬 差异表达分析是所有下游分析的基础',
                '📊 生存分析可以帮助识别预后相关基因',
                '🔗 网络分析揭示基因间的调控关系',
                '🎯 免疫分析对肿瘤研究特别有价值'
            ],
            
            'troubleshooting': [
                '❓ 如果上传失败，请检查文件格式和大小',
                '🔧 清除浏览器缓存可以解决一些显示问题',
                '📝 确保数据文件的编码格式为 UTF-8',
                '🔄 如果页面无响应，尝试刷新页面'
            ]
        }
    
    def get_user_progress(self, user_id: str) -> UserProgress:
        """获取用户进度"""
        
        if user_id not in self.user_progress:
            self.user_progress[user_id] = UserProgress(
                user_id=user_id,
                tutorial_progress={},
                completed_tutorials=[],
                skill_level='beginner',
                last_active=datetime.now().isoformat(),
                total_analyses=0,
                feature_usage={}
            )
        
        return self.user_progress[user_id]
    
    def update_user_progress(self, user_id: str, tutorial_id: str, step_index: int):
        """更新用户进度"""
        
        progress = self.get_user_progress(user_id)
        progress.tutorial_progress[tutorial_id] = step_index
        progress.last_active = datetime.now().isoformat()
        
        # 检查是否完成教程
        tutorial_steps = self.tutorials.get(tutorial_id, [])
        if step_index >= len(tutorial_steps) - 1:
            if tutorial_id not in progress.completed_tutorials:
                progress.completed_tutorials.append(tutorial_id)
                
                # 更新技能等级
                self._update_skill_level(progress)
    
    def _update_skill_level(self, progress: UserProgress):
        """更新技能等级"""
        
        completed_count = len(progress.completed_tutorials)
        total_analyses = progress.total_analyses
        
        if completed_count >= 3 and total_analyses >= 10:
            progress.skill_level = 'advanced'
        elif completed_count >= 2 or total_analyses >= 5:
            progress.skill_level = 'intermediate'
        else:
            progress.skill_level = 'beginner'
    
    def get_recommended_tutorial(self, user_id: str, current_page: str = None) -> Optional[str]:
        """获取推荐教程"""
        
        progress = self.get_user_progress(user_id)
        
        # 新用户推荐平台概览
        if not progress.completed_tutorials:
            return 'platform_overview'
        
        # 根据当前页面推荐
        if current_page == 'data-upload' and 'first_analysis' not in progress.completed_tutorials:
            return 'first_analysis'
        
        # 进阶用户推荐高级功能
        if (progress.skill_level in ['intermediate', 'advanced'] and 
            'advanced_features' not in progress.completed_tutorials):
            return 'advanced_features'
        
        return None
    
    def get_contextual_help_for_page(self, page_id: str) -> Dict:
        """获取页面相关帮助"""
        
        return self.contextual_help.get(page_id, {
            'title': '页面帮助',
            'content': ['暂无特定帮助信息'],
            'tips': ['尝试探索页面上的各种功能']
        })
    
    def get_smart_tips(self, user_id: str, context: Dict = None) -> List[str]:
        """获取智能提示"""
        
        progress = self.get_user_progress(user_id)
        tips = []
        
        # 基于技能等级的提示
        if progress.skill_level == 'beginner':
            tips.extend(self.tips_database['general'][:2])
        elif progress.skill_level == 'intermediate':
            tips.extend(self.tips_database['analysis'][:2])
        else:
            tips.extend(self.tips_database['performance'][:2])
        
        # 基于上下文的提示
        if context:
            if context.get('has_large_dataset'):
                tips.append('💡 检测到大数据集，建议使用批量处理功能以获得更好性能')
            
            if context.get('analysis_count', 0) > 5:
                tips.append('🎯 您已进行多次分析，可以尝试数据集管理功能来组织结果')
            
            if context.get('upload_errors', 0) > 0:
                tips.extend(self.tips_database['troubleshooting'][:1])
        
        return tips[:3]  # 返回最多3个提示
    
    def create_tutorial_overlay(self, tutorial_id: str, step_index: int = 0) -> html.Div:
        """创建教程覆盖层"""
        
        tutorial_steps = self.tutorials.get(tutorial_id, [])
        if not tutorial_steps or step_index >= len(tutorial_steps):
            return html.Div()
        
        current_step = tutorial_steps[step_index]
        total_steps = len(tutorial_steps)
        
        return html.Div([
            # 遮罩层
            html.Div(
                style={
                    'position': 'fixed',
                    'top': '0',
                    'left': '0',
                    'width': '100vw',
                    'height': '100vh',
                    'backgroundColor': 'rgba(0, 0, 0, 0.5)',
                    'zIndex': '9998'
                }
            ),
            
            # 教程弹框
            html.Div([
                # 头部
                html.Div([
                    html.H4(current_step.title, style={'margin': '0', 'color': '#2c3e50'}),
                    html.Button(
                        '×',
                        id='close-tutorial',
                        style={
                            'background': 'none',
                            'border': 'none',
                            'fontSize': '24px',
                            'cursor': 'pointer',
                            'color': '#666'
                        }
                    )
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'padding': '20px 20px 10px 20px',
                    'borderBottom': '1px solid #eee'
                }),
                
                # 内容
                html.Div([
                    html.P(current_step.description, style={
                        'fontSize': '16px',
                        'lineHeight': '1.6',
                        'color': '#555',
                        'margin': '0 0 20px 0'
                    }),
                    
                    # 提示
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-lightbulb", style={'marginRight': '8px'}),
                            tip
                        ], style={'marginBottom': '8px', 'fontSize': '14px', 'color': '#666'})
                        for tip in (current_step.tips or [])
                    ]) if current_step.tips else html.Div(),
                    
                ], style={'padding': '20px'}),
                
                # 底部控制
                html.Div([
                    # 进度指示器
                    html.Div([
                        html.Div([
                            html.Div(
                                style={
                                    'width': '8px',
                                    'height': '8px',
                                    'borderRadius': '50%',
                                    'backgroundColor': '#007bff' if i <= step_index else '#ddd',
                                    'margin': '0 4px'
                                }
                            ) for i in range(total_steps)
                        ], style={'display': 'flex', 'alignItems': 'center'}),
                        html.Small(f'{step_index + 1} / {total_steps}', style={'marginLeft': '10px', 'color': '#666'})
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    
                    # 控制按钮
                    html.Div([
                        html.Button(
                            '跳过教程',
                            id='skip-tutorial',
                            className='btn btn-outline-secondary',
                            style={'marginRight': '10px'}
                        ),
                        html.Button(
                            '上一步' if step_index > 0 else '',
                            id='prev-tutorial-step',
                            className='btn btn-outline-primary',
                            style={'marginRight': '10px', 'display': 'inline-block' if step_index > 0 else 'none'}
                        ),
                        html.Button(
                            '下一步' if step_index < total_steps - 1 else '完成',
                            id='next-tutorial-step',
                            className='btn btn-primary'
                        )
                    ])
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'padding': '15px 20px',
                    'borderTop': '1px solid #eee',
                    'backgroundColor': '#f8f9fa'
                })
            ], style={
                'position': 'fixed',
                'top': '50%',
                'left': '50%',
                'transform': 'translate(-50%, -50%)',
                'backgroundColor': 'white',
                'borderRadius': '12px',
                'boxShadow': '0 10px 30px rgba(0, 0, 0, 0.3)',
                'maxWidth': '500px',
                'width': '90%',
                'zIndex': '9999'
            })
        ], id='tutorial-overlay')
    
    def create_help_panel(self, page_id: str = None, user_id: str = None) -> html.Div:
        """创建帮助面板"""
        
        help_content = self.get_contextual_help_for_page(page_id or 'general')
        tips = self.get_smart_tips(user_id or 'anonymous') if user_id else []
        
        return html.Div([
            # 帮助按钮
            html.Button([
                html.I(className="fas fa-question-circle"),
                " 帮助"
            ], id='toggle-help-panel', className='btn btn-info btn-sm', 
               style={
                   'position': 'fixed',
                   'bottom': '20px',
                   'right': '20px',
                   'zIndex': '1000',
                   'borderRadius': '50px',
                   'padding': '12px 20px',
                   'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.2)'
               }),
            
            # 帮助面板
            html.Div([
                # 头部
                html.Div([
                    html.H5([
                        html.I(className="fas fa-question-circle", style={'marginRight': '10px'}),
                        help_content.get('title', '帮助')
                    ], style={'margin': '0'}),
                    html.Button(
                        '×',
                        id='close-help-panel',
                        style={
                            'background': 'none',
                            'border': 'none',
                            'fontSize': '20px',
                            'cursor': 'pointer'
                        }
                    )
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'padding': '15px',
                    'borderBottom': '1px solid #eee'
                }),
                
                # 内容
                html.Div([
                    # 主要帮助内容
                    html.Div([
                        html.H6("📖 使用指南", style={'marginBottom': '10px'}),
                        html.Ul([
                            html.Li(item, style={'marginBottom': '5px'})
                            for item in help_content.get('content', [])
                        ])
                    ], style={'marginBottom': '20px'}),
                    
                    # 提示
                    html.Div([
                        html.H6("💡 实用提示", style={'marginBottom': '10px'}),
                        html.Ul([
                            html.Li(tip, style={'marginBottom': '5px'})
                            for tip in help_content.get('tips', [])
                        ])
                    ], style={'marginBottom': '20px'}) if help_content.get('tips') else html.Div(),
                    
                    # 智能提示
                    html.Div([
                        html.H6("🎯 个性化建议", style={'marginBottom': '10px'}),
                        html.Ul([
                            html.Li(tip, style={'marginBottom': '5px'})
                            for tip in tips
                        ])
                    ]) if tips else html.Div(),
                    
                    # 教程入口
                    html.Div([
                        html.Hr(),
                        html.H6("🎓 互动教程"),
                        html.Div([
                            html.Button(
                                '平台入门',
                                id='start-tutorial-overview',
                                className='btn btn-outline-primary btn-sm',
                                style={'marginRight': '10px', 'marginBottom': '5px'}
                            ),
                            html.Button(
                                '第一次分析',
                                id='start-tutorial-first',
                                className='btn btn-outline-success btn-sm',
                                style={'marginRight': '10px', 'marginBottom': '5px'}
                            ),
                            html.Button(
                                '高级功能',
                                id='start-tutorial-advanced',
                                className='btn btn-outline-info btn-sm',
                                style={'marginBottom': '5px'}
                            )
                        ])
                    ])
                    
                ], style={'padding': '15px', 'maxHeight': '400px', 'overflowY': 'auto'})
                
            ], id='help-panel', style={
                'position': 'fixed',
                'bottom': '80px',
                'right': '20px',
                'width': '350px',
                'backgroundColor': 'white',
                'border': '1px solid #ddd',
                'borderRadius': '12px',
                'boxShadow': '0 6px 20px rgba(0, 0, 0, 0.15)',
                'zIndex': '1001',
                'display': 'none'
            })
        ])

# 全局实例
guidance_system = IntelligentGuidanceSystem()