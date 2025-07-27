"""
Specialized Immune Cell Analysis Module
专项免疫细胞分析模块

核心功能：
1. TAMs (肿瘤相关巨噬细胞) 分析
   - M1/M2极化状态评分
   - 极化转换关键因子识别
   - TAMs密度与预后关联

2. Tregs (调节性T细胞) 功能分析
   - 抑制功能评分系统
   - FOXP3+细胞浸润程度
   - 免疫抑制强度评估

3. CD8+ T细胞状态分析
   - 耗竭状态标志物（PD-1, TIM-3, LAG-3等）
   - 细胞毒性功能评分
   - 克隆扩增分析

4. CAFs (癌相关成纤维细胞) 分析
   - 亚型分类 (iCAFs, myCAFs, apCAFs)
   - 基质激活程度评分
   - 基质硬度/张力评估
   - 药物渗透屏障分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class TAMsAnalyzer:
    """肿瘤相关巨噬细胞分析器"""
    
    def __init__(self):
        self.m1_markers = self._load_m1_markers()
        self.m2_markers = self._load_m2_markers()
        self.polarization_factors = self._load_polarization_factors()
        self.analysis_results = {}
        
    def _load_m1_markers(self) -> List[str]:
        """加载M1型巨噬细胞标记基因"""
        return [
            # 经典M1标记
            'CD68', 'CD80', 'CD86', 'ITGAX',  # 表面标记
            'IL1B', 'IL6', 'TNF', 'IL12A', 'IL12B', 'IL23A',  # 促炎细胞因子
            'NOS2', 'PTGS2', 'CXCL9', 'CXCL10', 'CXCL11',  # 效应分子
            'IRF5', 'IRF8', 'STAT1', 'NFKB1', 'RELA',  # 转录因子
            'CCR7', 'TLR2', 'TLR4', 'TLR7', 'TLR8',  # 受体
            'SOCS1', 'SOCS3', 'IDO1', 'INDO',  # 调节因子
            # 抗肿瘤功能
            'TRAIL', 'FAS', 'FASL', 'CASP1', 'CASP3',
            'GZMB', 'PRF1', 'IFNG', 'CD40', 'CD40LG'
        ]
    
    def _load_m2_markers(self) -> List[str]:
        """加载M2型巨噬细胞标记基因"""
        return [
            # 经典M2标记  
            'CD163', 'CD206', 'MRC1', 'MSR1',  # 表面标记
            'ARG1', 'ARG2', 'ALOX15', 'CHI3L1',  # 代谢酶
            'IL10', 'TGFB1', 'IL1RN', 'IL4R', 'IL13RA1',  # 抗炎因子
            'CCL17', 'CCL18', 'CCL22', 'CCL24', 'CXCL13',  # 趋化因子
            'IRF4', 'STAT6', 'STAT3', 'KLF4', 'PPARG',  # 转录因子
            'VEGFA', 'VEGFB', 'VEGFC', 'PDGFA', 'PDGFB',  # 血管生成
            'MMP9', 'MMP12', 'TIMP1', 'TIMP2',  # 基质重塑
            # 促肿瘤功能
            'CSF1R', 'CSF2RA', 'MARCO', 'STAB1',
            'EGF', 'HGF', 'IGF1', 'FGF2', 'ANGPT1', 'ANGPT2'
        ]
        
    def _load_polarization_factors(self) -> Dict[str, List[str]]:
        """加载极化转换关键因子"""
        return {
            'm1_inducers': [
                # Th1细胞因子
                'IFNG', 'TNF', 'IL2', 'IL12A', 'IL12B',
                # 病原体识别
                'TLR4', 'TLR2', 'TLR7', 'TLR8', 'TLR9',
                # 转录调节
                'IRF5', 'IRF8', 'STAT1', 'NFKB1', 'NFKB2',
                # 信号通路
                'JAK1', 'JAK2', 'TYK2', 'MAPK1', 'MAPK8'
            ],
            'm2_inducers': [
                # Th2细胞因子
                'IL4', 'IL13', 'IL10', 'TGFB1',
                # 抗炎信号
                'IL1RN', 'SOCS1', 'SOCS3', 'TNFAIP3',
                # 转录调节
                'IRF4', 'STAT6', 'STAT3', 'KLF4', 'PPARG',
                # 代谢调节
                'ARNT', 'HIF1A', 'PPARA', 'SREBF1'
            ],
            'plasticity_factors': [
                # 极化转换关键因子
                'NOTCH1', 'NOTCH2', 'JAG1', 'DLL1',
                'WNT3A', 'WNT5A', 'CTNNB1', 'GSK3B',
                'SMAD2', 'SMAD3', 'SMAD4', 'SMAD7',
                'FOXO1', 'FOXO3', 'SIRT1', 'TP53'
            ]
        }
    
    def analyze_tams_polarization(self, expression_data: pd.DataFrame, 
                                 clinical_data: pd.DataFrame,
                                 os_time_col: str = 'os_time',
                                 os_status_col: str = 'os_status') -> Dict:
        """
        分析TAMs极化状态与预后关联
        
        Args:
            expression_data: 基因表达数据 (genes x samples)
            clinical_data: 临床数据
            os_time_col: 总生存时间列名
            os_status_col: 生存状态列名
            
        Returns:
            Dict: TAMs极化分析结果
        """
        results = {}
        
        print("正在进行TAMs极化分析...")
        
        # 计算M1/M2评分
        m1_score = self._calculate_polarization_score(expression_data, self.m1_markers, 'M1')
        m2_score = self._calculate_polarization_score(expression_data, self.m2_markers, 'M2')
        
        # 计算M1/M2比值
        m1_m2_ratio = m1_score / (m2_score + 1e-6)  # 避免除零
        
        # 分析与预后的关联
        m1_prognosis = self._analyze_score_prognosis(
            m1_score, clinical_data, os_time_col, os_status_col, 'M1_Score'
        )
        
        m2_prognosis = self._analyze_score_prognosis(
            m2_score, clinical_data, os_time_col, os_status_col, 'M2_Score'
        )
        
        ratio_prognosis = self._analyze_score_prognosis(
            m1_m2_ratio, clinical_data, os_time_col, os_status_col, 'M1_M2_Ratio'
        )
        
        # 分析极化关键因子
        polarization_analysis = self._analyze_polarization_factors(
            expression_data, clinical_data, os_time_col, os_status_col
        )
        
        # TAMs密度分析
        tams_density = self._analyze_tams_density(expression_data)
        
        results = {
            'polarization_scores': {
                'M1_score': m1_score,
                'M2_score': m2_score,
                'M1_M2_ratio': m1_m2_ratio
            },
            'prognostic_associations': {
                'M1_prognosis': m1_prognosis,
                'M2_prognosis': m2_prognosis,
                'ratio_prognosis': ratio_prognosis
            },
            'polarization_factors': polarization_analysis,
            'tams_density': tams_density,
            'marker_availability': {
                'M1_markers_available': len([g for g in self.m1_markers if g in expression_data.index]),
                'M2_markers_available': len([g for g in self.m2_markers if g in expression_data.index]),
                'total_M1_markers': len(self.m1_markers),
                'total_M2_markers': len(self.m2_markers)
            }
        }
        
        self.analysis_results = results
        return results
    
    def _calculate_polarization_score(self, expression_data: pd.DataFrame, 
                                    markers: List[str], score_type: str) -> pd.Series:
        """计算极化评分"""
        # 获取可用标记基因
        available_markers = [gene for gene in markers if gene in expression_data.index]
        
        if len(available_markers) == 0:
            print(f"警告：{score_type}标记基因均不可用")
            return pd.Series(0.0, index=expression_data.columns)
        
        print(f"{score_type}评分使用 {len(available_markers)}/{len(markers)} 个标记基因")
        
        # 提取标记基因表达
        marker_expr = expression_data.loc[available_markers]
        
        # 标准化
        scaler = StandardScaler()
        marker_expr_scaled = pd.DataFrame(
            scaler.fit_transform(marker_expr.T).T,
            index=marker_expr.index,
            columns=marker_expr.columns
        )
        
        # 计算平均评分
        score = marker_expr_scaled.mean(axis=0)
        
        return score
    
    def _analyze_score_prognosis(self, score: pd.Series, clinical_data: pd.DataFrame,
                               os_time_col: str, os_status_col: str, 
                               score_name: str) -> Dict:
        """分析评分与预后的关联"""
        try:
            # 匹配样本
            common_samples = list(set(score.index) & set(clinical_data.index))
            if len(common_samples) < 10:
                return {'error': '样本数量不足'}
            
            score_matched = score.loc[common_samples]
            clinical_matched = clinical_data.loc[common_samples]
            
            # 检查数据完整性
            if clinical_matched[os_time_col].isna().any() or clinical_matched[os_status_col].isna().any():
                return {'error': '临床数据不完整'}
            
            # 按中位数分组
            median_score = score_matched.median()
            high_score_group = score_matched > median_score
            
            # 生存分析
            high_group_clinical = clinical_matched[high_score_group]
            low_group_clinical = clinical_matched[~high_score_group]
            
            if len(high_group_clinical) < 3 or len(low_group_clinical) < 3:
                return {'error': '分组样本数量不足'}
            
            # 计算生存统计
            high_events = high_group_clinical[os_status_col].sum()
            high_total = len(high_group_clinical)
            low_events = low_group_clinical[os_status_col].sum()
            low_total = len(low_group_clinical)
            
            # 计算HR
            high_event_rate = high_events / high_total if high_total > 0 else 0
            low_event_rate = low_events / low_total if low_total > 0 else 0
            
            if low_event_rate == 0:
                hr = float('inf') if high_event_rate > 0 else 1.0
            else:
                hr = high_event_rate / low_event_rate
            
            # 卡方检验
            contingency_table = [
                [high_events, high_total - high_events],
                [low_events, low_total - low_events]
            ]
            chi2, p_value = stats.chi2_contingency(contingency_table)[:2]
            
            # 计算置信区间
            if high_events > 0 and low_events > 0:
                log_hr = np.log(hr)
                se_log_hr = np.sqrt(1/high_events + 1/low_events)
                ci_lower = np.exp(log_hr - 1.96 * se_log_hr)
                ci_upper = np.exp(log_hr + 1.96 * se_log_hr)
            else:
                ci_lower, ci_upper = 0, float('inf')
            
            return {
                'score_name': score_name,
                'median_score': median_score,
                'hr': hr,
                'p_value': p_value,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'high_score_events': int(high_events),
                'high_score_total': int(high_total),
                'low_score_events': int(low_events),
                'low_score_total': int(low_total),
                'high_score_event_rate': high_event_rate,
                'low_score_event_rate': low_event_rate
            }
            
        except Exception as e:
            return {'error': f'分析失败: {str(e)}'}
    
    def _analyze_polarization_factors(self, expression_data: pd.DataFrame,
                                    clinical_data: pd.DataFrame,
                                    os_time_col: str, os_status_col: str) -> Dict:
        """分析极化关键因子"""
        results = {}
        
        for factor_type, factors in self.polarization_factors.items():
            factor_results = []
            
            for factor in factors:
                if factor in expression_data.index:
                    # 分析该因子与预后的关联
                    factor_prognosis = self._analyze_score_prognosis(
                        expression_data.loc[factor], clinical_data,
                        os_time_col, os_status_col, factor
                    )
                    
                    if 'error' not in factor_prognosis:
                        factor_prognosis['factor'] = factor
                        factor_results.append(factor_prognosis)
            
            # 按显著性排序
            if factor_results:
                factor_df = pd.DataFrame(factor_results)
                factor_df = factor_df[factor_df['p_value'] < 0.05].sort_values('p_value')
                results[factor_type] = factor_df.head(10).to_dict('records')
            else:
                results[factor_type] = []
        
        return results
    
    def _analyze_tams_density(self, expression_data: pd.DataFrame) -> Dict:
        """分析TAMs密度"""
        # 计算TAMs总体密度评分
        all_tams_markers = list(set(self.m1_markers + self.m2_markers))
        available_tams_markers = [gene for gene in all_tams_markers if gene in expression_data.index]
        
        if len(available_tams_markers) == 0:
            return {'error': 'TAMs标记基因不可用'}
        
        # 计算密度评分
        tams_expr = expression_data.loc[available_tams_markers]
        density_score = tams_expr.mean(axis=0)
        
        # 计算样本排名
        density_percentiles = density_score.rank(pct=True)
        
        # 分类密度等级
        density_categories = pd.cut(
            density_percentiles,
            bins=[0, 0.25, 0.5, 0.75, 1.0],
            labels=['Low', 'Medium-Low', 'Medium-High', 'High']
        )
        
        return {
            'density_score': density_score,
            'density_percentiles': density_percentiles,
            'density_categories': density_categories,
            'markers_used': available_tams_markers,
            'n_markers': len(available_tams_markers)
        }
    
    def classify_tams_phenotype(self, expression_data: pd.DataFrame) -> pd.DataFrame:
        """TAMs表型分类"""
        if not hasattr(self, 'analysis_results') or not self.analysis_results:
            raise ValueError("请先运行 analyze_tams_polarization 方法")
        
        scores = self.analysis_results['polarization_scores']
        m1_score = scores['M1_score']
        m2_score = scores['M2_score']
        m1_m2_ratio = scores['M1_M2_ratio']
        
        classification = pd.DataFrame(index=expression_data.columns)
        
        # 基于M1/M2比值分类
        ratio_median = m1_m2_ratio.median()
        ratio_q75 = m1_m2_ratio.quantile(0.75)
        ratio_q25 = m1_m2_ratio.quantile(0.25)
        
        conditions = [
            m1_m2_ratio >= ratio_q75,
            (m1_m2_ratio >= ratio_median) & (m1_m2_ratio < ratio_q75),
            (m1_m2_ratio >= ratio_q25) & (m1_m2_ratio < ratio_median),
            m1_m2_ratio < ratio_q25
        ]
        
        labels = ['M1-dominant', 'M1-biased', 'M2-biased', 'M2-dominant']
        
        classification['TAMs_phenotype'] = np.select(conditions, labels)
        classification['M1_score'] = m1_score
        classification['M2_score'] = m2_score
        classification['M1_M2_ratio'] = m1_m2_ratio
        
        # 添加密度信息
        if 'tams_density' in self.analysis_results:
            density_info = self.analysis_results['tams_density']
            if 'density_score' in density_info:
                classification['TAMs_density'] = density_info['density_score']
                classification['density_category'] = density_info['density_categories']
        
        return classification
    
    def get_tams_summary_report(self) -> Dict:
        """生成TAMs分析总结报告"""
        if not self.analysis_results:
            return {"error": "请先运行分析"}
        
        summary = {
            'analysis_type': 'TAMs Polarization Analysis',
            'markers_summary': self.analysis_results['marker_availability'],
            'prognostic_summary': {},
            'key_findings': []
        }
        
        # 预后关联总结
        prog_results = self.analysis_results['prognostic_associations']
        
        for score_type, result in prog_results.items():
            if 'error' not in result:
                summary['prognostic_summary'][score_type] = {
                    'hr': result['hr'],
                    'p_value': result['p_value'],
                    'significant': result['p_value'] < 0.05
                }
                
                # 关键发现
                if result['p_value'] < 0.05:
                    direction = "高风险" if result['hr'] > 1 else "保护因子"
                    summary['key_findings'].append(
                        f"{result['score_name']}: HR={result['hr']:.3f}, P={result['p_value']:.3e} ({direction})"
                    )
        
        # 极化因子总结
        polarization_summary = {}
        for factor_type, factors in self.analysis_results['polarization_factors'].items():
            significant_factors = [f for f in factors if f.get('p_value', 1) < 0.05]
            polarization_summary[factor_type] = {
                'total_factors': len(factors),
                'significant_factors': len(significant_factors),
                'top_factors': [f['factor'] for f in significant_factors[:5]]
            }
        
        summary['polarization_factors_summary'] = polarization_summary
        
        return summary


class TregsAnalyzer:
    """调节性T细胞分析器"""
    
    def __init__(self):
        self.tregs_markers = self._load_tregs_markers()
        self.suppression_markers = self._load_suppression_markers()
        
    def _load_tregs_markers(self) -> List[str]:
        """加载Tregs标记基因"""
        return [
            # 核心标记
            'FOXP3', 'IL2RA', 'IKZF2', 'IKZF4',
            # 表面标记
            'CD25', 'CTLA4', 'TNFRSF18', 'TNFRSF4', 'TNFRSF9',
            'LAG3', 'TIGIT', 'HAVCR2', 'PDCD1',
            # 功能分子
            'IL10', 'TGFB1', 'GZMB', 'PRF1', 'GZMA',
            # 趋化受体
            'CCR4', 'CCR5', 'CCR6', 'CCR7', 'CCR8', 'CXCR3'
        ]
    
    def _load_suppression_markers(self) -> List[str]:
        """加载免疫抑制功能标记"""
        return [
            'IL10', 'TGFB1', 'IL35', 'IDO1', 'IDO2',
            'CTLA4', 'PD1', 'LAG3', 'TIGIT', 'TIM3',
            'GZMB', 'PRF1', 'TRAIL', 'FAS', 'FASL'
        ]
    
    def analyze_tregs_function(self, expression_data: pd.DataFrame, 
                              clinical_data: pd.DataFrame,
                              os_time_col: str = 'os_time',
                              os_status_col: str = 'os_status') -> Dict:
        """
        分析Tregs功能与预后关联
        
        Args:
            expression_data: 基因表达数据 (genes x samples)
            clinical_data: 临床数据
            os_time_col: 总生存时间列名
            os_status_col: 生存状态列名
            
        Returns:
            Dict: Tregs功能分析结果
        """
        results = {}
        
        print("正在进行Tregs功能分析...")
        
        # 计算Tregs浸润评分
        tregs_score = self._calculate_tregs_infiltration_score(expression_data)
        
        # 计算抑制功能评分
        suppression_score = self._calculate_suppression_score(expression_data)
        
        # 计算FOXP3+ Tregs密度
        foxp3_density = self._calculate_foxp3_density(expression_data)
        
        # 计算Tregs/CD8比值
        tregs_cd8_ratio = self._calculate_tregs_cd8_ratio(expression_data)
        
        # 分析与预后的关联
        tregs_prognosis = self._analyze_score_prognosis(
            tregs_score, clinical_data, os_time_col, os_status_col, 'Tregs_Score'
        )
        
        suppression_prognosis = self._analyze_score_prognosis(
            suppression_score, clinical_data, os_time_col, os_status_col, 'Suppression_Score'
        )
        
        foxp3_prognosis = self._analyze_score_prognosis(
            foxp3_density, clinical_data, os_time_col, os_status_col, 'FOXP3_Density'
        )
        
        ratio_prognosis = self._analyze_score_prognosis(
            tregs_cd8_ratio, clinical_data, os_time_col, os_status_col, 'Tregs_CD8_Ratio'
        )
        
        # 免疫抑制状态评估
        immune_suppression_status = self._assess_immune_suppression_status(
            tregs_score, suppression_score, tregs_cd8_ratio
        )
        
        results = {
            'functional_scores': {
                'tregs_score': tregs_score,
                'suppression_score': suppression_score,
                'foxp3_density': foxp3_density,
                'tregs_cd8_ratio': tregs_cd8_ratio
            },
            'prognostic_associations': {
                'tregs_prognosis': tregs_prognosis,
                'suppression_prognosis': suppression_prognosis,
                'foxp3_prognosis': foxp3_prognosis,
                'ratio_prognosis': ratio_prognosis
            },
            'immune_suppression_status': immune_suppression_status,
            'marker_availability': {
                'tregs_markers_available': len([g for g in self.tregs_markers if g in expression_data.index]),
                'suppression_markers_available': len([g for g in self.suppression_markers if g in expression_data.index]),
                'total_tregs_markers': len(self.tregs_markers),
                'total_suppression_markers': len(self.suppression_markers)
            }
        }
        
        return results
    
    def _calculate_tregs_infiltration_score(self, expression_data: pd.DataFrame) -> pd.Series:
        """计算Tregs浸润评分"""
        available_markers = [gene for gene in self.tregs_markers if gene in expression_data.index]
        
        if len(available_markers) == 0:
            print("警告：Tregs标记基因均不可用")
            return pd.Series(0.0, index=expression_data.columns)
        
        print(f"Tregs浸润评分使用 {len(available_markers)}/{len(self.tregs_markers)} 个标记基因")
        
        marker_expr = expression_data.loc[available_markers]
        scaler = StandardScaler()
        marker_expr_scaled = pd.DataFrame(
            scaler.fit_transform(marker_expr.T).T,
            index=marker_expr.index,
            columns=marker_expr.columns
        )
        
        return marker_expr_scaled.mean(axis=0)
    
    def _calculate_suppression_score(self, expression_data: pd.DataFrame) -> pd.Series:
        """计算免疫抑制功能评分"""
        available_markers = [gene for gene in self.suppression_markers if gene in expression_data.index]
        
        if len(available_markers) == 0:
            print("警告：免疫抑制标记基因均不可用")
            return pd.Series(0.0, index=expression_data.columns)
        
        print(f"免疫抑制评分使用 {len(available_markers)}/{len(self.suppression_markers)} 个标记基因")
        
        marker_expr = expression_data.loc[available_markers]
        scaler = StandardScaler()
        marker_expr_scaled = pd.DataFrame(
            scaler.fit_transform(marker_expr.T).T,
            index=marker_expr.index,
            columns=marker_expr.columns
        )
        
        return marker_expr_scaled.mean(axis=0)
    
    def _calculate_foxp3_density(self, expression_data: pd.DataFrame) -> pd.Series:
        """计算FOXP3+ Tregs密度"""
        if 'FOXP3' in expression_data.index:
            return expression_data.loc['FOXP3']
        else:
            print("警告：FOXP3基因不可用")
            return pd.Series(0.0, index=expression_data.columns)
    
    def _calculate_tregs_cd8_ratio(self, expression_data: pd.DataFrame) -> pd.Series:
        """计算Tregs/CD8比值"""
        # 计算Tregs评分
        tregs_score = self._calculate_tregs_infiltration_score(expression_data)
        
        # 计算CD8+ T细胞评分
        cd8_markers = ['CD8A', 'CD8B', 'CD3E', 'CD3D']
        available_cd8 = [gene for gene in cd8_markers if gene in expression_data.index]
        
        if len(available_cd8) == 0:
            print("警告：CD8标记基因均不可用")
            return pd.Series(1.0, index=expression_data.columns)
        
        cd8_expr = expression_data.loc[available_cd8]
        cd8_score = cd8_expr.mean(axis=0)
        
        # 计算比值，避免除零
        ratio = tregs_score / (cd8_score + 1e-6)
        return ratio
    
    def _analyze_score_prognosis(self, score: pd.Series, clinical_data: pd.DataFrame,
                                os_time_col: str, os_status_col: str, 
                                score_name: str) -> Dict:
        """分析评分与预后的关联（复用TAMs中的方法）"""
        try:
            # 匹配样本
            common_samples = list(set(score.index) & set(clinical_data.index))
            if len(common_samples) < 10:
                return {'error': '样本数量不足'}
            
            score_matched = score.loc[common_samples]
            clinical_matched = clinical_data.loc[common_samples]
            
            # 检查数据完整性
            if clinical_matched[os_time_col].isna().any() or clinical_matched[os_status_col].isna().any():
                return {'error': '临床数据不完整'}
            
            # 按中位数分组
            median_score = score_matched.median()
            high_score_group = score_matched > median_score
            
            # 生存分析
            high_group_clinical = clinical_matched[high_score_group]
            low_group_clinical = clinical_matched[~high_score_group]
            
            if len(high_group_clinical) < 3 or len(low_group_clinical) < 3:
                return {'error': '分组样本数量不足'}
            
            # 计算生存统计
            high_events = high_group_clinical[os_status_col].sum()
            high_total = len(high_group_clinical)
            low_events = low_group_clinical[os_status_col].sum()
            low_total = len(low_group_clinical)
            
            # 计算HR
            high_event_rate = high_events / high_total if high_total > 0 else 0
            low_event_rate = low_events / low_total if low_total > 0 else 0
            
            if low_event_rate == 0:
                hr = float('inf') if high_event_rate > 0 else 1.0
            else:
                hr = high_event_rate / low_event_rate
            
            # 卡方检验
            contingency_table = [
                [high_events, high_total - high_events],
                [low_events, low_total - low_events]
            ]
            chi2, p_value = stats.chi2_contingency(contingency_table)[:2]
            
            # 计算置信区间
            if high_events > 0 and low_events > 0:
                log_hr = np.log(hr)
                se_log_hr = np.sqrt(1/high_events + 1/low_events)
                ci_lower = np.exp(log_hr - 1.96 * se_log_hr)
                ci_upper = np.exp(log_hr + 1.96 * se_log_hr)
            else:
                ci_lower, ci_upper = 0, float('inf')
            
            return {
                'score_name': score_name,
                'median_score': median_score,
                'hr': hr,
                'p_value': p_value,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'high_score_events': int(high_events),
                'high_score_total': int(high_total),
                'low_score_events': int(low_events),
                'low_score_total': int(low_total),
                'high_score_event_rate': high_event_rate,
                'low_score_event_rate': low_event_rate
            }
            
        except Exception as e:
            return {'error': f'分析失败: {str(e)}'}
    
    def _assess_immune_suppression_status(self, tregs_score: pd.Series, 
                                        suppression_score: pd.Series,
                                        tregs_cd8_ratio: pd.Series) -> pd.DataFrame:
        """评估免疫抑制状态"""
        status_df = pd.DataFrame(index=tregs_score.index)
        
        # 计算综合抑制指数
        suppression_index = (tregs_score + suppression_score + tregs_cd8_ratio) / 3
        
        # 分层
        q25 = suppression_index.quantile(0.25)
        q50 = suppression_index.quantile(0.50)
        q75 = suppression_index.quantile(0.75)
        
        conditions = [
            suppression_index >= q75,
            (suppression_index >= q50) & (suppression_index < q75),
            (suppression_index >= q25) & (suppression_index < q50),
            suppression_index < q25
        ]
        
        labels = ['High-Suppression', 'Moderate-Suppression', 'Low-Suppression', 'Minimal-Suppression']
        
        status_df['immune_suppression_status'] = np.select(conditions, labels)
        status_df['suppression_index'] = suppression_index
        status_df['tregs_score'] = tregs_score
        status_df['suppression_score'] = suppression_score
        status_df['tregs_cd8_ratio'] = tregs_cd8_ratio
        
        return status_df


class CD8TAnalyzer:
    """CD8+ T细胞分析器"""
    
    def __init__(self):
        self.cd8_markers = self._load_cd8_markers()
        self.exhaustion_markers = self._load_exhaustion_markers()
        self.cytotoxicity_markers = self._load_cytotoxicity_markers()
        
    def _load_cd8_markers(self) -> List[str]:
        """加载CD8+ T细胞标记基因"""
        return [
            'CD8A', 'CD8B', 'CD3E', 'CD3D', 'CD3G',
            'TCF7', 'LEF1', 'IL7R', 'CCR7', 'SELL'
        ]
    
    def _load_exhaustion_markers(self) -> List[str]:
        """加载T细胞耗竭标记"""
        return [
            'PDCD1', 'HAVCR2', 'LAG3', 'TIGIT', 'CTLA4',
            'CD244', 'CD160', 'BTLA', 'KLRG1', 'CD57'
        ]
    
    def _load_cytotoxicity_markers(self) -> List[str]:
        """加载细胞毒性标记"""
        return [
            'GZMA', 'GZMB', 'GZMH', 'GZMK', 'PRF1',
            'IFNG', 'TNF', 'IL2', 'GNLY', 'NKG7'
        ]
    
    def _load_memory_markers(self) -> List[str]:
        """加载记忆性T细胞标记"""
        return [
            # 中央记忆T细胞 (TCM)
            'CCR7', 'CD45RA', 'IL7R', 'CD62L', 'SELL',
            # 效应记忆T细胞 (TEM)  
            'CD45RO', 'CCR5', 'CXCR3', 'CX3CR1',
            # 组织驻留记忆T细胞 (TRM)
            'CD69', 'CD103', 'ITGAE', 'CD49A', 'ITGA1'
        ]
    
    def _load_activation_markers(self) -> List[str]:
        """加载激活标记"""
        return [
            'CD25', 'CD69', 'CD71', 'ICOS', 'OX40',
            'CD137', '4-1BB', 'GITR', 'CD27', 'CD28'
        ]
    
    def analyze_cd8t_state(self, expression_data: pd.DataFrame, 
                          clinical_data: pd.DataFrame,
                          os_time_col: str = 'os_time',
                          os_status_col: str = 'os_status') -> Dict:
        """
        分析CD8+ T细胞状态与功能
        
        Args:
            expression_data: 基因表达数据 (genes x samples)
            clinical_data: 临床数据
            os_time_col: 总生存时间列名
            os_status_col: 生存状态列名
            
        Returns:
            Dict: CD8+ T细胞状态分析结果
        """
        results = {}
        
        print("正在进行CD8+ T细胞状态分析...")
        
        # 计算各种评分
        infiltration_score = self._calculate_cd8t_infiltration_score(expression_data)
        exhaustion_score = self._calculate_exhaustion_score(expression_data)
        cytotoxicity_score = self._calculate_cytotoxicity_score(expression_data)
        memory_score = self._calculate_memory_score(expression_data)
        activation_score = self._calculate_activation_score(expression_data)
        
        # 计算功能效力指数
        functional_potency = self._calculate_functional_potency(
            cytotoxicity_score, exhaustion_score, activation_score
        )
        
        # 分析与预后的关联
        infiltration_prognosis = self._analyze_score_prognosis(
            infiltration_score, clinical_data, os_time_col, os_status_col, 'CD8T_Infiltration'
        )
        
        exhaustion_prognosis = self._analyze_score_prognosis(
            exhaustion_score, clinical_data, os_time_col, os_status_col, 'CD8T_Exhaustion'
        )
        
        cytotoxicity_prognosis = self._analyze_score_prognosis(
            cytotoxicity_score, clinical_data, os_time_col, os_status_col, 'CD8T_Cytotoxicity'
        )
        
        functional_prognosis = self._analyze_score_prognosis(
            functional_potency, clinical_data, os_time_col, os_status_col, 'CD8T_Functional_Potency'
        )
        
        # 免疫治疗响应潜力评估
        immunotherapy_potential = self._assess_immunotherapy_potential(
            functional_potency, exhaustion_score, infiltration_score
        )
        
        results = {
            'functional_scores': {
                'infiltration_score': infiltration_score,
                'exhaustion_score': exhaustion_score,
                'cytotoxicity_score': cytotoxicity_score,
                'memory_score': memory_score,
                'activation_score': activation_score,
                'functional_potency': functional_potency
            },
            'prognostic_associations': {
                'infiltration_prognosis': infiltration_prognosis,
                'exhaustion_prognosis': exhaustion_prognosis,
                'cytotoxicity_prognosis': cytotoxicity_prognosis,
                'functional_prognosis': functional_prognosis
            },
            'immunotherapy_potential': immunotherapy_potential,
            'marker_availability': {
                'cd8_markers_available': len([g for g in self.cd8_markers if g in expression_data.index]),
                'exhaustion_markers_available': len([g for g in self.exhaustion_markers if g in expression_data.index]),
                'cytotoxicity_markers_available': len([g for g in self.cytotoxicity_markers if g in expression_data.index]),
                'total_cd8_markers': len(self.cd8_markers),
                'total_exhaustion_markers': len(self.exhaustion_markers),
                'total_cytotoxicity_markers': len(self.cytotoxicity_markers)
            }
        }
        
        return results
    
    def _calculate_cd8t_infiltration_score(self, expression_data: pd.DataFrame) -> pd.Series:
        """计算CD8+ T细胞浸润评分"""
        available_markers = [gene for gene in self.cd8_markers if gene in expression_data.index]
        
        if len(available_markers) == 0:
            print("警告：CD8+ T细胞标记基因均不可用")
            return pd.Series(0.0, index=expression_data.columns)
        
        print(f"CD8+ T细胞浸润评分使用 {len(available_markers)}/{len(self.cd8_markers)} 个标记基因")
        
        marker_expr = expression_data.loc[available_markers]
        scaler = StandardScaler()
        marker_expr_scaled = pd.DataFrame(
            scaler.fit_transform(marker_expr.T).T,
            index=marker_expr.index,
            columns=marker_expr.columns
        )
        
        return marker_expr_scaled.mean(axis=0)
    
    def _calculate_exhaustion_score(self, expression_data: pd.DataFrame) -> pd.Series:
        """计算T细胞耗竭评分"""
        available_markers = [gene for gene in self.exhaustion_markers if gene in expression_data.index]
        
        if len(available_markers) == 0:
            print("警告：T细胞耗竭标记基因均不可用")
            return pd.Series(0.0, index=expression_data.columns)
        
        print(f"T细胞耗竭评分使用 {len(available_markers)}/{len(self.exhaustion_markers)} 个标记基因")
        
        marker_expr = expression_data.loc[available_markers]
        scaler = StandardScaler()
        marker_expr_scaled = pd.DataFrame(
            scaler.fit_transform(marker_expr.T).T,
            index=marker_expr.index,
            columns=marker_expr.columns
        )
        
        return marker_expr_scaled.mean(axis=0)
    
    def _calculate_cytotoxicity_score(self, expression_data: pd.DataFrame) -> pd.Series:
        """计算细胞毒性功能评分"""
        available_markers = [gene for gene in self.cytotoxicity_markers if gene in expression_data.index]
        
        if len(available_markers) == 0:
            print("警告：细胞毒性标记基因均不可用")
            return pd.Series(0.0, index=expression_data.columns)
        
        print(f"细胞毒性评分使用 {len(available_markers)}/{len(self.cytotoxicity_markers)} 个标记基因")
        
        marker_expr = expression_data.loc[available_markers]
        scaler = StandardScaler()
        marker_expr_scaled = pd.DataFrame(
            scaler.fit_transform(marker_expr.T).T,
            index=marker_expr.index,
            columns=marker_expr.columns
        )
        
        return marker_expr_scaled.mean(axis=0)
    
    def _calculate_memory_score(self, expression_data: pd.DataFrame) -> pd.Series:
        """计算记忆性T细胞评分"""
        memory_markers = self._load_memory_markers()
        available_markers = [gene for gene in memory_markers if gene in expression_data.index]
        
        if len(available_markers) == 0:
            print("警告：记忆性T细胞标记基因均不可用")
            return pd.Series(0.0, index=expression_data.columns)
        
        print(f"记忆性T细胞评分使用 {len(available_markers)}/{len(memory_markers)} 个标记基因")
        
        marker_expr = expression_data.loc[available_markers]
        scaler = StandardScaler()
        marker_expr_scaled = pd.DataFrame(
            scaler.fit_transform(marker_expr.T).T,
            index=marker_expr.index,
            columns=marker_expr.columns
        )
        
        return marker_expr_scaled.mean(axis=0)
    
    def _calculate_activation_score(self, expression_data: pd.DataFrame) -> pd.Series:
        """计算激活状态评分"""
        activation_markers = self._load_activation_markers()
        available_markers = [gene for gene in activation_markers if gene in expression_data.index]
        
        if len(available_markers) == 0:
            print("警告：激活标记基因均不可用")
            return pd.Series(0.0, index=expression_data.columns)
        
        print(f"激活状态评分使用 {len(available_markers)}/{len(activation_markers)} 个标记基因")
        
        marker_expr = expression_data.loc[available_markers]
        scaler = StandardScaler()
        marker_expr_scaled = pd.DataFrame(
            scaler.fit_transform(marker_expr.T).T,
            index=marker_expr.index,
            columns=marker_expr.columns
        )
        
        return marker_expr_scaled.mean(axis=0)
    
    def _calculate_functional_potency(self, cytotoxicity_score: pd.Series, 
                                    exhaustion_score: pd.Series, 
                                    activation_score: pd.Series) -> pd.Series:
        """计算功能效力指数"""
        # 功能效力 = (细胞毒性 + 激活状态) - 耗竭状态
        potency = (cytotoxicity_score + activation_score) / 2 - exhaustion_score
        return potency
    
    def _assess_immunotherapy_potential(self, functional_potency: pd.Series,
                                      exhaustion_score: pd.Series,
                                      infiltration_score: pd.Series) -> pd.DataFrame:
        """评估免疫治疗响应潜力"""
        potential_df = pd.DataFrame(index=functional_potency.index)
        
        # 计算综合响应潜力指数
        # 高浸润 + 高功能效力 + 低耗竭 = 高响应潜力
        response_potential = (infiltration_score + functional_potency - exhaustion_score) / 3
        
        # 分层评估
        q25 = response_potential.quantile(0.25)
        q50 = response_potential.quantile(0.50)
        q75 = response_potential.quantile(0.75)
        
        conditions = [
            response_potential >= q75,
            (response_potential >= q50) & (response_potential < q75),
            (response_potential >= q25) & (response_potential < q50),
            response_potential < q25
        ]
        
        labels = ['High-Response', 'Moderate-Response', 'Low-Response', 'Poor-Response']
        
        potential_df['immunotherapy_response_potential'] = np.select(conditions, labels)
        potential_df['response_potential_index'] = response_potential
        potential_df['infiltration_score'] = infiltration_score
        potential_df['functional_potency'] = functional_potency
        potential_df['exhaustion_score'] = exhaustion_score
        
        # 预测PD-1/PD-L1抑制剂响应
        pd1_potential = self._predict_pd1_response(exhaustion_score, infiltration_score)
        potential_df['pd1_response_prediction'] = pd1_potential
        
        return potential_df
    
    def _predict_pd1_response(self, exhaustion_score: pd.Series, 
                            infiltration_score: pd.Series) -> pd.Series:
        """预测PD-1/PD-L1抑制剂响应"""
        # 中等耗竭 + 高浸润 = 最佳PD-1响应
        # 过度耗竭或无浸润 = 较差PD-1响应
        
        normalized_exhaustion = (exhaustion_score - exhaustion_score.min()) / (exhaustion_score.max() - exhaustion_score.min())
        normalized_infiltration = (infiltration_score - infiltration_score.min()) / (infiltration_score.max() - infiltration_score.min())
        
        # 中等耗竭范围 (0.3-0.7)
        optimal_exhaustion = 1 - np.abs(normalized_exhaustion - 0.5) * 2
        
        # PD-1响应 = 中等耗竭状态 * 高浸润状态
        pd1_response = optimal_exhaustion * normalized_infiltration
        
        return pd1_response
    
    def _analyze_score_prognosis(self, score: pd.Series, clinical_data: pd.DataFrame,
                                os_time_col: str, os_status_col: str, 
                                score_name: str) -> Dict:
        """分析评分与预后的关联（复用之前的方法）"""
        try:
            # 匹配样本
            common_samples = list(set(score.index) & set(clinical_data.index))
            if len(common_samples) < 10:
                return {'error': '样本数量不足'}
            
            score_matched = score.loc[common_samples]
            clinical_matched = clinical_data.loc[common_samples]
            
            # 检查数据完整性
            if clinical_matched[os_time_col].isna().any() or clinical_matched[os_status_col].isna().any():
                return {'error': '临床数据不完整'}
            
            # 按中位数分组
            median_score = score_matched.median()
            high_score_group = score_matched > median_score
            
            # 生存分析
            high_group_clinical = clinical_matched[high_score_group]
            low_group_clinical = clinical_matched[~high_score_group]
            
            if len(high_group_clinical) < 3 or len(low_group_clinical) < 3:
                return {'error': '分组样本数量不足'}
            
            # 计算生存统计
            high_events = high_group_clinical[os_status_col].sum()
            high_total = len(high_group_clinical)
            low_events = low_group_clinical[os_status_col].sum()
            low_total = len(low_group_clinical)
            
            # 计算HR
            high_event_rate = high_events / high_total if high_total > 0 else 0
            low_event_rate = low_events / low_total if low_total > 0 else 0
            
            if low_event_rate == 0:
                hr = float('inf') if high_event_rate > 0 else 1.0
            else:
                hr = high_event_rate / low_event_rate
            
            # 卡方检验
            contingency_table = [
                [high_events, high_total - high_events],
                [low_events, low_total - low_events]
            ]
            chi2, p_value = stats.chi2_contingency(contingency_table)[:2]
            
            # 计算置信区间
            if high_events > 0 and low_events > 0:
                log_hr = np.log(hr)
                se_log_hr = np.sqrt(1/high_events + 1/low_events)
                ci_lower = np.exp(log_hr - 1.96 * se_log_hr)
                ci_upper = np.exp(log_hr + 1.96 * se_log_hr)
            else:
                ci_lower, ci_upper = 0, float('inf')
            
            return {
                'score_name': score_name,
                'median_score': median_score,
                'hr': hr,
                'p_value': p_value,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'high_score_events': int(high_events),
                'high_score_total': int(high_total),
                'low_score_events': int(low_events),
                'low_score_total': int(low_total),
                'high_score_event_rate': high_event_rate,
                'low_score_event_rate': low_event_rate
            }
            
        except Exception as e:
            return {'error': f'分析失败: {str(e)}'}


# Import CAFs analyzer
from .cafs_analyzer import CAFsAnalyzer
