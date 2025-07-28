"""
Drug Combination Therapy Prediction Module for LIHC Platform
药物组合疗法预测与协同效应分析系统
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, List, Optional, Tuple, Union
import warnings
from datetime import datetime
from itertools import combinations
warnings.filterwarnings('ignore')

class DrugCombinationPredictor:
    """药物组合疗法预测器"""
    
    def __init__(self):
        # FDA批准的肝癌治疗药物
        self.approved_drugs = {
            'Sorafenib': {
                'type': 'Multi-kinase inhibitor',
                'targets': ['VEGFR', 'PDGFR', 'RAF'],
                'mechanism': 'Angiogenesis + Proliferation inhibition',
                'resistance_genes': ['EGFR', 'MET', 'FGF'],
                'biomarkers': ['VEGF', 'PDGF']
            },
            'Lenvatinib': {
                'type': 'Multi-kinase inhibitor', 
                'targets': ['VEGFR', 'FGFR', 'PDGFR', 'RET', 'KIT'],
                'mechanism': 'Angiogenesis inhibition',
                'resistance_genes': ['MET', 'AXL'],
                'biomarkers': ['VEGFR2', 'FGFR1']
            },
            'Regorafenib': {
                'type': 'Multi-kinase inhibitor',
                'targets': ['VEGFR', 'TIE2', 'PDGFR', 'FGFR', 'KIT', 'RET', 'RAF'],
                'mechanism': 'Angiogenesis + Oncogenic kinase inhibition',
                'resistance_genes': ['BRAF', 'KRAS'],
                'biomarkers': ['VEGF', 'TIE2']
            },
            'Cabozantinib': {
                'type': 'Multi-kinase inhibitor',
                'targets': ['MET', 'VEGFR2', 'RET', 'KIT', 'FLT3'],
                'mechanism': 'MET + Angiogenesis inhibition',
                'resistance_genes': ['MET amplification'],
                'biomarkers': ['MET', 'VEGFR2']
            },
            'Atezolizumab': {
                'type': 'Immune checkpoint inhibitor',
                'targets': ['PD-L1'],
                'mechanism': 'Immune activation',
                'resistance_genes': ['STK11', 'KEAP1'],
                'biomarkers': ['PD-L1', 'TMB', 'MSI']
            },
            'Nivolumab': {
                'type': 'Immune checkpoint inhibitor',
                'targets': ['PD-1'],
                'mechanism': 'T-cell activation',
                'resistance_genes': ['B2M', 'JAK1', 'JAK2'],
                'biomarkers': ['PD-1', 'CD8', 'TMB']
            },
            'Pembrolizumab': {
                'type': 'Immune checkpoint inhibitor',
                'targets': ['PD-1'],
                'mechanism': 'T-cell activation',
                'resistance_genes': ['STK11', 'KEAP1'],
                'biomarkers': ['PD-L1', 'TMB']
            },
            'Bevacizumab': {
                'type': 'Monoclonal antibody',
                'targets': ['VEGF-A'],
                'mechanism': 'Angiogenesis inhibition',
                'resistance_genes': ['VEGF', 'ANGPT2'],
                'biomarkers': ['VEGF', 'VEGFR2']
            }
        }
        
        # 实验性药物
        self.experimental_drugs = {
            'Ramucirumab': {
                'type': 'VEGFR2 antagonist',
                'targets': ['VEGFR2'],
                'mechanism': 'Angiogenesis inhibition',
                'phase': 'Phase III'
            },
            'Tivantinib': {
                'type': 'MET inhibitor',
                'targets': ['MET'],
                'mechanism': 'Growth factor inhibition',
                'phase': 'Phase II'
            },
            'Durvalumab': {
                'type': 'PD-L1 inhibitor',
                'targets': ['PD-L1'],
                'mechanism': 'Immune checkpoint inhibition',
                'phase': 'Phase III'
            }
        }
        
        # 协同效应评估模型
        self.synergy_models = [
            'Bliss Independence',
            'Loewe Additivity', 
            'Zero Interaction Potency',
            'Highest Single Agent',
            'Combination Index'
        ]
        
    def predict_drug_combinations(self, patient_profile: Dict, 
                                 available_drugs: Optional[List[str]] = None) -> Dict:
        """预测最佳药物组合"""
        
        if available_drugs is None:
            available_drugs = list(self.approved_drugs.keys())
        
        results = {
            'patient_id': patient_profile.get('patient_id', 'Unknown'),
            'analysis_date': datetime.now().isoformat(),
            'single_drug_predictions': {},
            'combination_predictions': {},
            'synergy_analysis': {},
            'resistance_assessment': {},
            'optimal_combinations': {},
            'treatment_schedule': {}
        }
        
        # 1. 单药效果预测
        single_drug_results = self._predict_single_drug_effects(patient_profile, available_drugs)
        results['single_drug_predictions'] = single_drug_results
        
        # 2. 组合效果预测
        combination_results = self._predict_combination_effects(patient_profile, available_drugs)
        results['combination_predictions'] = combination_results
        
        # 3. 协同效应分析
        synergy_results = self._analyze_drug_synergy(patient_profile, available_drugs)
        results['synergy_analysis'] = synergy_results
        
        # 4. 耐药性评估
        resistance_results = self._assess_resistance_potential(patient_profile, available_drugs)
        results['resistance_assessment'] = resistance_results
        
        # 5. 最优组合推荐
        optimal_results = self._recommend_optimal_combinations(
            single_drug_results, combination_results, synergy_results, resistance_results
        )
        results['optimal_combinations'] = optimal_results
        
        # 6. 治疗计划制定
        treatment_schedule = self._generate_treatment_schedule(optimal_results, patient_profile)
        results['treatment_schedule'] = treatment_schedule
        
        return results
    
    def _predict_single_drug_effects(self, patient_profile: Dict, drugs: List[str]) -> Dict:
        """预测单药效果"""
        
        single_drug_results = {}
        
        for drug in drugs:
            if drug not in self.approved_drugs:
                continue
                
            drug_info = self.approved_drugs[drug]
            
            # 基于生物标志物预测响应概率
            response_prob = self._calculate_response_probability(patient_profile, drug_info)
            
            # 预测副作用
            side_effects = self._predict_side_effects(patient_profile, drug_info)
            
            # 计算治疗指数
            therapeutic_index = self._calculate_therapeutic_index(response_prob, side_effects)
            
            single_drug_results[drug] = {
                'response_probability': response_prob,
                'predicted_pfs': np.random.exponential(8) + 2,  # 模拟PFS (月)
                'predicted_os': np.random.exponential(15) + 8,  # 模拟OS (月)
                'side_effects': side_effects,
                'therapeutic_index': therapeutic_index,
                'biomarker_match': self._assess_biomarker_match(patient_profile, drug_info),
                'confidence': np.random.uniform(0.6, 0.9)
            }
        
        return single_drug_results
    
    def _predict_combination_effects(self, patient_profile: Dict, drugs: List[str]) -> Dict:
        """预测组合效果"""
        
        combination_results = {}
        
        # 生成所有可能的2-drug和3-drug组合
        for combo_size in [2, 3]:
            for combo in combinations(drugs, combo_size):
                combo_name = ' + '.join(combo)
                
                # 计算组合效果
                combo_effect = self._calculate_combination_effect(patient_profile, combo)
                
                combination_results[combo_name] = {
                    'drugs': list(combo),
                    'predicted_response_rate': combo_effect['response_rate'],
                    'predicted_pfs': combo_effect['pfs'],
                    'predicted_os': combo_effect['os'],
                    'synergy_score': combo_effect['synergy_score'],
                    'toxicity_score': combo_effect['toxicity_score'],
                    'combination_index': combo_effect['combination_index'],
                    'mechanism_compatibility': combo_effect['mechanism_compatibility'],
                    'dosing_feasibility': combo_effect['dosing_feasibility']
                }
        
        return combination_results
    
    def _analyze_drug_synergy(self, patient_profile: Dict, drugs: List[str]) -> Dict:
        """分析药物协同效应"""
        
        synergy_results = {
            'synergy_matrix': {},
            'antagonism_pairs': [],
            'synergistic_pairs': [],
            'additive_pairs': [],
            'mechanism_interactions': {}
        }
        
        # 构建协同效应矩阵
        drug_pairs = list(combinations(drugs, 2))
        
        for drug1, drug2 in drug_pairs:
            synergy_score = self._calculate_synergy_score(patient_profile, drug1, drug2)
            
            pair_name = f"{drug1} + {drug2}"
            synergy_results['synergy_matrix'][pair_name] = synergy_score
            
            # 分类协同效应
            if synergy_score > 0.3:
                synergy_results['synergistic_pairs'].append(pair_name)
            elif synergy_score < -0.3:
                synergy_results['antagonism_pairs'].append(pair_name)
            else:
                synergy_results['additive_pairs'].append(pair_name)
            
            # 机制相互作用分析
            interaction = self._analyze_mechanism_interaction(drug1, drug2)
            synergy_results['mechanism_interactions'][pair_name] = interaction
        
        return synergy_results
    
    def _assess_resistance_potential(self, patient_profile: Dict, drugs: List[str]) -> Dict:
        """评估耐药性潜力"""
        
        resistance_results = {
            'inherent_resistance': {},
            'acquired_resistance_risk': {},
            'resistance_mechanisms': {},
            'combination_resistance_delay': {}
        }
        
        for drug in drugs:
            if drug not in self.approved_drugs:
                continue
                
            drug_info = self.approved_drugs[drug]
            
            # 评估固有耐药性
            inherent_resistance = self._assess_inherent_resistance(patient_profile, drug_info)
            resistance_results['inherent_resistance'][drug] = inherent_resistance
            
            # 预测获得性耐药风险
            acquired_risk = self._predict_acquired_resistance(patient_profile, drug_info)
            resistance_results['acquired_resistance_risk'][drug] = acquired_risk
            
            # 识别耐药机制
            mechanisms = self._identify_resistance_mechanisms(patient_profile, drug_info)
            resistance_results['resistance_mechanisms'][drug] = mechanisms
        
        # 评估组合对耐药性的延缓效果
        for combo in combinations(drugs, 2):
            combo_name = ' + '.join(combo)
            delay_effect = self._assess_resistance_delay(patient_profile, combo)
            resistance_results['combination_resistance_delay'][combo_name] = delay_effect
        
        return resistance_results
    
    def _recommend_optimal_combinations(self, single_drug_results: Dict,
                                      combination_results: Dict,
                                      synergy_results: Dict,
                                      resistance_results: Dict) -> Dict:
        """推荐最优组合"""
        
        recommendations = {
            'first_line': [],
            'second_line': [],
            'third_line': [],
            'personalized_ranking': {},
            'treatment_rationale': {}
        }
        
        # 计算综合评分
        all_treatments = {}
        
        # 单药治疗
        for drug, results in single_drug_results.items():
            score = self._calculate_treatment_score(
                response_prob=results['response_probability'],
                pfs=results['predicted_pfs'],
                os=results['predicted_os'],
                toxicity=results['side_effects']['severity_score'],
                confidence=results['confidence']
            )
            all_treatments[drug] = {
                'type': 'monotherapy',
                'score': score,
                'details': results
            }
        
        # 组合治疗
        for combo, results in combination_results.items():
            score = self._calculate_treatment_score(
                response_prob=results['predicted_response_rate'],
                pfs=results['predicted_pfs'], 
                os=results['predicted_os'],
                toxicity=results['toxicity_score'],
                confidence=0.8
            )
            all_treatments[combo] = {
                'type': 'combination',
                'score': score,
                'details': results
            }
        
        # 排序和分类
        sorted_treatments = sorted(all_treatments.items(), key=lambda x: x[1]['score'], reverse=True)
        
        # 一线治疗（Top 3）
        recommendations['first_line'] = [name for name, _ in sorted_treatments[:3]]
        
        # 二线治疗（Next 3）
        recommendations['second_line'] = [name for name, _ in sorted_treatments[3:6]]
        
        # 三线治疗（Next 3）
        recommendations['third_line'] = [name for name, _ in sorted_treatments[6:9]]
        
        # 个性化排名
        for name, data in sorted_treatments:
            recommendations['personalized_ranking'][name] = {
                'rank': sorted_treatments.index((name, data)) + 1,
                'score': data['score'],
                'type': data['type']
            }
        
        # 治疗理由
        for name in recommendations['first_line']:
            recommendations['treatment_rationale'][name] = self._generate_treatment_rationale(
                name, all_treatments[name], synergy_results, resistance_results
            )
        
        return recommendations
    
    def _generate_treatment_schedule(self, optimal_combinations: Dict, patient_profile: Dict) -> Dict:
        """生成治疗计划"""
        
        schedule = {
            'treatment_sequence': [],
            'dosing_schedule': {},
            'monitoring_plan': {},
            'progression_criteria': {},
            'safety_monitoring': {}
        }
        
        # 治疗序列
        first_line = optimal_combinations['first_line'][0] if optimal_combinations['first_line'] else None
        second_line = optimal_combinations['second_line'][0] if optimal_combinations['second_line'] else None
        
        if first_line:
            schedule['treatment_sequence'].append({
                'line': 'First-line',
                'treatment': first_line,
                'expected_duration': '6-12 months',
                'response_evaluation': '8-12 weeks'
            })
            
            # 给药方案
            schedule['dosing_schedule'][first_line] = self._generate_dosing_schedule(first_line, patient_profile)
            
            # 监测计划
            schedule['monitoring_plan'][first_line] = self._generate_monitoring_plan(first_line, patient_profile)
        
        if second_line:
            schedule['treatment_sequence'].append({
                'line': 'Second-line',
                'treatment': second_line,
                'expected_duration': '4-8 months',
                'response_evaluation': '6-8 weeks'
            })
        
        # 疾病进展标准
        schedule['progression_criteria'] = {
            'radiological': 'RECIST 1.1 criteria',
            'biochemical': 'AFP doubling time < 2 months',
            'clinical': 'Performance status decline ≥ 2 points',
            'time_to_progression': 'No response after 12 weeks'
        }
        
        # 安全监测
        schedule['safety_monitoring'] = {
            'blood_counts': 'Weekly for first month, then bi-weekly',
            'liver_function': 'Bi-weekly',
            'cardiac_function': 'Baseline and every 3 months',
            'thyroid_function': 'Every 6 weeks (for immunotherapy)',
            'blood_pressure': 'Weekly (for anti-VEGF therapy)'
        }
        
        return schedule
    
    def _calculate_response_probability(self, patient_profile: Dict, drug_info: Dict) -> float:
        """计算响应概率"""
        base_response_rate = 0.15  # 基础响应率
        
        # 基于生物标志物调整
        biomarker_boost = 0
        if 'biomarkers' in patient_profile:
            for biomarker in drug_info['biomarkers']:
                if biomarker in patient_profile['biomarkers']:
                    biomarker_level = patient_profile['biomarkers'][biomarker]
                    # 处理字符串值（如'low', 'high'）和数值
                    if isinstance(biomarker_level, str):
                        if biomarker_level.lower() in ['high', 'positive']:
                            biomarker_boost += 0.2
                    elif isinstance(biomarker_level, (int, float)) and biomarker_level > 0.5:
                        biomarker_boost += 0.2
        
        # 基于突变状态调整
        mutation_effect = 0
        if 'mutations' in patient_profile:
            for gene in drug_info.get('targets', []):
                if gene in patient_profile['mutations']:
                    mutation_effect += 0.15
        
        # 基于临床特征调整
        clinical_adjustment = 0
        if 'stage' in patient_profile:
            stage = str(patient_profile['stage'])  # 确保转换为字符串
            if stage in ['I', 'II']:
                clinical_adjustment += 0.1
            elif stage == 'IV':
                clinical_adjustment -= 0.05
        
        final_prob = min(base_response_rate + biomarker_boost + mutation_effect + clinical_adjustment, 0.8)
        return max(final_prob, 0.05)
    
    def _predict_side_effects(self, patient_profile: Dict, drug_info: Dict) -> Dict:
        """预测副作用"""
        
        # 基础副作用谱
        base_side_effects = {
            'Multi-kinase inhibitor': {
                'fatigue': 0.6, 'diarrhea': 0.5, 'hypertension': 0.4,
                'hand_foot_syndrome': 0.3, 'decreased_appetite': 0.4
            },
            'Immune checkpoint inhibitor': {
                'fatigue': 0.4, 'rash': 0.3, 'diarrhea': 0.2,
                'hepatitis': 0.1, 'pneumonitis': 0.05
            },
            'Monoclonal antibody': {
                'hypertension': 0.3, 'proteinuria': 0.2, 'bleeding': 0.1,
                'thrombosis': 0.05
            }
        }
        
        drug_type = drug_info['type']
        side_effects = base_side_effects.get(drug_type, {})
        
        # 基于患者特征调整
        adjusted_effects = {}
        for effect, prob in side_effects.items():
            adjusted_prob = prob
            
            # 年龄调整
            if 'age' in patient_profile:
                age = float(patient_profile['age'])  # 确保转换为数字
                if age > 70:
                    adjusted_prob *= 1.2
                elif age < 50:
                    adjusted_prob *= 0.8
            
            # 性能状态调整
            if 'performance_status' in patient_profile:
                ps = float(patient_profile['performance_status'])  # 确保转换为数字
                if ps > 1:
                    adjusted_prob *= 1.3
            
            adjusted_effects[effect] = min(adjusted_prob, 0.9)
        
        # 计算总体严重程度评分
        severity_score = sum(adjusted_effects.values()) / len(adjusted_effects) if adjusted_effects else 0
        
        return {
            'individual_effects': adjusted_effects,
            'severity_score': severity_score,
            'manageable': severity_score < 0.6
        }
    
    def _calculate_therapeutic_index(self, response_prob: float, side_effects: Dict) -> float:
        """计算治疗指数"""
        benefit = response_prob
        risk = side_effects['severity_score']
        
        # 治疗指数 = 效益/风险比
        if risk == 0:
            return benefit * 10  # 避免除零
        
        therapeutic_index = benefit / risk
        return min(therapeutic_index, 10)  # 限制最大值
    
    def _assess_biomarker_match(self, patient_profile: Dict, drug_info: Dict) -> Dict:
        """评估生物标志物匹配度"""
        
        match_score = 0
        total_biomarkers = len(drug_info['biomarkers'])
        matched_biomarkers = []
        
        if 'biomarkers' in patient_profile and total_biomarkers > 0:
            for biomarker in drug_info['biomarkers']:
                if biomarker in patient_profile['biomarkers']:
                    level = patient_profile['biomarkers'][biomarker]
                    # 处理字符串和数值类型
                    if isinstance(level, str):
                        if level.lower() in ['high', 'positive']:
                            match_score += 1
                            matched_biomarkers.append(biomarker)
                    elif isinstance(level, (int, float)) and level > 0.5:  # 阳性阈值
                        match_score += 1
                        matched_biomarkers.append(biomarker)
            
            match_percentage = match_score / total_biomarkers
        else:
            match_percentage = 0
        
        return {
            'match_score': match_score,
            'total_biomarkers': total_biomarkers,
            'match_percentage': match_percentage,
            'matched_biomarkers': matched_biomarkers,
            'recommendation': 'Highly recommended' if match_percentage > 0.7 else 
                           'Recommended' if match_percentage > 0.3 else 'Consider alternatives'
        }
    
    def _calculate_combination_effect(self, patient_profile: Dict, combo: Tuple[str]) -> Dict:
        """计算组合效果"""
        
        # 基础组合效应模型
        individual_responses = []
        individual_toxicities = []
        
        for drug in combo:
            if drug in self.approved_drugs:
                drug_info = self.approved_drugs[drug]
                response = self._calculate_response_probability(patient_profile, drug_info)
                toxicity = self._predict_side_effects(patient_profile, drug_info)['severity_score']
                
                individual_responses.append(response)
                individual_toxicities.append(toxicity)
        
        # 协同效应计算（Bliss Independence模型）
        combined_response = 1 - np.prod([1 - r for r in individual_responses])
        
        # 添加协同效应调整
        synergy_bonus = self._calculate_synergy_bonus(combo)
        combined_response *= (1 + synergy_bonus)
        
        # 毒性叠加（通常是累加的）
        combined_toxicity = sum(individual_toxicities) * 0.8  # 适度折减
        
        # PFS和OS预测
        pfs = np.mean([8, 12]) + synergy_bonus * 4  # 月
        os = np.mean([15, 20]) + synergy_bonus * 6  # 月
        
        return {
            'response_rate': min(combined_response, 0.85),
            'pfs': pfs,
            'os': os,
            'synergy_score': synergy_bonus,
            'toxicity_score': min(combined_toxicity, 1.0),
            'combination_index': combined_response / (sum(individual_responses) / len(individual_responses)),
            'mechanism_compatibility': self._assess_mechanism_compatibility(combo),
            'dosing_feasibility': self._assess_dosing_feasibility(combo)
        }
    
    def _calculate_synergy_score(self, patient_profile: Dict, drug1: str, drug2: str) -> float:
        """计算协同效应评分"""
        
        # 获取药物信息
        drug1_info = self.approved_drugs.get(drug1, {})
        drug2_info = self.approved_drugs.get(drug2, {})
        
        # 机制互补性
        mechanism_synergy = 0
        if drug1_info.get('type') != drug2_info.get('type'):
            mechanism_synergy = 0.3  # 不同机制有协同潜力
        
        # 靶点互补性
        targets1 = set(drug1_info.get('targets', []))
        targets2 = set(drug2_info.get('targets', []))
        
        if targets1.isdisjoint(targets2):  # 不同靶点
            target_synergy = 0.2
        elif targets1 & targets2:  # 共同靶点
            target_synergy = -0.1  # 可能竞争
        else:
            target_synergy = 0
        
        # 基于患者特征的协同效应
        patient_synergy = np.random.uniform(-0.2, 0.4)  # 模拟个体化效应
        
        total_synergy = mechanism_synergy + target_synergy + patient_synergy
        return np.clip(total_synergy, -0.5, 0.8)
    
    def _analyze_mechanism_interaction(self, drug1: str, drug2: str) -> Dict:
        """分析药物机制相互作用"""
        
        drug1_info = self.approved_drugs.get(drug1, {})
        drug2_info = self.approved_drugs.get(drug2, {})
        
        interaction = {
            'interaction_type': 'unknown',
            'mechanism_overlap': 0.0,
            'pathway_convergence': [],
            'expected_effect': 'additive',
            'confidence': 0.5
        }
        
        # 分析机制重叠
        mechanisms1 = set(drug1_info.get('mechanisms', []))
        mechanisms2 = set(drug2_info.get('mechanisms', []))
        
        if mechanisms1 & mechanisms2:
            overlap = len(mechanisms1 & mechanisms2) / len(mechanisms1 | mechanisms2)
            interaction['mechanism_overlap'] = overlap
            if overlap > 0.5:
                interaction['interaction_type'] = 'competitive'
                interaction['expected_effect'] = 'antagonistic'
            else:
                interaction['interaction_type'] = 'complementary'
                interaction['expected_effect'] = 'synergistic'
        else:
            interaction['interaction_type'] = 'independent'
            interaction['expected_effect'] = 'additive'
        
        # 分析通路汇聚
        pathways1 = set(drug1_info.get('pathways', []))
        pathways2 = set(drug2_info.get('pathways', []))
        interaction['pathway_convergence'] = list(pathways1 & pathways2)
        
        # 设置置信度
        interaction['confidence'] = np.random.uniform(0.6, 0.9)
        
        return interaction
    
    def _calculate_synergy_bonus(self, combo: Tuple[str]) -> float:
        """计算协同效应奖励"""
        # 模拟已知的协同组合
        known_synergies = {
            ('Atezolizumab', 'Bevacizumab'): 0.25,
            ('Sorafenib', 'Regorafenib'): -0.1,  # 可能拮抗
            ('Nivolumab', 'Cabozantinib'): 0.2,
        }
        
        # 检查已知协同效应
        for known_combo, synergy in known_synergies.items():
            if set(combo) == set(known_combo):
                return synergy
        
        # 默认协同效应估计
        return np.random.uniform(-0.1, 0.3)
    
    def _assess_mechanism_compatibility(self, combo: Tuple[str]) -> Dict:
        """评估机制兼容性"""
        
        mechanisms = []
        for drug in combo:
            if drug in self.approved_drugs:
                mechanisms.append(self.approved_drugs[drug]['mechanism'])
        
        # 评估兼容性
        unique_mechanisms = set(mechanisms)
        
        if len(unique_mechanisms) == len(mechanisms):
            compatibility = 'Complementary'
            score = 0.8
        elif len(unique_mechanisms) == 1:
            compatibility = 'Overlapping'
            score = 0.3
        else:
            compatibility = 'Partially complementary'
            score = 0.6
        
        return {
            'compatibility': compatibility,
            'score': score,
            'mechanisms': mechanisms
        }
    
    def _assess_dosing_feasibility(self, combo: Tuple[str]) -> Dict:
        """评估给药可行性"""
        
        # 模拟给药间隔和冲突
        dosing_conflicts = []
        feasibility_score = 1.0
        
        # 检查已知的给药冲突
        if len(combo) > 2:
            feasibility_score *= 0.7  # 三药组合更复杂
            dosing_conflicts.append('Complex multi-drug scheduling')
        
        # 肝毒性药物组合
        hepatotoxic_drugs = ['Sorafenib', 'Lenvatinib', 'Regorafenib']
        hepatotoxic_count = sum(1 for drug in combo if drug in hepatotoxic_drugs)
        
        if hepatotoxic_count > 1:
            feasibility_score *= 0.5
            dosing_conflicts.append('Multiple hepatotoxic agents')
        
        return {
            'feasibility_score': feasibility_score,
            'conflicts': dosing_conflicts,
            'recommendation': 'Feasible' if feasibility_score > 0.7 else 
                           'Caution needed' if feasibility_score > 0.4 else 'Not recommended'
        }
    
    def _calculate_treatment_score(self, response_prob: float, pfs: float, os: float, 
                                 toxicity: float, confidence: float) -> float:
        """计算治疗综合评分"""
        
        # 权重
        weights = {
            'efficacy': 0.4,      # 疗效权重
            'survival': 0.3,      # 生存权重  
            'safety': 0.2,        # 安全性权重
            'confidence': 0.1     # 置信度权重
        }
        
        # 标准化评分 (0-1)
        efficacy_score = response_prob  # 已经是0-1
        survival_score = min((pfs + os/2) / 20, 1)  # 标准化生存获益
        safety_score = 1 - toxicity  # 毒性越低，安全性越高
        
        # 综合评分
        total_score = (
            weights['efficacy'] * efficacy_score +
            weights['survival'] * survival_score +
            weights['safety'] * safety_score +
            weights['confidence'] * confidence
        )
        
        return total_score
    
    def _assess_inherent_resistance(self, patient_profile: Dict, drug_info: Dict) -> Dict:
        """评估固有耐药性"""
        
        resistance_score = 0
        resistance_factors = []
        
        # 检查耐药基因
        if 'mutations' in patient_profile:
            for resistance_gene in drug_info.get('resistance_genes', []):
                if resistance_gene in patient_profile['mutations']:
                    resistance_score += 0.3
                    resistance_factors.append(f'{resistance_gene} mutation')
        
        # 其他耐药因素
        if 'prior_treatments' in patient_profile:
            for treatment in patient_profile['prior_treatments']:
                if treatment in drug_info.get('targets', []):
                    resistance_score += 0.2
                    resistance_factors.append(f'Prior {treatment} exposure')
        
        return {
            'resistance_score': min(resistance_score, 1.0),
            'resistance_factors': resistance_factors,
            'likelihood': 'High' if resistance_score > 0.6 else 
                         'Moderate' if resistance_score > 0.3 else 'Low'
        }
    
    def _predict_acquired_resistance(self, patient_profile: Dict, drug_info: Dict) -> Dict:
        """预测获得性耐药风险"""
        
        # 基于药物类型的耐药时间模型
        resistance_timeline = {
            'Multi-kinase inhibitor': 8,  # 月
            'Immune checkpoint inhibitor': 18,
            'Monoclonal antibody': 12
        }
        
        drug_type = drug_info['type']
        median_resistance_time = resistance_timeline.get(drug_type, 10)
        
        # 患者特异性调整
        if 'tumor_burden' in patient_profile:
            if patient_profile['tumor_burden'] == 'high':
                median_resistance_time *= 0.7
        
        return {
            'median_resistance_time_months': median_resistance_time,
            'resistance_probability_6m': 1 - np.exp(-6/median_resistance_time),
            'resistance_probability_12m': 1 - np.exp(-12/median_resistance_time),
            'high_risk_factors': ['High tumor burden', 'Poor performance status']
        }
    
    def _identify_resistance_mechanisms(self, patient_profile: Dict, drug_info: Dict) -> List[str]:
        """识别潜在耐药机制"""
        
        mechanisms = []
        
        # 基于药物类型的常见耐药机制
        if 'Multi-kinase inhibitor' in drug_info['type']:
            mechanisms.extend([
                'Alternative kinase activation',
                'Efflux pump upregulation',
                'Angiogenesis pathway rewiring'
            ])
        
        if 'Immune checkpoint inhibitor' in drug_info['type']:
            mechanisms.extend([
                'T-cell exhaustion',
                'Immunosuppressive microenvironment',
                'Antigen presentation defects'
            ])
        
        # 基于患者突变状态
        if 'mutations' in patient_profile:
            patient_mutations = patient_profile['mutations']
            if 'TP53' in patient_mutations:
                mechanisms.append('p53 pathway disruption')
            if 'CTNNB1' in patient_mutations:
                mechanisms.append('Wnt pathway activation')
        
        return mechanisms
    
    def _assess_resistance_delay(self, patient_profile: Dict, combo: Tuple[str]) -> Dict:
        """评估组合对耐药性的延缓效果"""
        
        # 单药耐药时间
        single_drug_resistance_times = []
        for drug in combo:
            if drug in self.approved_drugs:
                drug_info = self.approved_drugs[drug]
                resistance_data = self._predict_acquired_resistance(patient_profile, drug_info)
                single_drug_resistance_times.append(resistance_data['median_resistance_time_months'])
        
        if not single_drug_resistance_times:
            return {'delay_factor': 1.0, 'mechanism': 'Unknown'}
        
        # 组合延缓因子
        if len(set([self.approved_drugs[drug]['type'] for drug in combo if drug in self.approved_drugs])) > 1:
            # 不同机制的组合
            delay_factor = 1.5 + np.random.uniform(0, 0.5)
            mechanism = 'Complementary mechanisms'
        else:
            # 相同机制的组合
            delay_factor = 1.1 + np.random.uniform(0, 0.2)
            mechanism = 'Additive effects'
        
        combined_resistance_time = max(single_drug_resistance_times) * delay_factor
        
        return {
            'delay_factor': delay_factor,
            'mechanism': mechanism,
            'single_drug_median': max(single_drug_resistance_times),
            'combination_median': combined_resistance_time,
            'benefit_months': combined_resistance_time - max(single_drug_resistance_times)
        }
    
    def _generate_treatment_rationale(self, treatment_name: str, treatment_data: Dict,
                                    synergy_results: Dict, resistance_results: Dict) -> str:
        """生成治疗推荐理由"""
        
        rationale_parts = []
        
        # 疗效理由
        if treatment_data['type'] == 'monotherapy':
            response_rate = treatment_data['details']['response_probability']
            if response_rate > 0.3:
                rationale_parts.append(f"高预期响应率 ({response_rate:.1%})")
        else:
            response_rate = treatment_data['details']['predicted_response_rate']
            if response_rate > 0.4:
                rationale_parts.append(f"协同效应增强响应率 ({response_rate:.1%})")
        
        # 安全性理由
        if treatment_data['type'] == 'monotherapy':
            if treatment_data['details']['side_effects']['manageable']:
                rationale_parts.append("可管理的副作用谱")
        else:
            if treatment_data['details']['toxicity_score'] < 0.6:
                rationale_parts.append("可接受的组合毒性")
        
        # 生物标志物匹配
        if treatment_data['type'] == 'monotherapy':
            biomarker_match = treatment_data['details']['biomarker_match']
            if biomarker_match['match_percentage'] > 0.5:
                rationale_parts.append(f"生物标志物高度匹配 ({biomarker_match['match_percentage']:.1%})")
        
        # 耐药性考虑
        if '+' in treatment_name:  # 组合治疗
            # 检查耐药延缓效果
            if treatment_name in resistance_results.get('combination_resistance_delay', {}):
                delay_data = resistance_results['combination_resistance_delay'][treatment_name]
                if delay_data['delay_factor'] > 1.3:
                    rationale_parts.append(f"显著延缓耐药性 ({delay_data['delay_factor']:.1f}x)")
        
        return "; ".join(rationale_parts) if rationale_parts else "基于综合评估推荐"
    
    def _generate_dosing_schedule(self, treatment: str, patient_profile: Dict) -> Dict:
        """生成给药方案"""
        
        # 标准给药方案
        standard_dosing = {
            'Sorafenib': {'dose': '400mg', 'frequency': 'BID', 'route': 'PO'},
            'Lenvatinib': {'dose': '12mg', 'frequency': 'QD', 'route': 'PO'},
            'Regorafenib': {'dose': '160mg', 'frequency': 'QD', 'route': 'PO'},
            'Cabozantinib': {'dose': '60mg', 'frequency': 'QD', 'route': 'PO'},
            'Atezolizumab': {'dose': '1200mg', 'frequency': 'Q3W', 'route': 'IV'},
            'Nivolumab': {'dose': '240mg', 'frequency': 'Q2W', 'route': 'IV'},
            'Pembrolizumab': {'dose': '200mg', 'frequency': 'Q3W', 'route': 'IV'},
            'Bevacizumab': {'dose': '15mg/kg', 'frequency': 'Q3W', 'route': 'IV'}
        }
        
        if '+' in treatment:  # 组合治疗
            drugs = treatment.split(' + ')
            schedule = {}
            for drug in drugs:
                if drug in standard_dosing:
                    schedule[drug] = standard_dosing[drug].copy()
                    # 组合治疗可能需要剂量调整
                    if 'mg' in schedule[drug]['dose']:
                        dose_str = schedule[drug]['dose']
                        try:
                            if 'mg/kg' in dose_str:
                                # 处理mg/kg格式
                                current_dose = float(dose_str.replace('mg/kg', ''))
                                adjusted_dose = current_dose * 0.8  # 80%剂量
                                schedule[drug]['dose'] = f'{adjusted_dose}mg/kg'
                            elif 'mg' in dose_str:
                                # 处理固定mg格式
                                current_dose = int(dose_str.replace('mg', ''))
                                adjusted_dose = int(current_dose * 0.8)  # 80%剂量
                                schedule[drug]['dose'] = f'{adjusted_dose}mg'
                        except ValueError:
                            # 如果解析失败，保持原剂量
                            pass
            return schedule
        else:
            return {treatment: standard_dosing.get(treatment, {'dose': 'TBD', 'frequency': 'TBD', 'route': 'TBD'})}
    
    def _generate_monitoring_plan(self, treatment: str, patient_profile: Dict) -> Dict:
        """生成监测计划"""
        
        monitoring = {
            'baseline_assessments': [],
            'routine_monitoring': [],
            'safety_monitoring': [],
            'efficacy_monitoring': []
        }
        
        # 基线评估
        monitoring['baseline_assessments'] = [
            'Complete blood count',
            'Comprehensive metabolic panel',
            'Liver function tests',
            'Thyroid function tests',
            'ECOG performance status',
            'CT/MRI imaging'
        ]
        
        # 常规监测
        monitoring['routine_monitoring'] = [
            'CBC every 2 weeks for first 2 months',
            'LFTs every 2 weeks',
            'Electrolytes weekly'
        ]
        
        # 药物特异性监测
        if any(drug in treatment for drug in ['Sorafenib', 'Lenvatinib', 'Regorafenib', 'Cabozantinib']):
            monitoring['safety_monitoring'].extend([
                'Blood pressure monitoring',
                'Hand-foot syndrome assessment',
                'Diarrhea management'
            ])
        
        if any(drug in treatment for drug in ['Atezolizumab', 'Nivolumab', 'Pembrolizumab']):
            monitoring['safety_monitoring'].extend([
                'Thyroid function Q6W',
                'Pneumonitis screening',
                'Hepatitis monitoring'
            ])
        
        # 疗效监测
        monitoring['efficacy_monitoring'] = [
            'CT/MRI every 8-12 weeks',
            'AFP every 4 weeks',
            'Clinical assessment every 2 weeks'
        ]
        
        return monitoring


def run_drug_combination_demo():
    """运行药物组合预测演示"""
    
    predictor = DrugCombinationPredictor()
    
    # 创建示例患者档案
    patient_profile = {
        'patient_id': 'LIHC_001',
        'age': 65,
        'gender': 'M',
        'stage': 'III',
        'performance_status': 1,
        'tumor_burden': 'moderate',
        'biomarkers': {
            'VEGF': 0.8,
            'PD-L1': 0.3,
            'AFP': 150,
            'TMB': 'low'
        },
        'mutations': ['TP53', 'CTNNB1'],
        'prior_treatments': []
    }
    
    print("Running drug combination prediction...")
    
    # 运行预测
    prediction_results = predictor.predict_drug_combinations(patient_profile)
    
    # 输出结果摘要
    print("\n=== 药物组合预测结果摘要 ===")
    print(f"患者ID: {prediction_results['patient_id']}")
    
    print("\n一线治疗推荐:")
    for i, treatment in enumerate(prediction_results['optimal_combinations']['first_line'], 1):
        ranking = prediction_results['optimal_combinations']['personalized_ranking'][treatment]
        rationale = prediction_results['optimal_combinations']['treatment_rationale'].get(treatment, '')
        print(f"{i}. {treatment} (评分: {ranking['score']:.3f})")
        print(f"   理由: {rationale}")
    
    print("\n单药预测结果:")
    for drug, results in prediction_results['single_drug_predictions'].items():
        print(f"- {drug}: 响应率 {results['response_probability']:.2%}, "
              f"PFS {results['predicted_pfs']:.1f}月, "
              f"治疗指数 {results['therapeutic_index']:.2f}")
    
    print("\n协同效应分析:")
    synergistic_pairs = prediction_results['synergy_analysis']['synergistic_pairs']
    if synergistic_pairs:
        print("协同组合:")
        for pair in synergistic_pairs[:3]:
            score = prediction_results['synergy_analysis']['synergy_matrix'][pair]
            print(f"- {pair}: 协同评分 {score:.3f}")
    
    print("\n治疗计划:")
    schedule = prediction_results['treatment_schedule']
    for step in schedule['treatment_sequence']:
        print(f"- {step['line']}: {step['treatment']} ({step['expected_duration']})")
    
    return prediction_results


if __name__ == "__main__":
    results = run_drug_combination_demo()