"""
Five-Dimensional Tumor Microenvironment Prognostic Analysis
五维度肿瘤微环境预后分析器

核心功能：
1. 从5个维度分析与临床预后相关的关键指标
2. 识别每个维度中预后正相关和负相关的Top 5指标
3. 生成综合预后风险评分

维度定义：
- 肿瘤细胞：增殖、凋亡、侵袭、转移相关
- 免疫细胞：TAMs、Tregs、CD8+ T细胞、NK细胞等
- 基质细胞：CAFs、内皮细胞、成纤维细胞等
- 细胞外基质：ECM重塑、MMP活性、胶原代谢等
- 细胞因子：炎症因子、生长因子、趋化因子等
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class FiveDimensionPrognosticAnalyzer:
    """五维度肿瘤微环境预后分析器"""
    
    def __init__(self):
        self.dimension_markers = self._load_dimension_markers()
        self.analysis_results = {}
        self.prognostic_scores = {}
        
    def _load_dimension_markers(self) -> Dict[str, List[str]]:
        """加载五个维度的基因标记集"""
        return {
            'tumor_cell': [
                # 增殖相关
                'MKI67', 'PCNA', 'TOP2A', 'CCNB1', 'CCNA2', 'CDC20', 'BUB1B', 'AURKA', 'PLK1', 'CDK1',
                # 凋亡相关
                'TP53', 'BAX', 'BCL2', 'CASP3', 'CASP9', 'APAF1', 'PUMA', 'BAK1', 'BID', 'NOXA',
                # 侵袭转移
                'SNAI1', 'TWIST1', 'ZEB1', 'ZEB2', 'VIM', 'CDH1', 'CDH2', 'MMP2', 'MMP9', 'TIMP1',
                # 肿瘤干细胞
                'CD44', 'CD24', 'ALDH1A1', 'SOX2', 'NANOG', 'OCT4', 'BMI1', 'CD133', 'LGALS3', 'ABCG2',
                # 增殖信号
                'MYC', 'EGFR', 'ERBB2', 'KRAS', 'PIK3CA', 'AKT1', 'MTOR', 'RB1', 'CDKN1A', 'CDKN2A'
            ],
            'immune_cell': [
                # CD8+ T细胞
                'CD8A', 'CD8B', 'GZMA', 'GZMB', 'PRF1', 'IFNG', 'TNF', 'IL2', 'CD3E', 'CD3D',
                # 调节性T细胞 (Tregs)
                'FOXP3', 'IL2RA', 'CTLA4', 'IKZF2', 'IL10', 'TGFB1', 'TNFRSF18', 'TNFRSF4', 'CCR4', 'CD25',
                # TAMs (M1)
                'CD68', 'CD80', 'CD86', 'IL1B', 'IL6', 'TNF', 'NOS2', 'CXCL9', 'CXCL10', 'IRF5',
                # TAMs (M2) 
                'CD163', 'CD206', 'ARG1', 'IL10', 'TGFB1', 'CCL17', 'CCL18', 'CCL22', 'IRF4', 'STAT6',
                # NK细胞
                'NCAM1', 'NCR1', 'KLRB1', 'KLRD1', 'KLRF1', 'GZMK', 'XCL1', 'XCL2', 'CXCR6', 'KIR2DL1',
                # B细胞
                'CD19', 'CD20', 'MS4A1', 'CD79A', 'CD79B', 'IGHM', 'IGHG1', 'JCHAIN', 'BANK1', 'BLK'
            ],
            'stromal_cell': [
                # 癌相关成纤维细胞 (CAFs)
                'ACTA2', 'COL1A1', 'COL1A2', 'FAP', 'PDGFRA', 'PDGFRB', 'THY1', 'VIM', 'S100A4', 'FN1',
                # 活化CAFs
                'TAGLN', 'CALD1', 'CNN1', 'MYL9', 'MYLK', 'TPM1', 'TPM2', 'SMTN', 'DES', 'MSLN',
                # 血管内皮细胞
                'PECAM1', 'VWF', 'ENG', 'TEK', 'FLT1', 'KDR', 'ANGPT1', 'ANGPT2', 'TIE1', 'VEGFA',
                # 淋巴内皮细胞
                'LYVE1', 'PROX1', 'PDPN', 'CCL21', 'VEGFC', 'VEGFD', 'FLT4', 'CCBE1', 'ANGPT4', 'NRP2',
                # 周细胞
                'PDGFRB', 'NG2', 'RGS5', 'NOTCH3', 'MCAM', 'ACTA2', 'TAGLN', 'MYH11', 'CNN1', 'CALD1'
            ],
            'ecm_remodeling': [
                # 胶原代谢
                'COL1A1', 'COL1A2', 'COL3A1', 'COL4A1', 'COL5A1', 'COL6A1', 'COL8A1', 'COL12A1', 'COL14A1', 'COL16A1',
                # 基质金属蛋白酶
                'MMP1', 'MMP2', 'MMP3', 'MMP7', 'MMP9', 'MMP11', 'MMP12', 'MMP13', 'MMP14', 'MMP15',
                # MMP抑制剂
                'TIMP1', 'TIMP2', 'TIMP3', 'TIMP4', 'RECK', 'ADAMTS1', 'ADAMTS4', 'ADAMTS5', 'ADAMTS8', 'ADAMTS9',
                # 透明质酸代谢
                'HAS1', 'HAS2', 'HAS3', 'HYAL1', 'HYAL2', 'CD44', 'RHAMM', 'VERSICAN', 'HAPLN1', 'HAPLN3',
                # 纤维连接蛋白
                'FN1', 'FNDC1', 'FNDC3A', 'FNDC3B', 'FNDC5', 'ITGA1', 'ITGA2', 'ITGA3', 'ITGA5', 'ITGB1',
                # 弹性蛋白
                'ELN', 'EMILIN1', 'EMILIN2', 'FBLN1', 'FBLN2', 'FBLN5', 'FBN1', 'FBN2', 'LTBP1', 'LTBP2'
            ],
            'cytokine_signaling': [
                # 促炎细胞因子
                'IL1B', 'IL6', 'TNF', 'IFNG', 'IL12A', 'IL12B', 'IL17A', 'IL17F', 'IL18', 'IL23A',
                # 抗炎细胞因子
                'IL10', 'TGFB1', 'IL4', 'IL13', 'IL1RN', 'TNFAIP3', 'SOCS1', 'SOCS3', 'IL35', 'IL27',
                # 趋化因子
                'CCL2', 'CCL3', 'CCL4', 'CCL5', 'CCL17', 'CCL18', 'CCL19', 'CCL20', 'CCL21', 'CCL22',
                'CXCL1', 'CXCL2', 'CXCL8', 'CXCL9', 'CXCL10', 'CXCL11', 'CXCL12', 'CXCL13', 'CXCL16', 'CX3CL1',
                # 生长因子
                'VEGFA', 'VEGFB', 'VEGFC', 'PDGFA', 'PDGFB', 'FGF1', 'FGF2', 'EGF', 'IGF1', 'IGF2',
                # 信号通路关键分子
                'STAT1', 'STAT3', 'STAT6', 'NFKB1', 'RELA', 'JUN', 'FOS', 'SMAD2', 'SMAD3', 'SMAD4'
            ]
        }
    
    def analyze_dimension_prognosis(self, expression_data: pd.DataFrame, 
                                  clinical_data: pd.DataFrame,
                                  os_time_col: str = 'os_time',
                                  os_status_col: str = 'os_status') -> Dict:
        """
        分析五个维度的预后关联性
        
        Args:
            expression_data: 基因表达数据 (genes x samples)
            clinical_data: 临床数据 (包含生存信息)
            os_time_col: 总生存时间列名
            os_status_col: 生存状态列名 (1=死亡, 0=存活)
            
        Returns:
            Dict: 包含每个维度预后分析结果
        """
        results = {}
        
        for dimension, markers in self.dimension_markers.items():
            print(f"正在分析 {dimension} 维度...")
            
            # 获取该维度的基因表达数据
            available_markers = [gene for gene in markers if gene in expression_data.index]
            if len(available_markers) == 0:
                print(f"警告：{dimension} 维度没有可用的标记基因")
                continue
                
            dimension_expr = expression_data.loc[available_markers]
            
            # 计算每个基因的预后关联性
            gene_results = []
            for gene in available_markers:
                try:
                    result = self._calculate_gene_prognosis(
                        gene_expr=dimension_expr.loc[gene],
                        clinical_data=clinical_data,
                        os_time_col=os_time_col,
                        os_status_col=os_status_col
                    )
                    if result is not None:
                        result['gene'] = gene
                        result['dimension'] = dimension
                        gene_results.append(result)
                except Exception as e:
                    print(f"分析基因 {gene} 时出错: {e}")
                    continue
            
            if gene_results:
                # 转换为DataFrame
                df_results = pd.DataFrame(gene_results)
                
                # 筛选显著性基因 (p < 0.05)
                significant = df_results[df_results['p_value'] < 0.05].copy()
                
                # 分离正相关和负相关
                positive_corr = significant[significant['hr'] > 1].sort_values('p_value').head(5)
                negative_corr = significant[significant['hr'] < 1].sort_values('p_value').head(5)
                
                results[dimension] = {
                    'all_results': df_results,
                    'positive_correlation': positive_corr,
                    'negative_correlation': negative_corr,
                    'n_significant': len(significant),
                    'n_total': len(gene_results)
                }
                
                print(f"{dimension}: 共{len(gene_results)}个基因，{len(significant)}个显著相关")
            else:
                results[dimension] = {
                    'all_results': pd.DataFrame(),
                    'positive_correlation': pd.DataFrame(),
                    'negative_correlation': pd.DataFrame(),
                    'n_significant': 0,
                    'n_total': 0
                }
        
        self.analysis_results = results
        return results
    
    def _calculate_gene_prognosis(self, gene_expr: pd.Series, clinical_data: pd.DataFrame,
                                 os_time_col: str, os_status_col: str) -> Optional[Dict]:
        """
        计算单个基因的预后关联性 (简化的Cox回归)
        
        Args:
            gene_expr: 基因表达数据
            clinical_data: 临床数据
            os_time_col: 生存时间列
            os_status_col: 生存状态列
            
        Returns:
            Dict: 包含HR, p值, 95% CI等统计信息
        """
        try:
            # 匹配样本
            common_samples = list(set(gene_expr.index) & set(clinical_data.index))
            if len(common_samples) < 10:  # 至少需要10个样本
                return None
            
            # 获取匹配样本的数据
            expr_matched = gene_expr.loc[common_samples]
            clinical_matched = clinical_data.loc[common_samples]
            
            # 检查生存数据的完整性
            if clinical_matched[os_time_col].isna().any() or clinical_matched[os_status_col].isna().any():
                return None
            
            # 将基因表达按中位数分为高低表达组
            median_expr = expr_matched.median()
            high_expr_group = expr_matched > median_expr
            
            # 生存分析 (使用log-rank检验的简化版本)
            high_group_clinical = clinical_matched[high_expr_group]
            low_group_clinical = clinical_matched[~high_expr_group]
            
            if len(high_group_clinical) < 3 or len(low_group_clinical) < 3:
                return None
            
            # 计算生存率差异
            high_group_events = high_group_clinical[os_status_col].sum()
            high_group_total = len(high_group_clinical)
            low_group_events = low_group_clinical[os_status_col].sum()
            low_group_total = len(low_group_clinical)
            
            # 计算事件率
            high_event_rate = high_group_events / high_group_total if high_group_total > 0 else 0
            low_event_rate = low_group_events / low_group_total if low_group_total > 0 else 0
            
            # 计算HR (简化版本)
            if low_event_rate == 0:
                hr = float('inf') if high_event_rate > 0 else 1.0
            else:
                hr = high_event_rate / low_event_rate
            
            # 使用卡方检验计算p值
            contingency_table = [
                [high_group_events, high_group_total - high_group_events],
                [low_group_events, low_group_total - low_group_events]
            ]
            
            chi2, p_value = stats.chi2_contingency(contingency_table)[:2]
            
            # 计算95%置信区间 (简化版本)
            if high_group_events > 0 and low_group_events > 0:
                log_hr = np.log(hr)
                se_log_hr = np.sqrt(1/high_group_events + 1/low_group_events)
                ci_lower = np.exp(log_hr - 1.96 * se_log_hr)
                ci_upper = np.exp(log_hr + 1.96 * se_log_hr)
            else:
                ci_lower, ci_upper = 0, float('inf')
            
            return {
                'hr': hr,
                'p_value': p_value,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'high_expr_events': int(high_group_events),
                'high_expr_total': int(high_group_total),
                'low_expr_events': int(low_group_events),
                'low_expr_total': int(low_group_total),
                'median_expression': median_expr
            }
            
        except Exception as e:
            print(f"计算预后关联性时出错: {e}")
            return None
    
    def calculate_integrated_score(self, expression_data: pd.DataFrame) -> pd.DataFrame:
        """
        计算五维度整合预后评分
        
        Args:
            expression_data: 基因表达数据
            
        Returns:
            pd.DataFrame: 包含各维度评分和总评分的数据框
        """
        if not self.analysis_results:
            raise ValueError("请先运行 analyze_dimension_prognosis 方法")
        
        scores = pd.DataFrame(index=expression_data.columns)
        
        # 为每个维度计算评分
        dimension_weights = {
            'tumor_cell': 0.25,
            'immune_cell': 0.25,
            'stromal_cell': 0.20,
            'ecm_remodeling': 0.15,
            'cytokine_signaling': 0.15
        }
        
        for dimension, weight in dimension_weights.items():
            if dimension in self.analysis_results:
                dimension_score = self._calculate_dimension_score(
                    expression_data, dimension
                )
                scores[f'{dimension}_score'] = dimension_score
            else:
                scores[f'{dimension}_score'] = 0
        
        # 计算总评分
        scores['integrated_score'] = sum(
            scores[f'{dim}_score'] * weight
            for dim, weight in dimension_weights.items()
            if f'{dim}_score' in scores.columns
        )
        
        # 标准化评分到0-100范围
        scaler = StandardScaler()
        for col in scores.columns:
            scores[col] = scaler.fit_transform(scores[[col]]).flatten()
            # 转换到0-100范围
            min_val = scores[col].min()
            max_val = scores[col].max()
            if max_val > min_val:
                scores[col] = 100 * (scores[col] - min_val) / (max_val - min_val)
        
        self.prognostic_scores = scores
        return scores
    
    def _calculate_dimension_score(self, expression_data: pd.DataFrame, dimension: str) -> pd.Series:
        """计算单个维度的预后评分"""
        results = self.analysis_results[dimension]
        
        # 获取显著相关的基因
        pos_genes = results['positive_correlation']
        neg_genes = results['negative_correlation']
        
        # 初始化评分
        scores = pd.Series(0.0, index=expression_data.columns)
        
        # 高风险基因 (HR > 1) 贡献正评分
        for _, gene_info in pos_genes.iterrows():
            gene = gene_info['gene']
            if gene in expression_data.index:
                hr = gene_info['hr']
                p_val = gene_info['p_value']
                weight = np.log(hr) * (-np.log10(p_val))  # 权重基于HR和显著性
                gene_expr = expression_data.loc[gene]
                scores += weight * (gene_expr - gene_expr.median()) / gene_expr.std()
        
        # 低风险基因 (HR < 1) 贡献负评分
        for _, gene_info in neg_genes.iterrows():
            gene = gene_info['gene']
            if gene in expression_data.index:
                hr = gene_info['hr']
                p_val = gene_info['p_value']
                weight = np.log(1/hr) * (-np.log10(p_val))  # 权重基于1/HR和显著性
                gene_expr = expression_data.loc[gene]
                scores -= weight * (gene_expr - gene_expr.median()) / gene_expr.std()
        
        return scores
    
    def classify_risk_groups(self, prognostic_scores: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        基于五维度评分进行风险分层
        
        Args:
            prognostic_scores: 预后评分数据，如果为None则使用self.prognostic_scores
            
        Returns:
            pd.DataFrame: 包含风险分层结果
        """
        if prognostic_scores is None:
            if not hasattr(self, 'prognostic_scores') or self.prognostic_scores.empty:
                raise ValueError("请先计算预后评分")
            prognostic_scores = self.prognostic_scores
        
        risk_classification = pd.DataFrame(index=prognostic_scores.index)
        
        # 基于综合评分进行分层
        integrated_score = prognostic_scores['integrated_score']
        
        # 四分位数分层
        q25 = integrated_score.quantile(0.25)
        q50 = integrated_score.quantile(0.50)
        q75 = integrated_score.quantile(0.75)
        
        # 风险分组
        risk_classification['risk_group'] = pd.cut(
            integrated_score,
            bins=[-np.inf, q25, q50, q75, np.inf],
            labels=['Low', 'Medium-Low', 'Medium-High', 'High']
        )
        
        # 添加评分
        risk_classification['integrated_score'] = integrated_score
        
        # 计算有利维度数量 (评分低于中位数的维度)
        dimension_cols = [col for col in prognostic_scores.columns if col.endswith('_score') and col != 'integrated_score']
        
        favorable_dimensions = 0
        for col in dimension_cols:
            median_score = prognostic_scores[col].median()
            favorable_dimensions += (prognostic_scores[col] < median_score).astype(int)
        
        risk_classification['favorable_dimensions'] = favorable_dimensions
        
        return risk_classification
    
    def get_summary_report(self) -> Dict:
        """生成五维度分析总结报告"""
        if not self.analysis_results:
            return {"error": "请先运行分析"}
        
        summary = {
            'total_dimensions': 5,
            'analyzed_dimensions': len(self.analysis_results),
            'dimension_summary': {}
        }
        
        for dimension, results in self.analysis_results.items():
            summary['dimension_summary'][dimension] = {
                'total_genes': results['n_total'],
                'significant_genes': results['n_significant'],
                'positive_correlation_genes': len(results['positive_correlation']),
                'negative_correlation_genes': len(results['negative_correlation']),
                'top_positive_genes': results['positive_correlation']['gene'].tolist() if not results['positive_correlation'].empty else [],
                'top_negative_genes': results['negative_correlation']['gene'].tolist() if not results['negative_correlation'].empty else []
            }
        
        return summary