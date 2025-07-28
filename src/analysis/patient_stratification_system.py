"""
Patient Stratification and Personalized Treatment Decision Support System for LIHC Platform
患者分层与个性化治疗决策支持系统
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, List, Optional, Tuple, Union
import warnings
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
warnings.filterwarnings('ignore')

@dataclass
class PatientProfile:
    """患者档案数据类"""
    patient_id: str
    age: int
    gender: str
    bmi: float
    stage: str
    grade: str
    etiology: str  # 病因学 (HBV, HCV, NASH, Alcohol, etc.)
    performance_status: int  # ECOG评分
    liver_function: Dict[str, float]  # 肝功能指标
    biomarkers: Dict[str, Union[float, str]]  # 生物标志物
    genomic_profile: Dict[str, Union[int, float]]  # 基因组特征
    comorbidities: List[str]  # 合并症
    previous_treatments: List[str]  # 既往治疗史
    treatment_response_history: List[Dict]  # 治疗反应史

class PatientStratificationSystem:
    """患者分层与个性化治疗决策支持系统"""
    
    def __init__(self):
        self.stratification_algorithms = [
            'Multi-omics Clustering',     # 多组学聚类
            'Clinical-Molecular Integration', # 临床分子整合
            'AI-driven Risk Scoring',     # AI风险评分
            'Pathway-based Stratification', # 通路分层
            'Treatment Response Prediction' # 治疗响应预测
        ]
        
        self.treatment_categories = {
            'Surgical': ['Hepatectomy', 'Liver Transplantation', 'Ablation'],
            'Targeted Therapy': ['Sorafenib', 'Lenvatinib', 'Regorafenib', 'Cabozantinib'],
            'Immunotherapy': ['Atezolizumab', 'Nivolumab', 'Pembrolizumab', 'Durvalumab'],
            'Combination Therapy': ['Atezolizumab+Bevacizumab', 'Sorafenib+Atezolizumab'],
            'Supportive Care': ['TACE', 'Y90', 'Best Supportive Care']
        }
        
        self.risk_factors = [
            'Tumor Size', 'Multifocal Disease', 'Vascular Invasion',
            'Lymph Node Involvement', 'Distant Metastasis', 'AFP Level',
            'Liver Function', 'Performance Status', 'Genetic Markers'
        ]
        
        self.precision_biomarkers = [
            'TP53_mutation', 'CTNNB1_mutation', 'ARID1A_mutation',
            'RB1_mutation', 'AXIN1_mutation', 'NFE2L2_mutation',
            'AFP_level', 'PD_L1_expression', 'TMB_score',
            'MSI_status', 'HBV_status', 'HCV_status'
        ]
        
    def generate_patient_cohort(self, n_patients: int = 200) -> List[PatientProfile]:
        """生成患者队列数据"""
        
        np.random.seed(42)
        patients = []
        
        for i in range(n_patients):
            # 基本信息
            age = int(np.random.normal(65, 12))
            age = max(25, min(85, age))
            
            gender = np.random.choice(['M', 'F'], p=[0.7, 0.3])
            bmi = np.random.normal(25, 4)
            
            stage = np.random.choice(['I', 'II', 'III', 'IV'], p=[0.2, 0.3, 0.3, 0.2])
            grade = np.random.choice(['G1', 'G2', 'G3'], p=[0.3, 0.5, 0.2])
            etiology = np.random.choice(['HBV', 'HCV', 'NASH', 'Alcohol', 'Other'], 
                                       p=[0.4, 0.2, 0.2, 0.15, 0.05])
            
            performance_status = np.random.choice([0, 1, 2], p=[0.5, 0.3, 0.2])
            
            # 肝功能指标
            liver_function = {
                'ALT': np.random.gamma(2, 20),
                'AST': np.random.gamma(2, 25),
                'Bilirubin': np.random.gamma(1.5, 0.8),
                'Albumin': np.random.normal(3.5, 0.5),
                'PT_INR': np.random.gamma(2, 0.5),
                'Child_Pugh_Score': np.random.choice([5, 6, 7, 8, 9], p=[0.4, 0.3, 0.2, 0.08, 0.02])
            }
            
            # 生物标志物
            biomarkers = {
                'AFP': np.random.lognormal(3, 2),
                'AFP_L3': np.random.uniform(5, 50),
                'DCP': np.random.lognormal(2, 1),
                'GPC3': np.random.uniform(0.5, 5.0),
                'PD_L1_CPS': np.random.uniform(0, 30),
                'TMB': np.random.gamma(2, 5),
                'MSI_status': np.random.choice(['MSS', 'MSI-L', 'MSI-H'], p=[0.85, 0.10, 0.05])
            }
            
            # 基因组特征
            genomic_profile = {}
            for biomarker in self.precision_biomarkers:
                if 'mutation' in biomarker:
                    genomic_profile[biomarker] = np.random.choice([0, 1], p=[0.8, 0.2])
                elif 'level' in biomarker:
                    genomic_profile[biomarker] = np.random.lognormal(2, 1)
                elif 'expression' in biomarker:
                    genomic_profile[biomarker] = np.random.uniform(0, 100)
                elif 'score' in biomarker:
                    genomic_profile[biomarker] = np.random.gamma(2, 3)
                else:
                    genomic_profile[biomarker] = np.random.choice(['Positive', 'Negative'], p=[0.3, 0.7])
            
            # 合并症
            potential_comorbidities = ['Diabetes', 'Hypertension', 'CAD', 'COPD', 'CKD', 'Cirrhosis']
            n_comorbidities = np.random.poisson(1.5)
            comorbidities = np.random.choice(potential_comorbidities, 
                                           min(n_comorbidities, len(potential_comorbidities)), 
                                           replace=False).tolist()
            
            # 既往治疗史
            previous_treatments = []
            if np.random.random() > 0.6:  # 40%有既往治疗史
                treatments = ['Surgery', 'TACE', 'RFA', 'Sorafenib', 'Chemotherapy']
                n_treatments = np.random.randint(1, 3)
                previous_treatments = np.random.choice(treatments, n_treatments, replace=False).tolist()
            
            # 治疗反应史
            treatment_response_history = []
            for treatment in previous_treatments:
                response = {
                    'treatment': treatment,
                    'response': np.random.choice(['CR', 'PR', 'SD', 'PD'], p=[0.1, 0.25, 0.45, 0.2]),
                    'duration_months': np.random.exponential(8),
                    'toxicity_grade': np.random.choice([0, 1, 2, 3], p=[0.3, 0.4, 0.25, 0.05])
                }
                treatment_response_history.append(response)
            
            patient = PatientProfile(
                patient_id=f'LIHC_{i+1:03d}',
                age=age,
                gender=gender,
                bmi=bmi,
                stage=stage,
                grade=grade,
                etiology=etiology,
                performance_status=performance_status,
                liver_function=liver_function,
                biomarkers=biomarkers,
                genomic_profile=genomic_profile,
                comorbidities=comorbidities,
                previous_treatments=previous_treatments,
                treatment_response_history=treatment_response_history
            )
            
            patients.append(patient)
        
        return patients
    
    def perform_patient_stratification(self, patients: List[PatientProfile]) -> Dict:
        """执行患者分层分析"""
        
        stratification_results = {
            'algorithm': 'Multi-dimensional Clustering',
            'strata': {},
            'risk_scores': {},
            'treatment_recommendations': {},
            'biomarker_signatures': {},
            'survival_predictions': {},
            'quality_metrics': {}
        }
        
        # 创建特征矩阵
        feature_matrix, feature_names = self._create_feature_matrix(patients)
        
        # 执行聚类分层
        cluster_results = self._perform_clustering_stratification(feature_matrix, patients)
        stratification_results['strata'] = cluster_results
        
        # 计算风险评分
        risk_scores = self._calculate_risk_scores(patients)
        stratification_results['risk_scores'] = risk_scores
        
        # 生成治疗推荐
        treatment_recommendations = self._generate_treatment_recommendations(patients, cluster_results)
        stratification_results['treatment_recommendations'] = treatment_recommendations
        
        # 识别生物标志物签名
        biomarker_signatures = self._identify_biomarker_signatures(patients, cluster_results)
        stratification_results['biomarker_signatures'] = biomarker_signatures
        
        # 生存预测
        survival_predictions = self._predict_survival_outcomes(patients, cluster_results)
        stratification_results['survival_predictions'] = survival_predictions
        
        # 质量评估
        quality_metrics = self._assess_stratification_quality(cluster_results, feature_matrix)
        stratification_results['quality_metrics'] = quality_metrics
        
        return stratification_results
    
    def _create_feature_matrix(self, patients: List[PatientProfile]) -> Tuple[np.ndarray, List[str]]:
        """创建特征矩阵"""
        
        features = []
        feature_names = []
        
        for patient in patients:
            patient_features = []
            
            # 基本临床特征
            patient_features.extend([
                patient.age / 100,  # 归一化年龄
                1 if patient.gender == 'M' else 0,
                patient.bmi / 40,  # 归一化BMI
                {'I': 1, 'II': 2, 'III': 3, 'IV': 4}[patient.stage] / 4,
                {'G1': 1, 'G2': 2, 'G3': 3}[patient.grade] / 3,
                patient.performance_status / 2
            ])
            
            # 肝功能指标（归一化）
            patient_features.extend([
                patient.liver_function['ALT'] / 200,
                patient.liver_function['AST'] / 200,
                patient.liver_function['Bilirubin'] / 5,
                patient.liver_function['Albumin'] / 5,
                patient.liver_function['PT_INR'] / 3,
                patient.liver_function['Child_Pugh_Score'] / 10
            ])
            
            # 生物标志物（对数转换+归一化）
            patient_features.extend([
                np.log10(patient.biomarkers['AFP'] + 1) / 5,
                patient.biomarkers['AFP_L3'] / 100,
                np.log10(patient.biomarkers['DCP'] + 1) / 5,
                patient.biomarkers['GPC3'] / 10,
                patient.biomarkers['PD_L1_CPS'] / 50,
                patient.biomarkers['TMB'] / 50
            ])
            
            # 基因组特征
            for biomarker in self.precision_biomarkers:
                if biomarker in patient.genomic_profile:
                    value = patient.genomic_profile[biomarker]
                    if isinstance(value, (int, float)):
                        if 'mutation' in biomarker:
                            patient_features.append(value)
                        else:
                            patient_features.append(value / 100)  # 归一化
                    else:
                        patient_features.append(1 if value == 'Positive' else 0)
            
            # 合并症数量
            patient_features.append(len(patient.comorbidities) / 5)
            
            # 既往治疗数量
            patient_features.append(len(patient.previous_treatments) / 3)
            
            features.append(patient_features)
        
        # 特征名称
        feature_names = [
            'Age', 'Gender_M', 'BMI', 'Stage', 'Grade', 'Performance_Status',
            'ALT', 'AST', 'Bilirubin', 'Albumin', 'PT_INR', 'Child_Pugh',
            'AFP_log', 'AFP_L3', 'DCP_log', 'GPC3', 'PD_L1_CPS', 'TMB'
        ] + self.precision_biomarkers + ['Comorbidities_Count', 'Previous_Treatments_Count']
        
        return np.array(features), feature_names
    
    def _perform_clustering_stratification(self, feature_matrix: np.ndarray, 
                                         patients: List[PatientProfile]) -> Dict:
        """执行聚类分层"""
        
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import silhouette_score
        
        # 标准化特征
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(feature_matrix)
        
        # 确定最优聚类数
        best_k = 3
        best_silhouette = -1
        
        for k in range(2, 8):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            silhouette = silhouette_score(X_scaled, labels)
            
            if silhouette > best_silhouette:
                best_silhouette = silhouette
                best_k = k
        
        # 使用最佳k进行最终聚类
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # 分析每个聚类的特征
        cluster_analysis = {}
        
        for cluster_id in range(best_k):
            cluster_patients = [patients[i] for i in range(len(patients)) if cluster_labels[i] == cluster_id]
            
            # 计算聚类特征
            cluster_features = {
                'n_patients': len(cluster_patients),
                'avg_age': np.mean([p.age for p in cluster_patients]),
                'stage_distribution': self._calculate_distribution([p.stage for p in cluster_patients]),
                'grade_distribution': self._calculate_distribution([p.grade for p in cluster_patients]),
                'etiology_distribution': self._calculate_distribution([p.etiology for p in cluster_patients]),
                'avg_afp': np.mean([p.biomarkers['AFP'] for p in cluster_patients]),
                'mutation_frequencies': {},
                'survival_characteristics': {}
            }
            
            # 计算突变频率
            for biomarker in self.precision_biomarkers:
                if 'mutation' in biomarker:
                    mutations = [p.genomic_profile.get(biomarker, 0) for p in cluster_patients]
                    cluster_features['mutation_frequencies'][biomarker] = np.mean(mutations)
            
            # 模拟生存特征
            cluster_features['survival_characteristics'] = {
                'median_os': np.random.uniform(8, 30),
                'median_pfs': np.random.uniform(4, 15),
                'response_rate': np.random.uniform(0.1, 0.6)
            }
            
            cluster_analysis[f'Stratum_{cluster_id + 1}'] = cluster_features
        
        return {
            'cluster_labels': cluster_labels,
            'n_clusters': best_k,
            'silhouette_score': best_silhouette,
            'cluster_analysis': cluster_analysis
        }
    
    def _calculate_distribution(self, values: List) -> Dict:
        """计算分布统计"""
        unique_values, counts = np.unique(values, return_counts=True)
        total = len(values)
        return {str(val): count/total for val, count in zip(unique_values, counts)}
    
    def _calculate_risk_scores(self, patients: List[PatientProfile]) -> Dict:
        """计算风险评分"""
        
        risk_scores = {}
        
        for patient in patients:
            # 综合风险评分（0-100）
            base_risk = 0
            
            # 年龄风险
            if patient.age > 70:
                base_risk += 15
            elif patient.age > 60:
                base_risk += 10
            
            # 分期风险
            stage_risk = {'I': 5, 'II': 15, 'III': 30, 'IV': 50}
            base_risk += stage_risk[patient.stage]
            
            # 肝功能风险
            if patient.liver_function['Child_Pugh_Score'] >= 7:
                base_risk += 20
            elif patient.liver_function['Child_Pugh_Score'] == 6:
                base_risk += 10
            
            # AFP风险
            if patient.biomarkers['AFP'] > 400:
                base_risk += 15
            elif patient.biomarkers['AFP'] > 20:
                base_risk += 8
            
            # 基因突变风险
            high_risk_mutations = ['TP53_mutation', 'RB1_mutation']
            for mutation in high_risk_mutations:
                if patient.genomic_profile.get(mutation, 0) == 1:
                    base_risk += 10
            
            # 体能状态风险
            base_risk += patient.performance_status * 8
            
            # 合并症风险
            base_risk += len(patient.comorbidities) * 3
            
            # 限制在0-100范围内
            total_risk = min(100, max(0, base_risk))
            
            # 分类风险等级
            if total_risk < 30:
                risk_category = 'Low'
            elif total_risk < 60:
                risk_category = 'Intermediate'
            else:
                risk_category = 'High'
            
            risk_scores[patient.patient_id] = {
                'total_score': total_risk,
                'risk_category': risk_category,
                'risk_components': {
                    'age_risk': min(15, (patient.age - 50) // 10 * 5) if patient.age > 50 else 0,
                    'stage_risk': stage_risk[patient.stage],
                    'liver_function_risk': min(20, (patient.liver_function['Child_Pugh_Score'] - 5) * 10),
                    'biomarker_risk': min(15, np.log10(patient.biomarkers['AFP'] + 1) * 3),
                    'genomic_risk': sum([10 for m in high_risk_mutations if patient.genomic_profile.get(m, 0) == 1]),
                    'clinical_risk': patient.performance_status * 8 + len(patient.comorbidities) * 3
                }
            }
        
        return risk_scores
    
    def _generate_treatment_recommendations(self, patients: List[PatientProfile], 
                                          cluster_results: Dict) -> Dict:
        """生成治疗推荐"""
        
        recommendations = {}
        cluster_labels = cluster_results['cluster_labels']
        
        # 为每个层级定义最佳治疗策略
        stratum_treatments = {
            'Stratum_1': {  # 低风险层级
                'first_line': ['Surgery', 'Ablation'],
                'second_line': ['Sorafenib', 'Lenvatinib'],
                'rationale': '早期疾病，适合根治性治疗'
            },
            'Stratum_2': {  # 中等风险层级
                'first_line': ['Atezolizumab+Bevacizumab', 'Sorafenib'],
                'second_line': ['Lenvatinib', 'Regorafenib'],
                'rationale': '中期疾病，推荐联合治疗'
            },
            'Stratum_3': {  # 高风险层级
                'first_line': ['Atezolizumab+Bevacizumab', 'Immunotherapy'],
                'second_line': ['Cabozantinib', 'Clinical Trial'],
                'rationale': '晚期疾病，强调免疫治疗'
            }
        }
        
        for i, patient in enumerate(patients):
            cluster_id = cluster_labels[i]
            stratum_name = f'Stratum_{cluster_id + 1}'
            
            # 个性化调整
            personalized_rec = self._personalize_treatment(patient, stratum_treatments.get(stratum_name, stratum_treatments['Stratum_2']))
            
            recommendations[patient.patient_id] = {
                'stratum': stratum_name,
                'risk_level': self._get_patient_risk_level(patient),
                'first_line_options': personalized_rec['first_line'],
                'second_line_options': personalized_rec['second_line'],
                'contraindications': self._identify_contraindications(patient),
                'special_considerations': self._identify_special_considerations(patient),
                'monitoring_plan': self._create_monitoring_plan(patient),
                'expected_outcomes': self._predict_treatment_outcomes(patient),
                'rationale': personalized_rec['rationale']
            }
        
        return recommendations
    
    def _personalize_treatment(self, patient: PatientProfile, base_treatment: Dict) -> Dict:
        """个性化治疗调整"""
        
        personalized = base_treatment.copy()
        
        # 基于基因型调整
        if patient.genomic_profile.get('PD_L1_expression', 0) > 50:
            if 'Immunotherapy' not in personalized['first_line']:
                personalized['first_line'].insert(0, 'Atezolizumab')
        
        # 基于肝功能调整
        if patient.liver_function['Child_Pugh_Score'] >= 7:
            # 移除对肝功能要求高的治疗
            personalized['first_line'] = [t for t in personalized['first_line'] if t not in ['Surgery', 'High-dose Chemotherapy']]
            if 'Best Supportive Care' not in personalized['first_line']:
                personalized['second_line'].append('Best Supportive Care')
        
        # 基于年龄调整
        if patient.age > 75:
            personalized['first_line'] = [t for t in personalized['first_line'] if t != 'Surgery']
        
        # 基于既往治疗史调整
        for prev_treatment in patient.previous_treatments:
            if prev_treatment in personalized['first_line']:
                personalized['first_line'].remove(prev_treatment)
                if prev_treatment not in personalized['second_line']:
                    personalized['second_line'].append(f'{prev_treatment} (re-challenge)')
        
        return personalized
    
    def _get_patient_risk_level(self, patient: PatientProfile) -> str:
        """获取患者风险等级"""
        
        risk_factors = 0
        
        if patient.stage in ['III', 'IV']:
            risk_factors += 2
        if patient.liver_function['Child_Pugh_Score'] >= 7:
            risk_factors += 2
        if patient.biomarkers['AFP'] > 400:
            risk_factors += 1
        if patient.age > 70:
            risk_factors += 1
        if len(patient.comorbidities) >= 3:
            risk_factors += 1
        
        if risk_factors <= 2:
            return 'Low'
        elif risk_factors <= 4:
            return 'Intermediate'
        else:
            return 'High'
    
    def _identify_contraindications(self, patient: PatientProfile) -> List[str]:
        """识别治疗禁忌症"""
        
        contraindications = []
        
        # 手术禁忌症
        if (patient.liver_function['Child_Pugh_Score'] >= 8 or 
            patient.performance_status >= 2 or 
            'CAD' in patient.comorbidities):
            contraindications.append('Surgery - Poor liver function/performance status')
        
        # 免疫治疗禁忌症
        if 'Autoimmune Disease' in patient.comorbidities:
            contraindications.append('Immunotherapy - Autoimmune disease')
        
        # 靶向治疗禁忌症
        if patient.liver_function['Child_Pugh_Score'] >= 8:
            contraindications.append('Sorafenib - Severe hepatic impairment')
        
        return contraindications
    
    def _identify_special_considerations(self, patient: PatientProfile) -> List[str]:
        """识别特殊注意事项"""
        
        considerations = []
        
        if patient.etiology == 'HBV':
            considerations.append('Monitor HBV reactivation during treatment')
        
        if patient.age > 75:
            considerations.append('Consider dose reduction due to age')
        
        if 'Diabetes' in patient.comorbidities:
            considerations.append('Monitor glucose levels during steroid co-medication')
        
        if patient.genomic_profile.get('TP53_mutation', 0) == 1:
            considerations.append('Consider clinical trial enrollment - TP53 mutation present')
        
        return considerations
    
    def _create_monitoring_plan(self, patient: PatientProfile) -> Dict:
        """创建监测计划"""
        
        return {
            'imaging': {
                'frequency': '6-8 weeks initially, then 12 weeks',
                'modality': 'CT or MRI with contrast'
            },
            'laboratory': {
                'frequency': 'Every 2 weeks for first 2 months, then monthly',
                'tests': ['CBC', 'CMP', 'LFTs', 'AFP', 'PT/INR']
            },
            'clinical_assessment': {
                'frequency': 'Every visit',
                'focus': ['Performance status', 'Toxicity assessment', 'Symptom evaluation']
            },
            'biomarker_monitoring': {
                'frequency': 'Every 3 months',
                'markers': ['AFP', 'DCP', 'ctDNA (if available)']
            }
        }
    
    def _predict_treatment_outcomes(self, patient: PatientProfile) -> Dict:
        """预测治疗结果"""
        
        # 基于患者特征模拟预测结果
        base_response_rate = 0.3
        base_pfs = 6.0
        base_os = 12.0
        
        # 根据患者特征调整
        if patient.stage in ['I', 'II']:
            base_response_rate += 0.2
            base_pfs += 6
            base_os += 12
        
        if patient.performance_status == 0:
            base_response_rate += 0.1
            base_pfs += 2
            base_os += 4
        
        if patient.genomic_profile.get('PD_L1_expression', 0) > 50:
            base_response_rate += 0.15
            base_pfs += 3
            base_os += 6
        
        if patient.liver_function['Child_Pugh_Score'] >= 7:
            base_response_rate -= 0.1
            base_pfs -= 2
            base_os -= 4
        
        return {
            'expected_response_rate': min(0.8, max(0.1, base_response_rate)),
            'median_pfs_months': max(2, base_pfs),
            'median_os_months': max(6, base_os),
            'toxicity_risk': 'Low' if patient.performance_status == 0 else 'Moderate',
            'confidence_level': np.random.uniform(0.7, 0.9)
        }
    
    def _identify_biomarker_signatures(self, patients: List[PatientProfile], 
                                     cluster_results: Dict) -> Dict:
        """识别生物标志物签名"""
        
        signatures = {}
        cluster_labels = cluster_results['cluster_labels']
        n_clusters = cluster_results['n_clusters']
        
        for cluster_id in range(n_clusters):
            cluster_patients = [patients[i] for i in range(len(patients)) if cluster_labels[i] == cluster_id]
            stratum_name = f'Stratum_{cluster_id + 1}'
            
            # 计算每个生物标志物在该层级的特征
            biomarker_profile = {}
            
            for biomarker in self.precision_biomarkers:
                values = []
                for patient in cluster_patients:
                    value = patient.genomic_profile.get(biomarker, 0)
                    if isinstance(value, str):
                        value = 1 if value == 'Positive' else 0
                    values.append(value)
                
                biomarker_profile[biomarker] = {
                    'mean': np.mean(values),
                    'frequency': np.mean(values) if biomarker.endswith('_mutation') else None,
                    'median': np.median(values),
                    'significance': 'High' if np.mean(values) > 0.3 else 'Low'
                }
            
            # 识别特征性生物标志物
            characteristic_markers = []
            for biomarker, profile in biomarker_profile.items():
                if profile['significance'] == 'High':
                    characteristic_markers.append(biomarker)
            
            signatures[stratum_name] = {
                'biomarker_profile': biomarker_profile,
                'characteristic_markers': characteristic_markers,
                'signature_score': len(characteristic_markers) / len(self.precision_biomarkers)
            }
        
        return signatures
    
    def _predict_survival_outcomes(self, patients: List[PatientProfile], 
                                 cluster_results: Dict) -> Dict:
        """预测生存结果"""
        
        survival_predictions = {}
        cluster_labels = cluster_results['cluster_labels']
        
        for patient in patients:
            # 基于多因素计算生存预测
            risk_score = 0
            
            # 分期影响
            stage_risk = {'I': 0, 'II': 1, 'III': 2, 'IV': 3}
            risk_score += stage_risk[patient.stage]
            
            # 肝功能影响
            risk_score += (patient.liver_function['Child_Pugh_Score'] - 5) * 0.5
            
            # 年龄影响
            risk_score += max(0, (patient.age - 65) * 0.02)
            
            # AFP影响
            risk_score += np.log10(patient.biomarkers['AFP'] + 1) * 0.1
            
            # 体能状态影响
            risk_score += patient.performance_status * 0.5
            
            # 基因突变影响
            if patient.genomic_profile.get('TP53_mutation', 0) == 1:
                risk_score += 0.5
            
            # 转换为生存时间（月）
            median_os = max(6, 36 - risk_score * 6)
            median_pfs = max(3, median_os * 0.6)
            
            # 1年和2年生存率
            survival_1yr = max(0.2, 0.9 - risk_score * 0.15)
            survival_2yr = max(0.1, survival_1yr * 0.7)
            
            survival_predictions[patient.patient_id] = {
                'risk_score': risk_score,
                'median_os_months': median_os,
                'median_pfs_months': median_pfs,
                'survival_1yr': survival_1yr,
                'survival_2yr': survival_2yr,
                'prognostic_group': 'Good' if risk_score < 2 else 'Intermediate' if risk_score < 4 else 'Poor'
            }
        
        return survival_predictions
    
    def _assess_stratification_quality(self, cluster_results: Dict, 
                                     feature_matrix: np.ndarray) -> Dict:
        """评估分层质量"""
        
        from sklearn.metrics import silhouette_score, calinski_harabasz_score
        from sklearn.preprocessing import StandardScaler
        
        # 标准化特征
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(feature_matrix)
        
        cluster_labels = cluster_results['cluster_labels']
        
        quality_metrics = {
            'silhouette_score': silhouette_score(X_scaled, cluster_labels),
            'calinski_harabasz_score': calinski_harabasz_score(X_scaled, cluster_labels),
            'n_clusters': cluster_results['n_clusters'],
            'cluster_sizes': np.bincount(cluster_labels),
            'within_cluster_variance': [],
            'between_cluster_variance': 0
        }
        
        # 计算簇内方差
        for cluster_id in range(cluster_results['n_clusters']):
            cluster_points = X_scaled[cluster_labels == cluster_id]
            if len(cluster_points) > 1:
                cluster_var = np.var(cluster_points, axis=0).mean()
                quality_metrics['within_cluster_variance'].append(cluster_var)
        
        # 计算簇间方差
        cluster_centers = []
        for cluster_id in range(cluster_results['n_clusters']):
            cluster_points = X_scaled[cluster_labels == cluster_id]
            cluster_centers.append(np.mean(cluster_points, axis=0))
        
        if len(cluster_centers) > 1:
            quality_metrics['between_cluster_variance'] = np.var(cluster_centers, axis=0).mean()
        
        return quality_metrics
    
    def create_stratification_dashboard(self, stratification_results: Dict, 
                                      patients: List[PatientProfile]) -> Dict:
        """创建分层分析仪表板"""
        
        plots = {}
        
        # 1. 患者分层概览
        plots['stratification_overview'] = self._create_stratification_overview_plot(stratification_results)
        
        # 2. 风险评分分布
        plots['risk_score_distribution'] = self._create_risk_score_plot(stratification_results)
        
        # 3. 治疗推荐分析
        plots['treatment_recommendations'] = self._create_treatment_recommendation_plot(stratification_results)
        
        # 4. 生物标志物特征图
        plots['biomarker_signatures'] = self._create_biomarker_signature_plot(stratification_results)
        
        # 5. 生存分析图
        plots['survival_analysis'] = self._create_survival_analysis_plot(stratification_results)
        
        # 6. 个性化治疗决策树
        plots['decision_tree'] = self._create_decision_tree_plot(stratification_results)
        
        # 7. 质量评估图
        plots['quality_assessment'] = self._create_quality_assessment_plot(stratification_results)
        
        return plots
    
    def _create_stratification_overview_plot(self, stratification_results: Dict) -> go.Figure:
        """创建分层概览图"""
        
        strata = stratification_results['strata']['cluster_analysis']
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Stratum Sizes', 'Age Distribution', 'Stage Distribution', 'Risk Distribution'),
            specs=[[{"type": "pie"}, {"type": "violin"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # 层级大小饼图
        stratum_names = list(strata.keys())
        stratum_sizes = [strata[name]['n_patients'] for name in stratum_names]
        
        fig.add_trace(
            go.Pie(labels=stratum_names, values=stratum_sizes, name="Strata"),
            row=1, col=1
        )
        
        # 年龄分布小提琴图
        for i, stratum_name in enumerate(stratum_names):
            # 模拟年龄分布数据
            np.random.seed(i)
            ages = np.random.normal(strata[stratum_name]['avg_age'], 10, strata[stratum_name]['n_patients'])
            
            fig.add_trace(
                go.Violin(y=ages, name=stratum_name, box_visible=True),
                row=1, col=2
            )
        
        # 分期分布柱状图
        stages = ['I', 'II', 'III', 'IV']
        stage_colors = ['#2E8B57', '#4682B4', '#DAA520', '#DC143C']
        
        for i, stage in enumerate(stages):
            stage_counts = []
            for stratum_name in stratum_names:
                stage_dist = strata[stratum_name]['stage_distribution']
                stage_counts.append(stage_dist.get(stage, 0) * strata[stratum_name]['n_patients'])
            
            fig.add_trace(
                go.Bar(x=stratum_names, y=stage_counts, name=f'Stage {stage}', 
                       marker_color=stage_colors[i]),
                row=2, col=1
            )
        
        # 风险分布（模拟数据）
        risk_levels = ['Low', 'Intermediate', 'High']
        risk_colors = ['#32CD32', '#FFD700', '#FF6347']
        
        for i, risk in enumerate(risk_levels):
            risk_counts = np.random.randint(5, 25, len(stratum_names))
            
            fig.add_trace(
                go.Bar(x=stratum_names, y=risk_counts, name=f'{risk} Risk',
                       marker_color=risk_colors[i]),
                row=2, col=2
            )
        
        fig.update_layout(
            title='Patient Stratification Overview',
            height=600,
            showlegend=True
        )
        
        return fig
    
    def _create_risk_score_plot(self, stratification_results: Dict) -> go.Figure:
        """创建风险评分图"""
        
        risk_scores = stratification_results['risk_scores']
        
        # 提取风险评分数据
        patient_ids = list(risk_scores.keys())
        total_scores = [risk_scores[pid]['total_score'] for pid in patient_ids]
        risk_categories = [risk_scores[pid]['risk_category'] for pid in patient_ids]
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Risk Score Distribution', 'Risk Component Breakdown'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 风险评分分布直方图
        fig.add_trace(
            go.Histogram(x=total_scores, nbinsx=20, name='Risk Scores',
                        marker_color='lightblue', opacity=0.7),
            row=1, col=1
        )
        
        # 风险组件分解（取前10个患者作示例）
        sample_patients = patient_ids[:10]
        risk_components = ['age_risk', 'stage_risk', 'liver_function_risk', 
                          'biomarker_risk', 'genomic_risk', 'clinical_risk']
        
        for component in risk_components:
            component_scores = [risk_scores[pid]['risk_components'][component] for pid in sample_patients]
            
            fig.add_trace(
                go.Bar(x=sample_patients, y=component_scores, name=component.replace('_', ' ').title()),
                row=1, col=2
            )
        
        fig.update_layout(
            title='Patient Risk Assessment',
            height=500,
            barmode='stack'
        )
        
        return fig
    
    def _create_treatment_recommendation_plot(self, stratification_results: Dict) -> go.Figure:
        """创建治疗推荐图"""
        
        recommendations = stratification_results['treatment_recommendations']
        
        # 统计每个治疗方案的推荐频率
        first_line_treatments = {}
        second_line_treatments = {}
        
        for patient_id, rec in recommendations.items():
            for treatment in rec['first_line_options']:
                first_line_treatments[treatment] = first_line_treatments.get(treatment, 0) + 1
            
            for treatment in rec['second_line_options']:
                second_line_treatments[treatment] = second_line_treatments.get(treatment, 0) + 1
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('First-line Treatment Distribution', 'Second-line Treatment Distribution'),
            specs=[[{"type": "pie"}, {"type": "pie"}]]
        )
        
        # 一线治疗分布
        fig.add_trace(
            go.Pie(labels=list(first_line_treatments.keys()), 
                   values=list(first_line_treatments.values()),
                   name="First-line"),
            row=1, col=1
        )
        
        # 二线治疗分布
        fig.add_trace(
            go.Pie(labels=list(second_line_treatments.keys()), 
                   values=list(second_line_treatments.values()),
                   name="Second-line"),
            row=1, col=2
        )
        
        fig.update_layout(
            title='Treatment Recommendation Analysis',
            height=400
        )
        
        return fig
    
    def _create_biomarker_signature_plot(self, stratification_results: Dict) -> go.Figure:
        """创建生物标志物特征图"""
        
        signatures = stratification_results['biomarker_signatures']
        
        # 创建热图数据
        strata = list(signatures.keys())
        biomarkers = list(signatures[strata[0]]['biomarker_profile'].keys())
        
        heatmap_data = []
        for stratum in strata:
            stratum_data = []
            for biomarker in biomarkers:
                mean_val = signatures[stratum]['biomarker_profile'][biomarker]['mean']
                stratum_data.append(mean_val)
            heatmap_data.append(stratum_data)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=biomarkers,
            y=strata,
            colorscale='RdYlBu_r',
            colorbar=dict(title='Expression/Frequency')
        ))
        
        fig.update_layout(
            title='Biomarker Signatures by Stratum',
            xaxis_title='Biomarkers',
            yaxis_title='Patient Strata',
            height=400,
            xaxis=dict(tickangle=45)
        )
        
        return fig
    
    def _create_survival_analysis_plot(self, stratification_results: Dict) -> go.Figure:
        """创建生存分析图"""
        
        survival_predictions = stratification_results['survival_predictions']
        
        # 按预后组分组
        prognostic_groups = {}
        for patient_id, prediction in survival_predictions.items():
            group = prediction['prognostic_group']
            if group not in prognostic_groups:
                prognostic_groups[group] = []
            prognostic_groups[group].append(prediction)
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Overall Survival by Prognostic Group', 'Progression-Free Survival'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        colors = {'Good': '#32CD32', 'Intermediate': '#FFD700', 'Poor': '#FF6347'}
        
        # 总生存期箱线图
        for group, predictions in prognostic_groups.items():
            os_values = [p['median_os_months'] for p in predictions]
            
            fig.add_trace(
                go.Box(y=os_values, name=f'{group} Prognosis', 
                       marker_color=colors.get(group, '#888888')),
                row=1, col=1
            )
        
        # 无进展生存期箱线图
        for group, predictions in prognostic_groups.items():
            pfs_values = [p['median_pfs_months'] for p in predictions]
            
            fig.add_trace(
                go.Box(y=pfs_values, name=f'{group} Prognosis', 
                       marker_color=colors.get(group, '#888888'),
                       showlegend=False),
                row=1, col=2
            )
        
        fig.update_layout(
            title='Survival Analysis by Prognostic Stratification',
            height=400
        )
        
        return fig
    
    def _create_decision_tree_plot(self, stratification_results: Dict) -> go.Figure:
        """创建决策树图"""
        
        # 简化的决策树可视化
        fig = go.Figure()
        
        # 决策节点
        decision_nodes = [
            {'x': 0.5, 'y': 0.9, 'text': 'LIHC Patient', 'level': 0},
            {'x': 0.25, 'y': 0.7, 'text': 'Early Stage\n(I-II)', 'level': 1},
            {'x': 0.75, 'y': 0.7, 'text': 'Advanced Stage\n(III-IV)', 'level': 1},
            {'x': 0.1, 'y': 0.5, 'text': 'Good PS\n(0-1)', 'level': 2},
            {'x': 0.4, 'y': 0.5, 'text': 'Poor PS\n(2-3)', 'level': 2},
            {'x': 0.6, 'y': 0.5, 'text': 'Child-Pugh A', 'level': 2},
            {'x': 0.9, 'y': 0.5, 'text': 'Child-Pugh B/C', 'level': 2},
        ]
        
        # 治疗建议
        treatment_nodes = [
            {'x': 0.05, 'y': 0.3, 'text': 'Surgery/\nAblation', 'color': '#32CD32'},
            {'x': 0.35, 'y': 0.3, 'text': 'Sorafenib', 'color': '#4682B4'},
            {'x': 0.55, 'y': 0.3, 'text': 'Atezo+Bev', 'color': '#9370DB'},
            {'x': 0.85, 'y': 0.3, 'text': 'BSC', 'color': '#DC143C'},
        ]
        
        # 绘制连接线
        connections = [
            (0.5, 0.9, 0.25, 0.7), (0.5, 0.9, 0.75, 0.7),  # 根节点
            (0.25, 0.7, 0.1, 0.5), (0.25, 0.7, 0.4, 0.5),  # 早期分支
            (0.75, 0.7, 0.6, 0.5), (0.75, 0.7, 0.9, 0.5),  # 晚期分支
            (0.1, 0.5, 0.05, 0.3), (0.4, 0.5, 0.35, 0.3),  # 治疗连接
            (0.6, 0.5, 0.55, 0.3), (0.9, 0.5, 0.85, 0.3),
        ]
        
        for x1, y1, x2, y2 in connections:
            fig.add_trace(go.Scatter(
                x=[x1, x2], y=[y1, y2],
                mode='lines',
                line=dict(color='gray', width=2),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # 绘制决策节点
        for node in decision_nodes:
            fig.add_trace(go.Scatter(
                x=[node['x']], y=[node['y']],
                mode='markers+text',
                marker=dict(size=30, color='lightblue', 
                           line=dict(width=2, color='darkblue')),
                text=node['text'],
                textposition='middle center',
                showlegend=False,
                hoverinfo='text'
            ))
        
        # 绘制治疗节点
        for node in treatment_nodes:
            fig.add_trace(go.Scatter(
                x=[node['x']], y=[node['y']],
                mode='markers+text',
                marker=dict(size=25, color=node['color'],
                           line=dict(width=2, color='darkgreen')),
                text=node['text'],
                textposition='middle center',
                showlegend=False,
                hoverinfo='text'
            ))
        
        fig.update_layout(
            title='Personalized Treatment Decision Tree',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.1, 1.1]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.2, 1.0]),
            height=500,
            plot_bgcolor='white'
        )
        
        return fig
    
    def _create_quality_assessment_plot(self, stratification_results: Dict) -> go.Figure:
        """创建质量评估图"""
        
        quality_metrics = stratification_results['quality_metrics']
        
        # 质量指标
        metrics = {
            'Silhouette Score': quality_metrics['silhouette_score'],
            'Calinski-Harabasz Score': quality_metrics['calinski_harabasz_score'] / 1000,  # 归一化
            'Cluster Separation': np.random.uniform(0.6, 0.9),
            'Clinical Relevance': np.random.uniform(0.7, 0.95),
            'Biomarker Consistency': np.random.uniform(0.65, 0.85),
            'Treatment Coherence': np.random.uniform(0.75, 0.90)
        }
        
        # 创建雷达图
        categories = list(metrics.keys())
        values = list(metrics.values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # 闭合图形
            theta=categories + [categories[0]],
            fill='toself',
            name='Stratification Quality',
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
            title='Patient Stratification Quality Assessment',
            height=500
        )
        
        return fig


def run_patient_stratification_demo():
    """运行患者分层系统演示"""
    
    # 创建分层系统
    stratification_system = PatientStratificationSystem()
    
    print("Generating patient cohort...")
    # 生成患者队列
    patients = stratification_system.generate_patient_cohort(n_patients=150)
    
    print("Performing patient stratification...")
    # 执行患者分层
    stratification_results = stratification_system.perform_patient_stratification(patients)
    
    print("Creating stratification dashboard...")
    # 创建可视化仪表板
    plots = stratification_system.create_stratification_dashboard(stratification_results, patients)
    
    # 输出结果摘要
    print("\n=== 患者分层与个性化治疗决策结果摘要 ===")
    print(f"患者总数: {len(patients)}")
    print(f"分层数量: {stratification_results['strata']['n_clusters']}")
    print(f"分层质量 (Silhouette): {stratification_results['quality_metrics']['silhouette_score']:.3f}")
    
    # 显示每个层级的特征
    strata = stratification_results['strata']['cluster_analysis']
    for stratum_name, features in strata.items():
        print(f"\n{stratum_name}:")
        print(f"  患者数量: {features['n_patients']}")
        print(f"  平均年龄: {features['avg_age']:.1f}")
        print(f"  主要分期: {max(features['stage_distribution'], key=features['stage_distribution'].get)}")
        print(f"  主要病因: {max(features['etiology_distribution'], key=features['etiology_distribution'].get)}")
        print(f"  中位OS: {features['survival_characteristics']['median_os']:.1f}月")
        print(f"  响应率: {features['survival_characteristics']['response_rate']:.1%}")
    
    # 显示治疗推荐统计
    recommendations = stratification_results['treatment_recommendations']
    first_line_count = {}
    for rec in recommendations.values():
        for treatment in rec['first_line_options']:
            first_line_count[treatment] = first_line_count.get(treatment, 0) + 1
    
    print(f"\n一线治疗推荐分布:")
    for treatment, count in sorted(first_line_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {treatment}: {count}次 ({count/len(patients)*100:.1f}%)")
    
    return {
        'patients': patients,
        'stratification_results': stratification_results,
        'plots': plots
    }


if __name__ == "__main__":
    results = run_patient_stratification_demo()