"""
CAFs (Cancer-Associated Fibroblasts) Analysis Module
癌相关成纤维细胞分析模块

核心功能：
1. CAFs亚型分类 (iCAFs, myCAFs, apCAFs)
2. 基质激活程度评分
3. 基质硬度/张力评估
4. 药物渗透屏障分析
5. 抗纤维化治疗靶点识别
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class CAFsAnalyzer:
    """癌相关成纤维细胞分析器"""
    
    def __init__(self):
        self.icafs_markers = self._load_icafs_markers()
        self.mycafs_markers = self._load_mycafs_markers()
        self.apcafs_markers = self._load_apcafs_markers()
        self.stromal_function_markers = self._load_stromal_function_markers()
        
    def _load_icafs_markers(self) -> List[str]:
        """加载炎症型CAFs (iCAFs) 标记基因"""
        return [
            # 核心炎症标记
            'IL6', 'IL8', 'CXCL8', 'IL1B', 'TNF',
            # 趋化因子
            'CCL2', 'CCL5', 'CCL20', 'CXCL1', 'CXCL2', 'CXCL12',
            # 生长因子受体
            'PDGFRA', 'PDGFRB', 'FGFR1', 'EGFR',
            # 炎症信号通路
            'NFKB1', 'RELA', 'STAT3', 'IRF1', 'IRF3',
            # 补体系统
            'C3', 'CFB', 'C1S', 'C1R',
            # 其他功能分子
            'PTGS2', 'NOS2', 'TNFAIP3', 'SOCS3'
        ]
    
    def _load_mycafs_markers(self) -> List[str]:
        """加载肌成纤维型CAFs (myCAFs) 标记基因"""
        return [
            # 肌动蛋白系统
            'ACTA2', 'ACTG2', 'MYH11', 'MYL9',
            # 收缩蛋白
            'TAGLN', 'TAGLN2', 'CNN1', 'CALD1',
            # 肌球蛋白
            'MYL6', 'MYL12A', 'MYL12B', 'MYLK',
            # 胶原合成
            'COL1A1', 'COL1A2', 'COL3A1', 'COL5A1', 'COL6A1',
            # 基质重塑
            'MMP2', 'MMP11', 'MMP14', 'TIMP1', 'TIMP2',
            # 交联酶
            'LOX', 'LOXL1', 'LOXL2', 'LOXL4',
            # 收缩调节
            'TPM1', 'TPM2', 'MYLPF', 'ACTBP2'
        ]
    
    def _load_apcafs_markers(self) -> List[str]:
        """加载抗原呈递型CAFs (apCAFs) 标记基因"""
        return [
            # MHC II类分子
            'HLA-DRA', 'HLA-DRB1', 'HLA-DQA1', 'HLA-DQB1',
            'HLA-DPA1', 'HLA-DPB1',
            # 抗原加工
            'CD74', 'CTSS', 'CTSL', 'CTSD',
            # 共刺激分子
            'CD80', 'CD86', 'CD40', 'ICOS',
            # 细胞因子
            'IL12A', 'IL12B', 'IL15', 'IL18',
            # 趋化因子
            'CCL19', 'CCL21', 'CXCL9', 'CXCL10',
            # 其他功能分子
            'SLPI', 'C3', 'CFI', 'SERPING1',
            # 免疫调节
            'IDO1', 'TNFSF4', 'TNFRSF14', 'ICOSLG'
        ]
    
    def _load_stromal_function_markers(self) -> Dict[str, List[str]]:
        """加载基质功能标记基因"""
        return {
            'collagen_synthesis': [
                'COL1A1', 'COL1A2', 'COL3A1', 'COL4A1', 'COL5A1',
                'COL6A1', 'COL6A2', 'COL8A1', 'COL12A1', 'COL14A1'
            ],
            'matrix_remodeling': [
                'MMP1', 'MMP2', 'MMP3', 'MMP9', 'MMP11', 'MMP14',
                'TIMP1', 'TIMP2', 'TIMP3', 'TIMP4',
                'PLOD1', 'PLOD2', 'PLOD3', 'P4HA1', 'P4HA2'
            ],
            'matrix_crosslinking': [
                'LOX', 'LOXL1', 'LOXL2', 'LOXL3', 'LOXL4',
                'TGM2', 'TGM3', 'PXDN', 'ALDH1A1'
            ],
            'angiogenesis_support': [
                'VEGFA', 'VEGFB', 'VEGFC', 'ANGPT1', 'ANGPT2',
                'PDGFA', 'PDGFB', 'FGF2', 'HGF', 'EGF'
            ],
            'immune_regulation': [
                'TGFB1', 'TGFB2', 'IL10', 'IDO1', 'IDO2',
                'CD274', 'PDCD1LG2', 'ENTPD1', 'NT5E', 'ADORA2A'
            ],
            'metabolic_support': [
                'GLUT1', 'SLC1A5', 'GLS', 'ASNS', 'PHGDH',
                'PSAT1', 'PSPH', 'SHMT2', 'MTHFD2', 'ALDH18A1'
            ],
            'drug_resistance': [
                'ABCB1', 'ABCC1', 'ABCG2', 'SLC22A3',
                'CYP1A1', 'CYP1B1', 'GSR', 'GSTA1', 'GSTP1'
            ]
        }
    
    def analyze_cafs_subtypes(self, expression_data: pd.DataFrame, 
                             clinical_data: pd.DataFrame,
                             os_time_col: str = 'os_time',
                             os_status_col: str = 'os_status') -> Dict:
        """
        分析CAFs亚型分布与功能
        
        Args:
            expression_data: 基因表达数据 (genes x samples)
            clinical_data: 临床数据
            os_time_col: 总生存时间列名
            os_status_col: 生存状态列名
            
        Returns:
            Dict: CAFs亚型分析结果
        """
        results = {}
        
        print("正在进行CAFs亚型分析...")
        
        # 计算各亚型评分
        icafs_score = self._calculate_cafs_subtype_score(expression_data, self.icafs_markers, 'iCAFs')
        mycafs_score = self._calculate_cafs_subtype_score(expression_data, self.mycafs_markers, 'myCAFs')
        apcafs_score = self._calculate_cafs_subtype_score(expression_data, self.apcafs_markers, 'apCAFs')
        
        # 计算基质激活评分
        stromal_activation = self._calculate_stromal_activation_score(expression_data)
        
        # 分析与预后的关联
        icafs_prognosis = self._analyze_score_prognosis(
            icafs_score, clinical_data, os_time_col, os_status_col, 'iCAFs_Score'
        )
        
        mycafs_prognosis = self._analyze_score_prognosis(
            mycafs_score, clinical_data, os_time_col, os_status_col, 'myCAFs_Score'
        )
        
        apcafs_prognosis = self._analyze_score_prognosis(
            apcafs_score, clinical_data, os_time_col, os_status_col, 'apCAFs_Score'
        )
        
        stromal_prognosis = self._analyze_score_prognosis(
            stromal_activation, clinical_data, os_time_col, os_status_col, 'Stromal_Activation'
        )
        
        # 分析基质功能
        stromal_functions = self._analyze_stromal_functions(
            expression_data, clinical_data, os_time_col, os_status_col
        )
        
        # CAFs亚型分类
        cafs_classification = self._classify_cafs_subtypes(
            icafs_score, mycafs_score, apcafs_score
        )
        
        # 基质硬度评估
        matrix_stiffness = self._assess_matrix_stiffness(expression_data)
        
        # 药物渗透屏障分析
        drug_barrier = self._analyze_drug_penetration_barrier(expression_data)
        
        results = {
            'subtype_scores': {
                'icafs_score': icafs_score,
                'mycafs_score': mycafs_score,
                'apcafs_score': apcafs_score,
                'stromal_activation': stromal_activation
            },
            'prognostic_associations': {
                'icafs_prognosis': icafs_prognosis,
                'mycafs_prognosis': mycafs_prognosis,
                'apcafs_prognosis': apcafs_prognosis,
                'stromal_prognosis': stromal_prognosis
            },
            'stromal_functions': stromal_functions,
            'cafs_classification': cafs_classification,
            'matrix_stiffness': matrix_stiffness,
            'drug_barrier': drug_barrier,
            'marker_availability': {
                'icafs_markers_available': len([g for g in self.icafs_markers if g in expression_data.index]),
                'mycafs_markers_available': len([g for g in self.mycafs_markers if g in expression_data.index]),
                'apcafs_markers_available': len([g for g in self.apcafs_markers if g in expression_data.index]),
                'total_icafs_markers': len(self.icafs_markers),
                'total_mycafs_markers': len(self.mycafs_markers),
                'total_apcafs_markers': len(self.apcafs_markers)
            }
        }
        
        return results
    
    def _calculate_cafs_subtype_score(self, expression_data: pd.DataFrame, 
                                    markers: List[str], subtype: str) -> pd.Series:
        """计算CAFs亚型评分"""
        # 获取可用标记基因
        available_markers = [gene for gene in markers if gene in expression_data.index]
        
        if len(available_markers) == 0:
            print(f"警告：{subtype}标记基因均不可用")
            return pd.Series(0.0, index=expression_data.columns)
        
        print(f"{subtype}评分使用 {len(available_markers)}/{len(markers)} 个标记基因")
        
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
    
    def _calculate_stromal_activation_score(self, expression_data: pd.DataFrame) -> pd.Series:
        """计算基质激活综合评分"""
        # 合并所有CAFs标记
        all_cafs_markers = list(set(self.icafs_markers + self.mycafs_markers + self.apcafs_markers))
        available_markers = [gene for gene in all_cafs_markers if gene in expression_data.index]
        
        if len(available_markers) == 0:
            print("警告：基质激活标记基因均不可用")
            return pd.Series(0.0, index=expression_data.columns)
        
        print(f"基质激活评分使用 {len(available_markers)}/{len(all_cafs_markers)} 个标记基因")
        
        marker_expr = expression_data.loc[available_markers]
        scaler = StandardScaler()
        marker_expr_scaled = pd.DataFrame(
            scaler.fit_transform(marker_expr.T).T,
            index=marker_expr.index,
            columns=marker_expr.columns
        )
        
        return marker_expr_scaled.mean(axis=0)
    
    def _analyze_stromal_functions(self, expression_data: pd.DataFrame,
                                 clinical_data: pd.DataFrame,
                                 os_time_col: str, os_status_col: str) -> Dict:
        """分析基质功能与预后关联"""
        function_results = {}
        
        for function_name, function_markers in self.stromal_function_markers.items():
            # 计算功能评分
            available_markers = [gene for gene in function_markers if gene in expression_data.index]
            
            if len(available_markers) > 0:
                marker_expr = expression_data.loc[available_markers]
                function_score = marker_expr.mean(axis=0)
                
                # 分析与预后的关联
                prognosis = self._analyze_score_prognosis(
                    function_score, clinical_data, os_time_col, os_status_col, function_name
                )
                
                function_results[function_name] = {
                    'score': function_score,
                    'prognosis': prognosis,
                    'markers_used': available_markers,
                    'markers_available': len(available_markers),
                    'total_markers': len(function_markers)
                }
        
        return function_results
    
    def _classify_cafs_subtypes(self, icafs_score: pd.Series, 
                              mycafs_score: pd.Series, 
                              apcafs_score: pd.Series) -> pd.DataFrame:
        """CAFs亚型分类"""
        classification = pd.DataFrame(index=icafs_score.index)
        
        # 计算相对评分
        total_score = icafs_score + mycafs_score + apcafs_score
        
        # 避免除零
        total_score = total_score.replace(0, 1e-6)
        
        icafs_ratio = icafs_score / total_score
        mycafs_ratio = mycafs_score / total_score
        apcafs_ratio = apcafs_score / total_score
        
        # 分类逻辑：占主导地位的亚型
        conditions = [
            (icafs_ratio >= 0.4) & (icafs_ratio >= mycafs_ratio) & (icafs_ratio >= apcafs_ratio),
            (mycafs_ratio >= 0.4) & (mycafs_ratio >= icafs_ratio) & (mycafs_ratio >= apcafs_ratio),
            (apcafs_ratio >= 0.4) & (apcafs_ratio >= icafs_ratio) & (apcafs_ratio >= mycafs_ratio),
            True  # Mixed type
        ]
        
        labels = ['iCAFs-dominant', 'myCAFs-dominant', 'apCAFs-dominant', 'Mixed-CAFs']
        
        classification['cafs_subtype'] = np.select(conditions, labels)
        classification['icafs_ratio'] = icafs_ratio
        classification['mycafs_ratio'] = mycafs_ratio
        classification['apcafs_ratio'] = apcafs_ratio
        classification['icafs_score'] = icafs_score
        classification['mycafs_score'] = mycafs_score
        classification['apcafs_score'] = apcafs_score
        
        return classification
    
    def _assess_matrix_stiffness(self, expression_data: pd.DataFrame) -> pd.DataFrame:
        """评估基质硬度"""
        stiffness_df = pd.DataFrame(index=expression_data.columns)
        
        # 胶原合成评分
        collagen_markers = self.stromal_function_markers['collagen_synthesis']
        available_collagen = [gene for gene in collagen_markers if gene in expression_data.index]
        
        if available_collagen:
            collagen_score = expression_data.loc[available_collagen].mean(axis=0)
        else:
            collagen_score = pd.Series(0.0, index=expression_data.columns)
        
        # 交联评分
        crosslink_markers = self.stromal_function_markers['matrix_crosslinking']
        available_crosslink = [gene for gene in crosslink_markers if gene in expression_data.index]
        
        if available_crosslink:
            crosslink_score = expression_data.loc[available_crosslink].mean(axis=0)
        else:
            crosslink_score = pd.Series(0.0, index=expression_data.columns)
        
        # 基质硬度指数
        stiffness_index = (collagen_score + crosslink_score) / 2
        
        # 分层
        q25 = stiffness_index.quantile(0.25)
        q50 = stiffness_index.quantile(0.50)
        q75 = stiffness_index.quantile(0.75)
        
        conditions = [
            stiffness_index >= q75,
            (stiffness_index >= q50) & (stiffness_index < q75),
            (stiffness_index >= q25) & (stiffness_index < q50),
            stiffness_index < q25
        ]
        
        labels = ['High-Stiffness', 'Moderate-Stiffness', 'Low-Stiffness', 'Soft-Matrix']
        
        stiffness_df['matrix_stiffness'] = np.select(conditions, labels)
        stiffness_df['stiffness_index'] = stiffness_index
        stiffness_df['collagen_score'] = collagen_score
        stiffness_df['crosslink_score'] = crosslink_score
        
        return stiffness_df
    
    def _analyze_drug_penetration_barrier(self, expression_data: pd.DataFrame) -> pd.DataFrame:
        """分析药物渗透屏障"""
        barrier_df = pd.DataFrame(index=expression_data.columns)
        
        # 物理屏障：胶原密度
        collagen_markers = self.stromal_function_markers['collagen_synthesis']
        available_collagen = [gene for gene in collagen_markers if gene in expression_data.index]
        
        if available_collagen:
            physical_barrier = expression_data.loc[available_collagen].mean(axis=0)
        else:
            physical_barrier = pd.Series(0.0, index=expression_data.columns)
        
        # 代谢屏障：药物代谢酶
        metabolic_markers = self.stromal_function_markers['drug_resistance']
        available_metabolic = [gene for gene in metabolic_markers if gene in expression_data.index]
        
        if available_metabolic:
            metabolic_barrier = expression_data.loc[available_metabolic].mean(axis=0)
        else:
            metabolic_barrier = pd.Series(0.0, index=expression_data.columns)
        
        # 综合屏障评分
        barrier_score = (physical_barrier + metabolic_barrier) / 2
        
        # 分层评估
        q50 = barrier_score.median()
        
        barrier_df['drug_penetration_potential'] = np.where(
            barrier_score <= q50, 'High-Penetration', 'Low-Penetration'
        )
        barrier_df['barrier_score'] = barrier_score
        barrier_df['physical_barrier'] = physical_barrier
        barrier_df['metabolic_barrier'] = metabolic_barrier
        
        return barrier_df
    
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