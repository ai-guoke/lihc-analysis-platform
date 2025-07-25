"""
Smart Analysis Recommendation System
智能分析推荐系统 - 基于数据特征和用户行为推荐最佳分析方法
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path

@dataclass
class AnalysisRecommendation:
    """分析推荐结构"""
    analysis_type: str
    confidence: float
    reason: str
    description: str
    estimated_time: str
    complexity: str  # 'beginner', 'intermediate', 'advanced'
    prerequisites: List[str]
    expected_outputs: List[str]
    priority: int  # 1-5, 5 being highest

class SmartRecommendationEngine:
    """智能推荐引擎"""
    
    def __init__(self):
        self.analysis_templates = self._load_analysis_templates()
        self.user_history = {}
        self.data_patterns = {}
        
    def _load_analysis_templates(self) -> Dict:
        """加载分析模板"""
        return {
            'differential_expression': {
                'name': '差异表达分析',
                'description': '识别在不同条件下表达差异显著的基因',
                'data_requirements': ['expression', 'clinical'],
                'min_samples': 6,
                'optimal_samples': 20,
                'time_estimate': '5-15分钟',
                'complexity': 'beginner',
                'outputs': ['差异基因列表', '火山图', '热图', 'GO富集分析'],
                'use_cases': ['比较肿瘤vs正常组织', '药物处理前后对比', '不同疾病分期对比']
            },
            
            'survival_analysis': {
                'name': '生存分析',
                'description': '评估基因表达对患者预后的影响',
                'data_requirements': ['expression', 'clinical_survival'],
                'min_samples': 15,
                'optimal_samples': 50,
                'time_estimate': '3-10分钟',
                'complexity': 'intermediate',
                'outputs': ['Kaplan-Meier曲线', '风险评估', 'Cox回归结果'],
                'use_cases': ['预后标志物筛选', '治疗效果评估', '风险分层']
            },
            
            'network_analysis': {
                'name': '网络分析',
                'description': '构建基因共表达网络，识别关键调控节点',
                'data_requirements': ['expression'],
                'min_samples': 20,
                'optimal_samples': 100,
                'time_estimate': '10-30分钟',
                'complexity': 'advanced',
                'outputs': ['网络图', '中心性分析', '模块检测', '关键基因识别'],
                'use_cases': ['调控网络重构', '关键驱动基因发现', '通路分析']
            },
            
            'immune_analysis': {
                'name': '免疫微环境分析',
                'description': '评估肿瘤免疫微环境特征和免疫细胞浸润',
                'data_requirements': ['expression'],
                'min_samples': 10,
                'optimal_samples': 30,
                'time_estimate': '8-20分钟',
                'complexity': 'intermediate',
                'outputs': ['免疫评分', '免疫细胞浸润', '免疫检查点分析'],
                'use_cases': ['免疫治疗预测', '免疫状态评估', '免疫逃逸机制']
            },
            
            'drug_response': {
                'name': '药物响应预测',
                'description': '基于分子特征预测药物敏感性',
                'data_requirements': ['expression', 'mutation'],
                'min_samples': 15,
                'optimal_samples': 40,
                'time_estimate': '15-45分钟',
                'complexity': 'advanced',
                'outputs': ['敏感性评分', '耐药机制', '替代药物推荐'],
                'use_cases': ['个性化用药指导', '耐药性预测', '药物重定位']
            },
            
            'molecular_subtyping': {
                'name': '分子亚型分类',
                'description': '基于多组学数据进行疾病分子分型',
                'data_requirements': ['expression', 'clinical'],
                'min_samples': 30,
                'optimal_samples': 100,
                'time_estimate': '20-60分钟',
                'complexity': 'advanced',
                'outputs': ['亚型分类', '特征基因', '预后差异', '治疗策略'],
                'use_cases': ['精准分型', '个性化治疗', '预后评估']
            },
            
            'pathway_analysis': {
                'name': '通路富集分析',
                'description': '识别显著富集的生物学通路和功能',
                'data_requirements': ['expression'],
                'min_samples': 6,
                'optimal_samples': 20,
                'time_estimate': '5-15分钟',
                'complexity': 'beginner',
                'outputs': ['富集通路', '功能注释', '通路网络', '关键基因'],
                'use_cases': ['功能解释', '机制探索', '通路富集']
            },
            
            'multi_omics_integration': {
                'name': '多组学整合分析',
                'description': '整合多种组学数据进行综合分析',
                'data_requirements': ['expression', 'mutation', 'clinical'],
                'min_samples': 25,
                'optimal_samples': 80,
                'time_estimate': '30-90分钟',
                'complexity': 'advanced',
                'outputs': ['整合网络', '关键特征', '预测模型', '生物学洞察'],
                'use_cases': ['系统生物学', '综合诊断', '多维度分析']
            }
        }
    
    def analyze_dataset_characteristics(self, dataset_info: Dict) -> Dict:
        """分析数据集特征"""
        
        characteristics = {
            'sample_size': dataset_info.get('samples', 0),
            'feature_count': dataset_info.get('genes', 0),
            'data_types': dataset_info.get('features', {}),
            'quality_score': 0.0,
            'completeness': 0.0,
            'data_balance': 0.0
        }
        
        # 计算数据质量评分
        sample_score = min(1.0, characteristics['sample_size'] / 50)  # 50样本为满分
        feature_score = min(1.0, characteristics['feature_count'] / 20000)  # 20k基因为满分
        
        # 数据类型完整性
        data_types = characteristics['data_types']
        type_score = 0
        if data_types.get('has_expression', False):
            type_score += 0.4
        if data_types.get('has_clinical', False):
            type_score += 0.3
        if data_types.get('has_mutation', False):
            type_score += 0.2
        if data_types.get('has_methylation', False):
            type_score += 0.1
        
        characteristics['quality_score'] = (sample_score + feature_score + type_score) / 3
        characteristics['completeness'] = type_score
        
        return characteristics
    
    def generate_recommendations(self, dataset_info: Dict, 
                               user_preferences: Dict = None,
                               analysis_history: List = None) -> List[AnalysisRecommendation]:
        """生成分析推荐"""
        
        dataset_chars = self.analyze_dataset_characteristics(dataset_info)
        recommendations = []
        
        for analysis_id, template in self.analysis_templates.items():
            recommendation = self._evaluate_analysis_fit(
                analysis_id, template, dataset_chars, 
                user_preferences, analysis_history
            )
            
            if recommendation:
                recommendations.append(recommendation)
        
        # 按优先级和置信度排序
        recommendations.sort(key=lambda x: (x.priority, x.confidence), reverse=True)
        
        return recommendations[:8]  # 返回前8个推荐
    
    def _evaluate_analysis_fit(self, analysis_id: str, template: Dict, 
                              dataset_chars: Dict, user_preferences: Dict = None,
                              analysis_history: List = None) -> Optional[AnalysisRecommendation]:
        """评估分析的适合度"""
        
        # 检查数据要求
        data_types = dataset_chars['data_types']
        required_types = template['data_requirements']
        
        missing_types = []
        for req_type in required_types:
            if req_type == 'expression' and not data_types.get('has_expression', False):
                missing_types.append('基因表达数据')
            elif req_type == 'clinical' and not data_types.get('has_clinical', False):
                missing_types.append('临床数据')
            elif req_type == 'clinical_survival' and not data_types.get('has_clinical', False):
                missing_types.append('生存数据')
            elif req_type == 'mutation' and not data_types.get('has_mutation', False):
                missing_types.append('突变数据')
        
        # 如果缺少必需数据类型，降低置信度
        if missing_types:
            confidence_penalty = len(missing_types) * 0.3
        else:
            confidence_penalty = 0
        
        # 检查样本数量
        sample_size = dataset_chars['sample_size']
        min_samples = template['min_samples']
        optimal_samples = template['optimal_samples']
        
        if sample_size < min_samples:
            sample_confidence = 0.3  # 样本不足，低置信度
            sample_reason = f"样本数量({sample_size})少于推荐最小值({min_samples})"
        elif sample_size < optimal_samples:
            sample_confidence = 0.5 + 0.3 * (sample_size - min_samples) / (optimal_samples - min_samples)
            sample_reason = f"样本数量({sample_size})接近推荐值"
        else:
            sample_confidence = 0.8 + 0.2 * min(1, (sample_size - optimal_samples) / optimal_samples)
            sample_reason = f"样本数量({sample_size})充足"
        
        # 基础置信度计算
        base_confidence = sample_confidence - confidence_penalty
        
        # 用户偏好调整
        preference_boost = 0
        if user_preferences:
            if user_preferences.get('complexity_preference') == template['complexity']:
                preference_boost += 0.1
            if analysis_id in user_preferences.get('preferred_analyses', []):
                preference_boost += 0.2
        
        # 历史分析调整
        history_penalty = 0
        if analysis_history:
            recent_analyses = [a for a in analysis_history if a['analysis_type'] == analysis_id]
            if len(recent_analyses) > 2:  # 如果最近做过多次相同分析，降低推荐
                history_penalty = 0.1
        
        final_confidence = max(0.1, min(1.0, base_confidence + preference_boost - history_penalty))
        
        # 生成推荐理由
        reasons = []
        if not missing_types:
            reasons.append("✅ 数据类型匹配")
        else:
            reasons.append(f"⚠️ 缺少: {', '.join(missing_types)}")
        
        reasons.append(sample_reason)
        
        if dataset_chars['quality_score'] > 0.7:
            reasons.append("✅ 数据质量良好")
        elif dataset_chars['quality_score'] > 0.5:
            reasons.append("🔸 数据质量中等")
        else:
            reasons.append("⚠️ 数据质量需要改善")
        
        # 确定优先级
        if final_confidence > 0.8:
            priority = 5
        elif final_confidence > 0.6:
            priority = 4
        elif final_confidence > 0.4:
            priority = 3
        elif final_confidence > 0.2:
            priority = 2
        else:
            priority = 1
        
        return AnalysisRecommendation(
            analysis_type=analysis_id,
            confidence=final_confidence,
            reason="; ".join(reasons),
            description=template['description'],
            estimated_time=template['time_estimate'],
            complexity=template['complexity'],
            prerequisites=missing_types,
            expected_outputs=template['outputs'],
            priority=priority
        )
    
    def get_analysis_workflow_suggestion(self, recommendations: List[AnalysisRecommendation]) -> Dict:
        """建议分析工作流程"""
        
        # 按复杂度和依赖关系排序
        beginner_analyses = [r for r in recommendations if r.complexity == 'beginner']
        intermediate_analyses = [r for r in recommendations if r.complexity == 'intermediate']
        advanced_analyses = [r for r in recommendations if r.complexity == 'advanced']
        
        workflow = {
            'recommended_order': [],
            'parallel_groups': [],
            'total_estimated_time': '0分钟',
            'description': ''
        }
        
        # 构建推荐顺序
        order = []
        
        # 1. 先做基础分析
        if beginner_analyses:
            order.extend([r.analysis_type for r in beginner_analyses[:2]])
        
        # 2. 再做中级分析
        if intermediate_analyses:
            order.extend([r.analysis_type for r in intermediate_analyses[:2]])
        
        # 3. 最后做高级分析
        if advanced_analyses:
            order.extend([r.analysis_type for r in advanced_analyses[:1]])
        
        workflow['recommended_order'] = order
        
        # 识别可并行的分析
        parallel_groups = []
        if len(beginner_analyses) > 1:
            parallel_groups.append([r.analysis_type for r in beginner_analyses])
        
        workflow['parallel_groups'] = parallel_groups
        
        # 估算总时间
        total_minutes = 0
        for rec in recommendations[:len(order)]:
            time_str = rec.estimated_time
            # 简单解析时间字符串 (例如: "5-15分钟")
            if '-' in time_str and '分钟' in time_str:
                time_parts = time_str.replace('分钟', '').split('-')
                avg_time = (int(time_parts[0]) + int(time_parts[1])) / 2
                total_minutes += avg_time
        
        workflow['total_estimated_time'] = f"{int(total_minutes)}分钟"
        
        # 生成描述
        if len(order) > 0:
            workflow['description'] = f"""
            建议按以下顺序进行分析：
            1. 从基础分析开始建立数据概览
            2. 进行中级分析深入理解数据
            3. 最后进行高级分析获得深层洞察
            
            预计总耗时约 {workflow['total_estimated_time']}
            """
        
        return workflow
    
    def get_contextual_tips(self, analysis_type: str, dataset_info: Dict) -> List[str]:
        """获取上下文相关的分析提示"""
        
        tips = []
        template = self.analysis_templates.get(analysis_type, {})
        sample_size = dataset_info.get('samples', 0)
        
        # 样本数量相关提示
        if sample_size < template.get('min_samples', 0):
            tips.append(f"💡 当前样本数量({sample_size})较少，结果可能不够稳定，建议增加样本或降低统计阈值")
        
        if sample_size > template.get('optimal_samples', 50):
            tips.append(f"✨ 样本数量({sample_size})充足，可以进行更深入的子群分析")
        
        # 数据类型相关提示
        data_types = dataset_info.get('features', {})
        
        if analysis_type == 'survival_analysis' and not data_types.get('has_clinical'):
            tips.append("⚠️ 生存分析需要临床数据，建议先上传包含生存信息的临床数据")
        
        if analysis_type == 'drug_response' and not data_types.get('has_mutation'):
            tips.append("💊 添加突变数据可以显著提高药物响应预测的准确性")
        
        if analysis_type == 'immune_analysis':
            tips.append("🛡️ 免疫分析结果可以与生存分析结合，评估免疫微环境对预后的影响")
        
        # 复杂度相关提示
        complexity = template.get('complexity', 'beginner')
        if complexity == 'advanced':
            tips.append("🚀 这是高级分析，建议先完成基础分析建立数据概览")
        
        if complexity == 'beginner':
            tips.append("🎯 这是入门级分析，适合快速了解数据特征")
        
        # 通用提示
        tips.append("📊 分析完成后，可以在可视化页面查看详细结果")
        tips.append("💾 记得保存分析结果以便后续比较和引用")
        
        return tips[:4]  # 返回最多4个提示

# 全局实例
recommendation_engine = SmartRecommendationEngine()