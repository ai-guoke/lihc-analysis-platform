"""
Chart Interaction Callbacks
图表交互回调函数 - 处理图表的所有交互事件
"""

import dash
from dash import Input, Output, State, callback_context, no_update
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
import base64
import io
from typing import Dict, List, Any, Optional
import traceback

from .interactive_charts import chart_enhancer

class ChartCallbackManager:
    """管理所有图表交互回调函数"""
    
    def __init__(self, app: dash.Dash):
        self.app = app
        self.chart_data_cache = {}
        self.selection_cache = {}
        self.filter_cache = {}
        
    def register_all_callbacks(self):
        """注册所有图表交互回调函数"""
        
        # 注册通用图表回调
        self._register_chart_selection_callbacks()
        self._register_chart_export_callbacks()
        self._register_chart_filter_callbacks()
        self._register_chart_statistics_callbacks()
        self._register_crossfilter_callbacks()
        
    def _register_chart_selection_callbacks(self):
        """注册图表选择回调"""
        
        def create_selection_callback(chart_id: str):
            @self.app.callback(
                [Output(f'stats-content-{chart_id}', 'children'),
                 Output(f'selection-store-{chart_id}', 'data', allow_duplicate=True)],
                [Input(f'chart-{chart_id}', 'selectedData')],
                prevent_initial_call=True
            )
            def update_chart_selection(selected_data):
                if not selected_data or 'points' not in selected_data:
                    return [
                        html.P("请在图表中选择数据点查看统计信息", 
                              style={'color': '#666', 'fontStyle': 'italic'})
                    ], {}
                
                try:
                    points = selected_data['points']
                    if not points:
                        return no_update, {}
                    
                    # 提取选中点的数据
                    selected_indices = [point.get('pointIndex', point.get('pointNumber', 0)) for point in points]
                    
                    # 创建统计信息
                    stats_content = self._create_selection_statistics(chart_id, points, selected_indices)
                    
                    # 存储选择数据供其他组件使用
                    selection_data = {
                        'chart_id': chart_id,
                        'indices': selected_indices,
                        'points': points,
                        'timestamp': pd.Timestamp.now().isoformat()
                    }
                    
                    return stats_content, selection_data
                    
                except Exception as e:
                    return [
                        html.Div([
                            html.P("处理选择数据时出错", style={'color': 'red'}),
                            html.Small(str(e), style={'color': '#666'})
                        ])
                    ], {}
        
        # 动态注册为已知图表ID创建回调
        known_chart_ids = ['scatter-plot', 'heatmap', 'bar-chart', 'line-chart', 
                          'violin-plot', 'network-graph', 'survival-curve']
        
        for chart_id in known_chart_ids:
            try:
                create_selection_callback(chart_id)
            except:
                pass  # 如果回调已存在，忽略错误
    
    def _register_chart_export_callbacks(self):
        """注册图表导出回调"""
        
        @self.app.callback(
            Output('download-chart-export', 'data'),
            [Input('export-png-{chart_id}', 'n_clicks') for chart_id in ['scatter-plot', 'heatmap', 'bar-chart']] +
            [Input('export-svg-{chart_id}', 'n_clicks') for chart_id in ['scatter-plot', 'heatmap', 'bar-chart']] +
            [Input('export-pdf-{chart_id}', 'n_clicks') for chart_id in ['scatter-plot', 'heatmap', 'bar-chart']] +
            [Input('export-html-{chart_id}', 'n_clicks') for chart_id in ['scatter-plot', 'heatmap', 'bar-chart']] +
            [Input('export-data-{chart_id}', 'n_clicks') for chart_id in ['scatter-plot', 'heatmap', 'bar-chart']],
            [State(f'chart-{chart_id}', 'figure') for chart_id in ['scatter-plot', 'heatmap', 'bar-chart']],
            prevent_initial_call=True
        )
        def handle_chart_export(*args):
            """处理图表导出"""
            ctx = callback_context
            if not ctx.triggered:
                return no_update
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            try:
                # 解析按钮ID获取图表ID和格式
                parts = button_id.split('-')
                export_format = parts[1]  # png, svg, pdf, html, data
                chart_id = '-'.join(parts[2:])  # chart ID
                
                # 获取对应的图表数据
                figure_state_index = ['scatter-plot', 'heatmap', 'bar-chart'].index(chart_id)
                figure = args[15 + figure_state_index]  # States start after all inputs
                
                if not figure:
                    return no_update
                
                return self._export_chart(figure, chart_id, export_format)
                
            except Exception as e:
                print(f"Export error: {e}")
                return no_update
    
    def _register_chart_filter_callbacks(self):
        """注册图表筛选回调"""
        
        def create_filter_callback(chart_id: str):
            @self.app.callback(
                Output(f'chart-{chart_id}', 'figure'),
                [Input(f'apply-filters-{chart_id}', 'n_clicks'),
                 Input(f'reset-filters-{chart_id}', 'n_clicks')],
                [State(f'filter-{filter_id}-{chart_id}', 'value') 
                 for filter_id in ['category', 'range', 'threshold']],
                prevent_initial_call=True
            )
            def update_chart_filters(apply_clicks, reset_clicks, *filter_values):
                ctx = callback_context
                if not ctx.triggered:
                    return no_update
                
                button_id = ctx.triggered[0]['prop_id'].split('.')[0]
                
                if f'reset-filters-{chart_id}' in button_id:
                    # 重置为原始数据
                    return self._get_original_figure(chart_id)
                
                if f'apply-filters-{chart_id}' in button_id:
                    # 应用筛选
                    return self._apply_filters_to_chart(chart_id, filter_values)
                
                return no_update
        
        # 为已知图表创建筛选回调
        known_chart_ids = ['scatter-plot', 'heatmap', 'bar-chart']
        for chart_id in known_chart_ids:
            try:
                create_filter_callback(chart_id)
            except:
                pass
    
    def _register_chart_statistics_callbacks(self):
        """注册图表统计回调"""
        
        @self.app.callback(
            [Output('global-selection-stats', 'children'),
             Output('crossfilter-status', 'children')],
            [Input(f'selection-store-{chart_id}', 'data') 
             for chart_id in ['scatter-plot', 'heatmap', 'bar-chart']],
            prevent_initial_call=True
        )
        def update_global_statistics(*selection_data_list):
            """更新全局统计信息"""
            
            active_selections = [data for data in selection_data_list if data]
            
            if not active_selections:
                return [
                    html.P("暂无数据选择", style={'color': '#666'})
                ], [
                    html.Span("🔗 交叉筛选: 未激活", style={'color': '#666'})
                ]
            
            # 合并所有选择
            total_points = sum(len(data.get('indices', [])) for data in active_selections)
            active_charts = len(active_selections)
            
            stats_content = [
                html.Div([
                    html.H6("🎯 全局选择统计"),
                    html.P(f"已选择 {total_points} 个数据点"),
                    html.P(f"涉及 {active_charts} 个图表"),
                    html.Hr(),
                    html.H6("📊 详细信息"),
                ])
            ]
            
            for data in active_selections:
                chart_info = html.Div([
                    html.Strong(f"图表: {data['chart_id']}"),
                    html.Br(),
                    html.Small(f"选中点数: {len(data.get('indices', []))}"),
                    html.Br(),
                    html.Small(f"更新时间: {data.get('timestamp', 'Unknown')[:19]}"),
                    html.Hr()
                ])
                stats_content.append(chart_info)
            
            crossfilter_status = [
                html.Span("🔗 交叉筛选: 已激活", style={'color': '#28a745'})
            ]
            
            return stats_content, crossfilter_status
    
    def _register_crossfilter_callbacks(self):
        """注册交叉筛选回调"""
        
        @self.app.callback(
            [Output(f'chart-{chart_id}', 'figure') for chart_id in ['scatter-plot', 'heatmap', 'bar-chart']],
            [Input('enable-crossfilter', 'value'),
             Input(f'selection-store-{chart_id}', 'data') 
             for chart_id in ['scatter-plot', 'heatmap', 'bar-chart']],
            [State(f'chart-{chart_id}', 'figure') for chart_id in ['scatter-plot', 'heatmap', 'bar-chart']],
            prevent_initial_call=True
        )
        def handle_crossfilter(enable_crossfilter, *args):
            """处理交叉筛选逻辑"""
            
            if not enable_crossfilter or 'crossfilter' not in enable_crossfilter:
                return [no_update] * 3
            
            # 分离输入参数
            mid_point = len(args) // 2
            selection_data_list = args[:mid_point]
            figure_states = args[mid_point:]
            
            updated_figures = []
            
            for i, (selection_data, current_figure) in enumerate(zip(selection_data_list, figure_states)):
                if not selection_data or not current_figure:
                    updated_figures.append(no_update)
                    continue
                
                # 应用交叉筛选效果
                updated_figure = self._apply_crossfilter_highlight(
                    current_figure, selection_data, i
                )
                updated_figures.append(updated_figure)
            
            return updated_figures
    
    def _create_selection_statistics(self, chart_id: str, points: List[Dict], 
                                   indices: List[int]) -> List:
        """创建选择统计信息"""
        
        stats = []
        
        # 基础统计
        stats.append(html.H6("📊 选择统计"))
        stats.append(html.P(f"选中点数: {len(points)}"))
        
        # 提取数值数据进行统计
        numeric_values = []
        for point in points:
            if 'y' in point and isinstance(point['y'], (int, float)):
                numeric_values.append(point['y'])
            elif 'z' in point and isinstance(point['z'], (int, float)):
                numeric_values.append(point['z'])
        
        if numeric_values:
            stats.extend([
                html.Hr(),
                html.H6("📈 数值统计"),
                html.P(f"均值: {np.mean(numeric_values):.3f}"),
                html.P(f"中位数: {np.median(numeric_values):.3f}"),
                html.P(f"标准差: {np.std(numeric_values):.3f}"),
                html.P(f"范围: {np.min(numeric_values):.3f} - {np.max(numeric_values):.3f}")
            ])
        
        # 分类统计
        category_values = []
        for point in points:
            if 'text' in point:
                category_values.append(point['text'])
            elif 'hovertext' in point:
                category_values.append(point['hovertext'])
        
        if category_values:
            unique_categories = list(set(category_values))
            stats.extend([
                html.Hr(),
                html.H6("🏷️ 分类统计"),
                html.P(f"类别数: {len(unique_categories)}"),
                html.Div([
                    html.Small(f"• {cat}", style={'display': 'block'}) 
                    for cat in unique_categories[:5]
                ] + ([html.Small("...", style={'display': 'block'})] if len(unique_categories) > 5 else []))
            ])
        
        # 操作按钮
        stats.extend([
            html.Hr(),
            html.Div([
                html.Button([
                    html.I(className="fas fa-copy"),
                    " 复制数据"
                ], id=f"copy-selection-{chart_id}", 
                   className="btn btn-sm btn-outline-primary",
                   style={'marginRight': '5px'}),
                
                html.Button([
                    html.I(className="fas fa-download"),
                    " 导出选择"
                ], id=f"export-selection-{chart_id}", 
                   className="btn btn-sm btn-outline-success")
            ])
        ])
        
        return stats
    
    def _export_chart(self, figure: Dict, chart_id: str, export_format: str):
        """导出图表"""
        
        try:
            if export_format == 'data':
                # 导出数据
                if 'data' in figure:
                    data_frames = []
                    for trace in figure['data']:
                        if 'x' in trace and 'y' in trace:
                            df = pd.DataFrame({
                                'x': trace['x'],
                                'y': trace['y']
                            })
                            if 'text' in trace:
                                df['text'] = trace['text']
                            data_frames.append(df)
                    
                    if data_frames:
                        combined_df = pd.concat(data_frames, ignore_index=True)
                        return dcc.send_data_frame(
                            combined_df.to_csv, 
                            f"{chart_id}_data.csv", 
                            index=False
                        )
            
            elif export_format in ['png', 'svg', 'pdf']:
                # 导出图像 (简化版本)
                filename = f"{chart_id}_chart.{export_format}"
                
                # 生成占位符内容
                placeholder_content = f"# {chart_id} Chart Export\n\nChart exported in {export_format} format\nTimestamp: {pd.Timestamp.now()}"
                
                return dict(
                    content=placeholder_content,
                    filename=filename,
                    type='text/plain'
                )
            
            elif export_format == 'html':
                # 导出HTML
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>{chart_id} Chart</title>
                    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                </head>
                <body>
                    <div id="chart" style="width:100%;height:600px;"></div>
                    <script>
                        Plotly.newPlot('chart', {json.dumps(figure['data'])}, {json.dumps(figure['layout'])});
                    </script>
                </body>
                </html>
                """
                
                return dict(
                    content=html_content,
                    filename=f"{chart_id}_chart.html",
                    type='text/html'
                )
        
        except Exception as e:
            print(f"Export error: {e}")
            return no_update
        
        return no_update
    
    def _get_original_figure(self, chart_id: str) -> Dict:
        """获取原始图表"""
        # 这里应该从缓存或重新生成原始图表
        # 简化版本返回空的更新
        return no_update
    
    def _apply_filters_to_chart(self, chart_id: str, filter_values: List) -> Dict:
        """应用筛选到图表"""
        # 简化版本，实际应用中需要根据筛选值更新图表数据
        return no_update
    
    def _apply_crossfilter_highlight(self, figure: Dict, selection_data: Dict, 
                                   chart_index: int) -> Dict:
        """应用交叉筛选高亮效果"""
        
        if not figure or not selection_data:
            return figure
        
        try:
            updated_figure = figure.copy()
            
            # 在其他图表中高亮选中的数据点
            for trace in updated_figure.get('data', []):
                if 'marker' in trace:
                    # 添加高亮效果
                    trace['marker'].update({
                        'line': dict(width=2, color='orange'),
                        'opacity': 0.7
                    })
            
            return updated_figure
            
        except Exception as e:
            print(f"Crossfilter error: {e}")
            return figure

def register_chart_callbacks(app: dash.Dash):
    """注册所有图表交互回调"""
    callback_manager = ChartCallbackManager(app)
    callback_manager.register_all_callbacks()
    return callback_manager