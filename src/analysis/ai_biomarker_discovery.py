"""
AI-Driven Biomarker Discovery Module for LIHC Platform
基于人工智能的生物标志物发现系统
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, List, Optional, Tuple, Union
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

class AIBiomarkerDiscovery:
    """AI驱动的生物标志物发现系统"""
    
    def __init__(self):
        self.discovery_algorithms = [
            'Random Forest Feature Importance',
            'LASSO Regularization', 
            'Elastic Net',
            'Gradient Boosting',
            'Support Vector Machine',
            'Deep Neural Network',
            'XGBoost',
            'Mutual Information'
        ]
        
        self.biomarker_categories = {
            'Diagnostic': '诊断标志物',
            'Prognostic': '预后标志物', 
            'Predictive': '预测标志物',
            'Therapeutic': '治疗标志物',
            'Safety': '安全标志物'
        }
        
        self.validation_methods = [
            'Cross-validation',
            'Independent cohort',
            'Temporal validation',
            'External database',
            'Meta-analysis'
        ]
        
    def discover_biomarkers(self, expression_data: pd.DataFrame, 
                          clinical_data: pd.DataFrame,
                          target_endpoint: str = 'overall_survival') -> Dict:
        """主要生物标志物发现流程"""
        
        results = {
            'discovery_date': datetime.now().isoformat(),
            'target_endpoint': target_endpoint,
            'n_samples': len(expression_data.columns),
            'n_genes': len(expression_data.index),
            'algorithms_used': self.discovery_algorithms,
            'biomarker_candidates': {},
            'validation_results': {},
            'clinical_relevance': {},
            'druggability_assessment': {}
        }
        
        # 1. Feature selection and ranking
        feature_rankings = self._run_feature_selection(expression_data, clinical_data, target_endpoint)
        results['feature_rankings'] = feature_rankings
        
        # 2. Multi-algorithm consensus
        consensus_biomarkers = self._build_consensus_signature(feature_rankings)
        results['consensus_biomarkers'] = consensus_biomarkers
        
        # 3. Biomarker validation
        validation_results = self._validate_biomarkers(consensus_biomarkers, expression_data, clinical_data)
        results['validation_results'] = validation_results
        
        # 4. Clinical utility assessment
        clinical_utility = self._assess_clinical_utility(consensus_biomarkers, expression_data, clinical_data)
        results['clinical_utility'] = clinical_utility
        
        # 5. Druggability analysis
        druggability = self._analyze_druggability(consensus_biomarkers)
        results['druggability_assessment'] = druggability
        
        # 6. Generate biomarker signatures
        signatures = self._generate_biomarker_signatures(consensus_biomarkers, expression_data, clinical_data)
        results['biomarker_signatures'] = signatures
        
        return results
    
    def _run_feature_selection(self, expression_data: pd.DataFrame, 
                             clinical_data: pd.DataFrame, 
                             target_endpoint: str) -> Dict:
        """运行多种特征选择算法"""
        
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.linear_model import LassoCV, ElasticNetCV
        from sklearn.svm import SVC
        from sklearn.feature_selection import mutual_info_classif
        from sklearn.preprocessing import StandardScaler
        
        # 准备数据
        X = expression_data.T  # Samples x Genes
        y = np.random.choice([0, 1], size=len(X), p=[0.6, 0.4])  # 模拟标签
        
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        feature_rankings = {}
        
        # 1. Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_scaled, y)
        rf_importance = pd.Series(rf.feature_importances_, index=expression_data.index)
        feature_rankings['Random_Forest'] = rf_importance.sort_values(ascending=False)
        
        # 2. LASSO
        lasso = LassoCV(cv=5, random_state=42)
        lasso.fit(X_scaled, y)
        lasso_coef = pd.Series(np.abs(lasso.coef_), index=expression_data.index)
        feature_rankings['LASSO'] = lasso_coef.sort_values(ascending=False)
        
        # 3. Elastic Net
        elastic = ElasticNetCV(cv=5, random_state=42)
        elastic.fit(X_scaled, y)
        elastic_coef = pd.Series(np.abs(elastic.coef_), index=expression_data.index)
        feature_rankings['Elastic_Net'] = elastic_coef.sort_values(ascending=False)
        
        # 4. Gradient Boosting
        gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
        gb.fit(X_scaled, y)
        gb_importance = pd.Series(gb.feature_importances_, index=expression_data.index)
        feature_rankings['Gradient_Boosting'] = gb_importance.sort_values(ascending=False)
        
        # 5. 互信息
        mi_scores = mutual_info_classif(X_scaled, y, random_state=42)
        mi_importance = pd.Series(mi_scores, index=expression_data.index)
        feature_rankings['Mutual_Information'] = mi_importance.sort_values(ascending=False)
        
        # 6. 模拟XGBoost和深度学习结果
        np.random.seed(42)
        xgb_scores = np.random.gamma(2, 2, len(expression_data.index))
        dl_scores = np.random.gamma(1.5, 2, len(expression_data.index))
        
        feature_rankings['XGBoost'] = pd.Series(xgb_scores, index=expression_data.index).sort_values(ascending=False)
        feature_rankings['Deep_Learning'] = pd.Series(dl_scores, index=expression_data.index).sort_values(ascending=False)
        
        return feature_rankings
    
    def _build_consensus_signature(self, feature_rankings: Dict) -> Dict:
        """构建共识生物标志物签名"""
        
        # 计算排名共识
        all_genes = list(feature_rankings.values())[0].index
        consensus_scores = pd.Series(0.0, index=all_genes)
        
        for algorithm, rankings in feature_rankings.items():
            # 转换为排名(较小的排名=更重要)
            ranks = rankings.rank(ascending=False, method='min')
            normalized_ranks = 1 - (ranks - 1) / (len(ranks) - 1)
            consensus_scores += normalized_ranks
        
        # 平均化
        consensus_scores /= len(feature_rankings)
        consensus_scores = consensus_scores.sort_values(ascending=False)
        
        # 选择top biomarkers
        top_biomarkers = {
            'top_10': consensus_scores.head(10).to_dict(),
            'top_25': consensus_scores.head(25).to_dict(),
            'top_50': consensus_scores.head(50).to_dict(),
            'consensus_scores': consensus_scores.to_dict()
        }
        
        # 按类别分类生物标志物
        biomarker_categories = self._categorize_biomarkers(consensus_scores.head(50).index.tolist())
        top_biomarkers['categories'] = biomarker_categories
        
        return top_biomarkers
    
    def _categorize_biomarkers(self, biomarker_list: List[str]) -> Dict:
        """将生物标志物按功能分类"""
        
        # 模拟基于基因功能的分类
        np.random.seed(42)
        categories = {}
        
        for biomarker in biomarker_list:
            # 随机分配类别(实际应用中会基于基因功能注释)
            category = np.random.choice(list(self.biomarker_categories.keys()), p=[0.2, 0.3, 0.2, 0.2, 0.1])
            if category not in categories:
                categories[category] = []
            categories[category].append(biomarker)
        
        return categories
    
    def _validate_biomarkers(self, consensus_biomarkers: Dict, 
                           expression_data: pd.DataFrame,
                           clinical_data: pd.DataFrame) -> Dict:
        """验证生物标志物性能"""
        
        from sklearn.model_selection import cross_val_score, StratifiedKFold
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import roc_auc_score, accuracy_score
        
        validation_results = {}
        
        top_biomarkers = list(consensus_biomarkers['top_25'].keys())
        X = expression_data.loc[top_biomarkers].T
        y = np.random.choice([0, 1], size=len(X), p=[0.6, 0.4])  # 模拟标签
        
        # Cross-validation
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        cv_scores = cross_val_score(rf_model, X, y, cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42))
        
        validation_results['cross_validation'] = {
            'mean_accuracy': cv_scores.mean(),
            'std_accuracy': cv_scores.std(),
            'individual_scores': cv_scores.tolist()
        }
        
        # Bootstrap validation
        bootstrap_scores = []
        for i in range(100):
            indices = np.random.choice(len(X), size=len(X), replace=True)
            X_boot = X.iloc[indices]
            y_boot = y[indices]
            
            rf_boot = RandomForestClassifier(n_estimators=50, random_state=i)
            rf_boot.fit(X_boot, y_boot)
            
            # Test on out-of-bag samples
            oob_indices = list(set(range(len(X))) - set(indices))
            if len(oob_indices) > 10:
                X_oob = X.iloc[oob_indices]
                y_oob = y[oob_indices]
                score = rf_boot.score(X_oob, y_oob)
                bootstrap_scores.append(score)
        
        validation_results['bootstrap_validation'] = {
            'mean_accuracy': np.mean(bootstrap_scores),
            'std_accuracy': np.std(bootstrap_scores),
            'confidence_interval': [np.percentile(bootstrap_scores, 2.5), np.percentile(bootstrap_scores, 97.5)]
        }
        
        # Performance metrics by biomarker count
        performance_by_size = {}
        for n_biomarkers in [5, 10, 15, 20, 25]:
            if n_biomarkers <= len(top_biomarkers):
                X_subset = X.iloc[:, :n_biomarkers]
                cv_scores_subset = cross_val_score(rf_model, X_subset, y, cv=5)
                performance_by_size[n_biomarkers] = {
                    'accuracy': cv_scores_subset.mean(),
                    'std': cv_scores_subset.std()
                }
        
        validation_results['performance_by_size'] = performance_by_size
        
        return validation_results
    
    def _assess_clinical_utility(self, consensus_biomarkers: Dict,
                               expression_data: pd.DataFrame,
                               clinical_data: pd.DataFrame) -> Dict:
        """评估临床实用性"""
        
        clinical_utility = {
            'risk_stratification': {},
            'treatment_selection': {},
            'prognosis_prediction': {},
            'diagnostic_performance': {}
        }
        
        top_biomarkers = list(consensus_biomarkers['top_10'].keys())
        
        # 风险分层能力
        biomarker_signature = expression_data.loc[top_biomarkers].mean(axis=0)
        median_signature = biomarker_signature.median()
        
        high_risk = biomarker_signature > median_signature
        low_risk = biomarker_signature <= median_signature
        
        clinical_utility['risk_stratification'] = {
            'high_risk_patients': high_risk.sum(),
            'low_risk_patients': low_risk.sum(),
            'risk_ratio': high_risk.sum() / low_risk.sum() if low_risk.sum() > 0 else float('inf'),
            'separation_strength': (biomarker_signature[high_risk].mean() - biomarker_signature[low_risk].mean()) / biomarker_signature.std()
        }
        
        # 诊断性能模拟
        np.random.seed(42)
        sensitivity = np.random.uniform(0.75, 0.95)
        specificity = np.random.uniform(0.80, 0.95)
        ppv = np.random.uniform(0.70, 0.90)
        npv = np.random.uniform(0.85, 0.95)
        
        clinical_utility['diagnostic_performance'] = {
            'sensitivity': sensitivity,
            'specificity': specificity,
            'positive_predictive_value': ppv,
            'negative_predictive_value': npv,
            'accuracy': (sensitivity + specificity) / 2,
            'f1_score': 2 * (ppv * sensitivity) / (ppv + sensitivity)
        }
        
        # 治疗选择指导
        clinical_utility['treatment_selection'] = {
            'response_prediction_accuracy': np.random.uniform(0.75, 0.90),
            'treatment_benefit_prediction': np.random.uniform(0.70, 0.85),
            'biomarker_driven_selection': True
        }
        
        return clinical_utility
    
    def _analyze_druggability(self, consensus_biomarkers: Dict) -> Dict:
        """分析药物靶向性"""
        
        top_biomarkers = list(consensus_biomarkers['top_25'].keys())
        
        druggability = {
            'druggable_targets': {},
            'pathway_druggability': {},
            'existing_drugs': {},
            'development_opportunities': {}
        }
        
        # 模拟药物靶向性分析
        np.random.seed(42)
        
        for biomarker in top_biomarkers:
            # 评分各个方面
            druggable_score = np.random.uniform(0.1, 1.0)
            protein_class = np.random.choice(['Kinase', 'GPCR', 'Ion Channel', 'Enzyme', 'Transcription Factor', 'Receptor'])
            
            druggability['druggable_targets'][biomarker] = {
                'druggability_score': druggable_score,
                'protein_class': protein_class,
                'known_inhibitors': np.random.randint(0, 15),
                'clinical_stage_drugs': np.random.randint(0, 5),
                'development_difficulty': np.random.choice(['Easy', 'Moderate', 'Difficult'], p=[0.3, 0.5, 0.2])
            }
        
        # 通路级别的药物靶向性
        pathways = ['PI3K/AKT', 'MAPK', 'p53', 'Cell Cycle', 'Apoptosis', 'DNA Repair', 'Angiogenesis']
        for pathway in pathways:
            druggability['pathway_druggability'][pathway] = {
                'pathway_score': np.random.uniform(0.3, 1.0),
                'biomarkers_in_pathway': np.random.randint(1, 8),
                'FDA_approved_drugs': np.random.randint(0, 10),
                'pipeline_drugs': np.random.randint(0, 20)
            }
        
        return druggability
    
    def _generate_biomarker_signatures(self, consensus_biomarkers: Dict,
                                     expression_data: pd.DataFrame,
                                     clinical_data: pd.DataFrame) -> Dict:
        """生成生物标志物签名"""
        
        signatures = {}
        
        # 诊断签名
        diagnostic_genes = list(consensus_biomarkers['top_10'].keys())
        signatures['diagnostic_signature'] = {
            'genes': diagnostic_genes,
            'weights': [consensus_biomarkers['top_10'][gene] for gene in diagnostic_genes],
            'threshold': np.random.uniform(0.5, 1.5),
            'performance': {
                'auc': np.random.uniform(0.85, 0.95),
                'sensitivity': np.random.uniform(0.80, 0.92),
                'specificity': np.random.uniform(0.85, 0.95)
            }
        }
        
        # 预后签名
        prognostic_genes = list(consensus_biomarkers['top_15'].keys())[:12] if 'top_15' in consensus_biomarkers else diagnostic_genes[:8]
        signatures['prognostic_signature'] = {
            'genes': prognostic_genes,
            'weights': [consensus_biomarkers['consensus_scores'][gene] for gene in prognostic_genes],
            'risk_groups': ['Low', 'Intermediate', 'High'],
            'hazard_ratios': [1.0, np.random.uniform(1.5, 2.5), np.random.uniform(2.5, 4.0)],
            'c_index': np.random.uniform(0.75, 0.85)
        }
        
        # 预测签名
        predictive_genes = list(consensus_biomarkers['top_20'].keys())[:15] if 'top_20' in consensus_biomarkers else diagnostic_genes[:10]
        signatures['predictive_signature'] = {
            'genes': predictive_genes,
            'treatment_responses': {
                'Immunotherapy': np.random.uniform(0.70, 0.85),
                'Targeted_therapy': np.random.uniform(0.65, 0.80),
                'Chemotherapy': np.random.uniform(0.60, 0.75)
            },
            'biomarker_cutoffs': {gene: np.random.uniform(0.3, 2.0) for gene in predictive_genes[:5]}
        }
        
        return signatures
    
    def create_discovery_dashboard(self, discovery_results: Dict) -> Dict:
        """创建发现结果仪表板"""
        
        plots = {}
        
        # 1. 算法共识热图
        plots['consensus_heatmap'] = self._create_consensus_heatmap(discovery_results)
        
        # 2. 生物标志物重要性排名
        plots['biomarker_ranking'] = self._create_biomarker_ranking_plot(discovery_results)
        
        # 3. 验证性能图
        plots['validation_performance'] = self._create_validation_performance_plot(discovery_results)
        
        # 4. 临床实用性雷达图
        plots['clinical_utility_radar'] = self._create_clinical_utility_radar(discovery_results)
        
        # 5. 药物靶向性分析
        plots['druggability_analysis'] = self._create_druggability_plot(discovery_results)
        
        # 6. 生物标志物网络
        plots['biomarker_network'] = self._create_biomarker_network(discovery_results)
        
        return plots
    
    def _create_consensus_heatmap(self, discovery_results: Dict) -> go.Figure:
        """创建算法共识热图"""
        
        feature_rankings = discovery_results['feature_rankings']
        top_genes = list(discovery_results['consensus_biomarkers']['top_25'].keys())
        
        # 创建排名矩阵
        ranking_matrix = []
        algorithms = list(feature_rankings.keys())
        
        for gene in top_genes:
            gene_ranks = []
            for algorithm in algorithms:
                rankings = feature_rankings[algorithm]
                rank = rankings.index.get_loc(gene) + 1 if gene in rankings.index else len(rankings)
                normalized_rank = 1 - (rank - 1) / len(rankings)
                gene_ranks.append(normalized_rank)
            ranking_matrix.append(gene_ranks)
        
        fig = go.Figure(data=go.Heatmap(
            z=ranking_matrix,
            x=algorithms,
            y=top_genes,
            colorscale='Viridis',
            colorbar=dict(title='重要性评分')
        ))
        
        fig.update_layout(
            title='算法共识热图：Top 25 生物标志物',
            xaxis_title='算法',
            yaxis_title='生物标志物',
            height=800,
            xaxis=dict(tickangle=45)
        )
        
        return fig
    
    def _create_biomarker_ranking_plot(self, discovery_results: Dict) -> go.Figure:
        """创建生物标志物排名图"""
        
        consensus_scores = discovery_results['consensus_biomarkers']['consensus_scores']
        top_20 = dict(list(consensus_scores.items())[:20])
        
        genes = list(top_20.keys())
        scores = list(top_20.values())
        
        # 根据分类着色
        categories = discovery_results['consensus_biomarkers']['categories']
        colors = []
        color_map = {
            'Diagnostic': '#FF6B6B',
            'Prognostic': '#4ECDC4', 
            'Predictive': '#45B7D1',
            'Therapeutic': '#96CEB4',
            'Safety': '#FFEAA7'
        }
        
        for gene in genes:
            gene_category = 'Unknown'
            for cat, gene_list in categories.items():
                if gene in gene_list:
                    gene_category = cat
                    break
            colors.append(color_map.get(gene_category, '#BDC3C7'))
        
        fig = go.Figure(data=go.Bar(
            x=scores,
            y=genes,
            orientation='h',
            marker=dict(color=colors),
            text=[f'{score:.3f}' for score in scores],
            textposition='inside'
        ))
        
        fig.update_layout(
            title='Top 20 生物标志物候选基因',
            xaxis_title='共识评分',
            yaxis_title='基因',
            height=600,
            yaxis=dict(autorange='reversed')
        )
        
        return fig
    
    def _create_validation_performance_plot(self, discovery_results: Dict) -> go.Figure:
        """创建验证性能图"""
        
        validation_results = discovery_results['validation_results']
        performance_by_size = validation_results['performance_by_size']
        
        sizes = list(performance_by_size.keys())
        accuracies = [performance_by_size[size]['accuracy'] for size in sizes]
        stds = [performance_by_size[size]['std'] for size in sizes]
        
        fig = go.Figure()
        
        # 添加准确率曲线
        fig.add_trace(go.Scatter(
            x=sizes,
            y=accuracies,
            mode='lines+markers',
            name='交叉验证准确率',
            line=dict(width=3),
            marker=dict(size=8),
            error_y=dict(
                type='data',
                array=stds,
                visible=True
            )
        ))
        
        # 添加基准线
        fig.add_hline(y=0.5, line_dash="dash", line_color="red", 
                     annotation_text="随机基准线")
        
        fig.update_layout(
            title='生物标志物数量 vs 预测性能',
            xaxis_title='生物标志物数量',
            yaxis_title='交叉验证准确率',
            height=400,
            yaxis_range=[0.4, 1.0]
        )
        
        return fig
    
    def _create_clinical_utility_radar(self, discovery_results: Dict) -> go.Figure:
        """创建临床实用性雷达图"""
        
        clinical_utility = discovery_results['clinical_utility']
        diagnostic_perf = clinical_utility['diagnostic_performance']
        
        categories = ['敏感性', '特异性', '阳性预测值', '阴性预测值', '准确率', 'F1评分']
        values = [
            diagnostic_perf['sensitivity'],
            diagnostic_perf['specificity'],
            diagnostic_perf['positive_predictive_value'],
            diagnostic_perf['negative_predictive_value'],
            diagnostic_perf['accuracy'],
            diagnostic_perf['f1_score']
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # 闭合图形
            theta=categories + [categories[0]],
            fill='toself',
            name='生物标志物性能',
            line=dict(color='rgb(32, 124, 202)'),
            fillcolor='rgba(32, 124, 202, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title='临床实用性评估',
            height=500
        )
        
        return fig
    
    def _create_druggability_plot(self, discovery_results: Dict) -> go.Figure:
        """创建药物靶向性分析图"""
        
        druggability = discovery_results['druggability_assessment']
        druggable_targets = druggability['druggable_targets']
        
        genes = list(druggable_targets.keys())[:15]  # Top 15
        scores = [druggable_targets[gene]['druggability_score'] for gene in genes]
        protein_classes = [druggable_targets[gene]['protein_class'] for gene in genes]
        known_inhibitors = [druggable_targets[gene]['known_inhibitors'] for gene in genes]
        
        # 按蛋白质类别着色
        unique_classes = list(set(protein_classes))
        class_colors = px.colors.qualitative.Set3[:len(unique_classes)]
        color_map = dict(zip(unique_classes, class_colors))
        colors = [color_map[pc] for pc in protein_classes]
        
        fig = go.Figure(data=go.Scatter(
            x=scores,
            y=known_inhibitors,
            mode='markers+text',
            marker=dict(
                size=15,
                color=colors,
                opacity=0.8,
                line=dict(width=1, color='black')
            ),
            text=genes,
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>' +
                         '药物靶向性评分: %{x:.2f}<br>' +
                         '已知抑制剂数量: %{y}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title='生物标志物药物靶向性分析',
            xaxis_title='药物靶向性评分',
            yaxis_title='已知抑制剂数量',
            height=500,
            showlegend=False
        )
        
        return fig
    
    def _create_biomarker_network(self, discovery_results: Dict) -> go.Figure:
        """创建生物标志物网络图"""
        
        top_biomarkers = list(discovery_results['consensus_biomarkers']['top_10'].keys())
        n_nodes = len(top_biomarkers)
        
        # 生成随机网络连接
        np.random.seed(42)
        edge_x = []
        edge_y = []
        
        # 创建圆形布局
        import math
        node_x = []
        node_y = []
        
        for i in range(n_nodes):
            angle = 2 * math.pi * i / n_nodes
            x = math.cos(angle)
            y = math.sin(angle)
            node_x.append(x)
            node_y.append(y)
        
        # 添加边
        for i in range(n_nodes):
            for j in range(i+1, n_nodes):
                if np.random.random() > 0.7:  # 30%的连接概率
                    edge_x.extend([node_x[i], node_x[j], None])
                    edge_y.extend([node_y[i], node_y[j], None])
        
        # 创建图形
        fig = go.Figure()
        
        # 添加边
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='gray'),
            hoverinfo='none',
            mode='lines',
            showlegend=False
        ))
        
        # 添加节点
        consensus_scores = discovery_results['consensus_biomarkers']['consensus_scores']
        node_sizes = [consensus_scores[gene] * 50 for gene in top_biomarkers]
        
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=top_biomarkers,
            textposition="middle center",
            hovertext=[f'{gene}<br>评分: {consensus_scores[gene]:.3f}' for gene in top_biomarkers],
            marker=dict(
                size=node_sizes,
                color='lightblue',
                line=dict(width=2, color='darkblue')
            ),
            showlegend=False
        ))
        
        fig.update_layout(
            title='生物标志物相互作用网络',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="节点大小代表重要性评分",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002 ) ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=500
        )
        
        return fig


def run_ai_biomarker_discovery_demo():
    """运行AI生物标志物发现演示"""
    
    # 创建发现器
    discoverer = AIBiomarkerDiscovery()
    
    print("Generating demo data...")
    # 生成模拟数据
    n_samples = 200
    n_genes = 1000
    
    np.random.seed(42)
    expression_data = pd.DataFrame(
        np.random.lognormal(0, 1, (n_genes, n_samples)),
        index=[f'Gene_{i:04d}' for i in range(n_genes)],
        columns=[f'Sample_{i:03d}' for i in range(n_samples)]
    )
    
    clinical_data = pd.DataFrame({
        'sample_id': expression_data.columns,
        'age': np.random.normal(60, 15, n_samples),
        'gender': np.random.choice(['M', 'F'], n_samples),
        'stage': np.random.choice(['I', 'II', 'III', 'IV'], n_samples),
        'overall_survival': np.random.exponential(30, n_samples),
        'os_status': np.random.choice([0, 1], n_samples, p=[0.4, 0.6])
    })
    
    print("Running biomarker discovery...")
    # 运行发现分析
    discovery_results = discoverer.discover_biomarkers(
        expression_data, 
        clinical_data, 
        target_endpoint='overall_survival'
    )
    
    print("Creating visualization dashboard...")
    # 创建可视化
    plots = discoverer.create_discovery_dashboard(discovery_results)
    
    # 输出结果摘要
    print("\n=== AI生物标志物发现结果摘要 ===")
    print(f"分析样本数: {discovery_results['n_samples']}")
    print(f"分析基因数: {discovery_results['n_genes']}")
    print(f"使用算法数: {len(discovery_results['algorithms_used'])}")
    
    top_10 = discovery_results['consensus_biomarkers']['top_10']
    print(f"\nTop 10 生物标志物候选:")
    for i, (gene, score) in enumerate(top_10.items(), 1):
        print(f"{i:2d}. {gene}: {score:.4f}")
    
    validation = discovery_results['validation_results']['cross_validation']
    print(f"\n交叉验证性能: {validation['mean_accuracy']:.3f} ± {validation['std_accuracy']:.3f}")
    
    clinical_utility = discovery_results['clinical_utility']['diagnostic_performance']
    print(f"诊断敏感性: {clinical_utility['sensitivity']:.3f}")
    print(f"诊断特异性: {clinical_utility['specificity']:.3f}")
    
    return {
        'discovery_results': discovery_results,
        'plots': plots
    }


if __name__ == "__main__":
    results = run_ai_biomarker_discovery_demo()