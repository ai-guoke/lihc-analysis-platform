"""
多语言文本组件
提供动态切换语言的文本显示功能
"""

from dash import html, dcc
import dash
from dash.dependencies import Input, Output, State
from src.utils.i18n import i18n

def create_text(text_key, text_id=None, tag='span', className='', style=None, fallback=None):
    """
    创建一个可以动态切换语言的文本组件
    
    Args:
        text_key: i18n中的文本键
        text_id: 组件的ID，如果不提供会自动生成
        tag: HTML标签类型（如'span', 'p', 'h1'等）
        className: CSS类名
        style: 样式字典
        fallback: 如果找不到翻译时的默认文本
    
    Returns:
        Dash HTML组件
    """
    if text_id is None:
        text_id = f"text-{text_key.replace('_', '-')}"
    
    # 获取当前语言的文本
    text_content = i18n.get_text(text_key, fallback)
    
    # 根据标签类型创建组件
    tag_map = {
        'span': html.Span,
        'p': html.P,
        'h1': html.H1,
        'h2': html.H2,
        'h3': html.H3,
        'h4': html.H4,
        'h5': html.H5,
        'h6': html.H6,
        'div': html.Div,
        'label': html.Label,
        'li': html.Li,
        'td': html.Td,
        'th': html.Th,
    }
    
    Component = tag_map.get(tag, html.Span)
    
    return Component(
        text_content,
        id=text_id,
        className=className,
        style=style
    )

def create_multilingual_layout(layout_dict):
    """
    创建包含多语言支持的布局
    
    Args:
        layout_dict: 布局配置字典，包含组件定义和文本键
    
    Returns:
        Dash布局组件
    """
    def process_item(item):
        if isinstance(item, dict) and 'text_key' in item:
            # 这是一个多语言文本组件
            return create_text(**item)
        elif isinstance(item, dict) and 'component' in item:
            # 这是一个复杂组件
            comp_type = item['component']
            props = item.get('props', {})
            children = item.get('children', [])
            
            # 递归处理子组件
            if children:
                if isinstance(children, list):
                    children = [process_item(child) for child in children]
                else:
                    children = process_item(children)
                props['children'] = children
            
            # 创建组件
            return comp_type(**props)
        elif isinstance(item, list):
            # 递归处理列表
            return [process_item(i) for i in item]
        else:
            # 返回原始项
            return item
    
    return process_item(layout_dict)

def register_language_callbacks(app, text_components):
    """
    为所有多语言文本组件注册回调
    
    Args:
        app: Dash应用实例
        text_components: 文本组件配置列表
    """
    # 批量更新所有文本组件
    outputs = []
    for comp in text_components:
        text_id = comp.get('text_id') or f"text-{comp['text_key'].replace('_', '-')}"
        outputs.append(Output(text_id, 'children'))
    
    if outputs:
        @app.callback(
            outputs,
            Input('language-store', 'data'),
            prevent_initial_call=False
        )
        def update_all_texts(current_lang):
            """更新所有文本内容"""
            i18n.set_language(current_lang)
            texts = []
            for comp in text_components:
                text_key = comp['text_key']
                fallback = comp.get('fallback')
                text_content = i18n.get_text(text_key, fallback)
                texts.append(text_content)
            return texts

# 预定义的文本组件配置
TEXT_COMPONENTS = [
    # 导航栏
    {'text_key': 'nav_upload', 'text_id': 'nav-data-upload'},
    {'text_key': 'nav_dataset_management', 'text_id': 'nav-dataset-management'},
    {'text_key': 'nav_demo', 'text_id': 'nav-demo'},
    {'text_key': 'nav_settings', 'text_id': 'nav-settings'},
    
    # 侧边栏
    {'text_key': 'nav_overview', 'text_id': 'side-overview'},
    {'text_key': 'nav_multidim', 'text_id': 'side-multidim'},
    {'text_key': 'nav_network', 'text_id': 'side-network'},
    {'text_key': 'nav_linchpin', 'text_id': 'side-linchpin'},
    {'text_key': 'nav_survival', 'text_id': 'side-survival'},
    {'text_key': 'nav_multiomics', 'text_id': 'side-multiomics'},
    {'text_key': 'nav_closedloop', 'text_id': 'side-closedloop'},
    {'text_key': 'nav_immune', 'text_id': 'side-immune'},
    {'text_key': 'nav_drug', 'text_id': 'side-drug'},
    {'text_key': 'nav_subtype', 'text_id': 'side-subtype'},
    {'text_key': 'nav_metabolism', 'text_id': 'side-metabolism'},
    {'text_key': 'nav_heterogeneity', 'text_id': 'side-heterogeneity'},
]