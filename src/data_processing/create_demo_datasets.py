"""
创建多个不同特征的演示数据集
用于展示LIHC平台在不同数据集上的分析能力
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import random

# 设置随机种子以确保可重现性
np.random.seed(42)
random.seed(42)

class DemoDatasetGenerator:
    """演示数据集生成器"""
    
    def __init__(self):
        self.common_genes = [
            'TP53', 'CTNNB1', 'ALB', 'AXIN1', 'ARID1A', 'CDKN2A', 'TERT', 
            'MYC', 'VEGFA', 'HGF', 'MET', 'AFP', 'GPC3', 'EGFR', 'PTEN',
            'RB1', 'KRAS', 'PIK3CA', 'MTOR', 'AKT1', 'STAT3', 'JAK2',
            'IL6', 'TNF', 'TGFB1', 'SMAD4', 'WNT1', 'NOTCH1', 'HIF1A',
            'MAPK1', 'BRAF', 'NRAS', 'FGF19', 'CCND1', 'MDM2', 'BCL2'
        ]
        
        # 免疫相关基因
        self.immune_genes = [
            'CD8A', 'CD8B', 'CD4', 'FOXP3', 'CD19', 'MS4A1', 'CD14', 'CD68',
            'CD163', 'CD80', 'CD86', 'CD274', 'PDCD1', 'CTLA4', 'LAG3', 'TIGIT',
            'HAVCR2', 'IDO1', 'ARG1', 'IL10', 'TGFB1', 'IFNG', 'GZMB', 'PRF1'
        ]
        
        # 代谢相关基因
        self.metabolic_genes = [
            'GLUT1', 'HK2', 'PKM2', 'LDHA', 'PDK1', 'G6PD', 'FASN', 'ACLY',
            'SCD1', 'CPT1A', 'ACADM', 'HMGCR', 'SREBF1', 'PPARG', 'PPARA'
        ]
        
        # 干细胞标志物
        self.stem_cell_markers = [
            'EPCAM', 'CD44', 'CD90', 'CD133', 'ALDH1A1', 'SOX2', 'NANOG', 
            'POU5F1', 'KLF4', 'MYC', 'LGR5', 'ABCG2'
        ]
        
    def generate_dataset_1_early_stage(self):
        """
        数据集1: 早期肝癌队列
        特征: 
        - 主要为Stage I/II患者
        - 较好的预后
        - 免疫活跃
        - 代谢相对正常
        """
        n_samples = 150
        n_genes = 2000
        
        # 生成患者ID
        patient_ids = [f"EARLY_{i:03d}" for i in range(1, n_samples + 1)]
        
        # 临床数据
        clinical_data = pd.DataFrame({
            'Patient_ID': patient_ids,
            'Age': np.random.normal(55, 10, n_samples).astype(int),
            'Gender': np.random.choice(['M', 'F'], n_samples, p=[0.7, 0.3]),
            'Stage': np.random.choice(['I', 'II'], n_samples, p=[0.6, 0.4]),
            'Grade': np.random.choice(['G1', 'G2'], n_samples, p=[0.7, 0.3]),
            'Tumor_Size': np.random.normal(3.5, 1.2, n_samples),
            'AFP': np.random.lognormal(2.5, 1.5, n_samples),
            'Cirrhosis': np.random.choice(['Yes', 'No'], n_samples, p=[0.4, 0.6]),
            'HBV': np.random.choice(['Positive', 'Negative'], n_samples, p=[0.5, 0.5]),
            'HCV': np.random.choice(['Positive', 'Negative'], n_samples, p=[0.2, 0.8]),
            'Alcohol': np.random.choice(['Yes', 'No'], n_samples, p=[0.3, 0.7]),
            'Survival_Days': np.random.normal(1800, 500, n_samples).clip(365, 3650),
            'Status': np.random.choice(['Alive', 'Dead'], n_samples, p=[0.8, 0.2])
        })
        
        # 基因表达数据
        # 选择基因
        selected_genes = (self.common_genes + self.immune_genes + 
                         self.metabolic_genes + self.stem_cell_markers)
        # 添加随机基因以达到2000个
        additional_genes = [f"GENE_{i:04d}" for i in range(len(selected_genes), n_genes)]
        all_genes = selected_genes + additional_genes
        
        # 生成表达矩阵
        expression_data = pd.DataFrame(
            index=patient_ids,
            columns=all_genes
        )
        
        # 早期肝癌特征：免疫基因高表达
        for gene in self.immune_genes:
            if gene in all_genes:
                expression_data[gene] = np.random.normal(8, 1.5, n_samples)
        
        # 癌基因适度表达
        for gene in self.common_genes:
            if gene in all_genes:
                expression_data[gene] = np.random.normal(6, 1.2, n_samples)
        
        # 代谢基因正常表达
        for gene in self.metabolic_genes:
            if gene in all_genes:
                expression_data[gene] = np.random.normal(7, 1, n_samples)
                
        # 其他基因随机表达
        for gene in additional_genes:
            expression_data[gene] = np.random.normal(5, 2, n_samples)
            
        # 突变数据
        mutation_data = pd.DataFrame(
            index=patient_ids,
            columns=['TP53', 'CTNNB1', 'TERT', 'ARID1A', 'AXIN1']
        )
        # 早期肝癌突变率较低
        for gene in mutation_data.columns:
            mutation_data[gene] = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
            
        return {
            'name': '早期肝癌队列',
            'description': '150例早期肝癌患者（Stage I/II），免疫活跃，预后较好',
            'clinical_data': clinical_data,
            'expression_data': expression_data,
            'mutation_data': mutation_data,
            'metadata': {
                'n_samples': n_samples,
                'n_genes': n_genes,
                'stage_distribution': {'I': 60, 'II': 40},
                'survival_rate': 80,
                'characteristics': ['高免疫浸润', '低突变负荷', '代谢正常']
            }
        }
    
    def generate_dataset_2_advanced_stage(self):
        """
        数据集2: 晚期肝癌队列
        特征:
        - 主要为Stage III/IV患者
        - 较差的预后
        - 免疫抑制
        - 代谢重编程明显
        """
        n_samples = 200
        n_genes = 2000
        
        # 生成患者ID
        patient_ids = [f"ADV_{i:03d}" for i in range(1, n_samples + 1)]
        
        # 临床数据
        clinical_data = pd.DataFrame({
            'Patient_ID': patient_ids,
            'Age': np.random.normal(62, 12, n_samples).astype(int),
            'Gender': np.random.choice(['M', 'F'], n_samples, p=[0.75, 0.25]),
            'Stage': np.random.choice(['III', 'IV'], n_samples, p=[0.45, 0.55]),
            'Grade': np.random.choice(['G3', 'G4'], n_samples, p=[0.6, 0.4]),
            'Tumor_Size': np.random.normal(8.5, 2.5, n_samples),
            'AFP': np.random.lognormal(5, 2, n_samples),
            'Cirrhosis': np.random.choice(['Yes', 'No'], n_samples, p=[0.8, 0.2]),
            'HBV': np.random.choice(['Positive', 'Negative'], n_samples, p=[0.6, 0.4]),
            'HCV': np.random.choice(['Positive', 'Negative'], n_samples, p=[0.3, 0.7]),
            'Alcohol': np.random.choice(['Yes', 'No'], n_samples, p=[0.5, 0.5]),
            'Metastasis': np.random.choice(['Yes', 'No'], n_samples, p=[0.7, 0.3]),
            'Survival_Days': np.random.normal(500, 300, n_samples).clip(30, 1500),
            'Status': np.random.choice(['Alive', 'Dead'], n_samples, p=[0.25, 0.75])
        })
        
        # 基因表达数据
        selected_genes = (self.common_genes + self.immune_genes + 
                         self.metabolic_genes + self.stem_cell_markers)
        additional_genes = [f"GENE_{i:04d}" for i in range(len(selected_genes), n_genes)]
        all_genes = selected_genes + additional_genes
        
        expression_data = pd.DataFrame(
            index=patient_ids,
            columns=all_genes
        )
        
        # 晚期肝癌特征：免疫抑制
        for gene in ['CD8A', 'CD8B', 'GZMB', 'PRF1', 'IFNG']:
            if gene in all_genes:
                expression_data[gene] = np.random.normal(4, 1.2, n_samples)  # 低表达
                
        # 免疫检查点高表达
        for gene in ['CD274', 'CTLA4', 'LAG3', 'TIGIT']:
            if gene in all_genes:
                expression_data[gene] = np.random.normal(9, 1.5, n_samples)  # 高表达
        
        # 癌基因高表达
        for gene in ['MYC', 'VEGFA', 'HGF', 'MET']:
            if gene in all_genes:
                expression_data[gene] = np.random.normal(10, 1.8, n_samples)
        
        # 代谢重编程
        for gene in ['GLUT1', 'HK2', 'PKM2', 'LDHA']:
            if gene in all_genes:
                expression_data[gene] = np.random.normal(9.5, 1.6, n_samples)
                
        # 其他基因
        for gene in additional_genes:
            expression_data[gene] = np.random.normal(5.5, 2.2, n_samples)
            
        # 突变数据 - 高突变负荷
        mutation_genes = ['TP53', 'CTNNB1', 'TERT', 'ARID1A', 'AXIN1', 
                         'CDKN2A', 'RB1', 'PTEN', 'PIK3CA', 'KRAS']
        mutation_data = pd.DataFrame(
            index=patient_ids,
            columns=mutation_genes
        )
        for gene in mutation_data.columns:
            mutation_data[gene] = np.random.choice([0, 1], n_samples, p=[0.4, 0.6])
            
        return {
            'name': '晚期肝癌队列',
            'description': '200例晚期肝癌患者（Stage III/IV），免疫抑制，预后较差',
            'clinical_data': clinical_data,
            'expression_data': expression_data,
            'mutation_data': mutation_data,
            'metadata': {
                'n_samples': n_samples,
                'n_genes': n_genes,
                'stage_distribution': {'III': 45, 'IV': 55},
                'survival_rate': 25,
                'metastasis_rate': 70,
                'characteristics': ['免疫抑制', '高突变负荷', '代谢重编程', '血管生成活跃']
            }
        }
    
    def generate_dataset_3_mixed_cohort(self):
        """
        数据集3: 混合队列（全阶段）
        特征:
        - 包含所有分期的患者
        - 中等预后
        - 异质性高
        - 适合亚型分析
        """
        n_samples = 300
        n_genes = 2000
        
        # 生成患者ID
        patient_ids = [f"MIX_{i:03d}" for i in range(1, n_samples + 1)]
        
        # 临床数据 - 混合特征
        stages = np.random.choice(['I', 'II', 'III', 'IV'], n_samples, p=[0.2, 0.3, 0.3, 0.2])
        clinical_data = pd.DataFrame({
            'Patient_ID': patient_ids,
            'Age': np.random.normal(58, 13, n_samples).astype(int),
            'Gender': np.random.choice(['M', 'F'], n_samples, p=[0.72, 0.28]),
            'Stage': stages,
            'Grade': [np.random.choice(['G1', 'G2']) if s in ['I', 'II'] else 
                     np.random.choice(['G3', 'G4']) for s in stages],
            'Tumor_Size': [np.random.normal(3, 1) if s in ['I', 'II'] else 
                          np.random.normal(7, 2) for s in stages],
            'AFP': np.random.lognormal(3.5, 2, n_samples),
            'Cirrhosis': np.random.choice(['Yes', 'No'], n_samples, p=[0.65, 0.35]),
            'HBV': np.random.choice(['Positive', 'Negative'], n_samples, p=[0.55, 0.45]),
            'HCV': np.random.choice(['Positive', 'Negative'], n_samples, p=[0.25, 0.75]),
            'Alcohol': np.random.choice(['Yes', 'No'], n_samples, p=[0.4, 0.6]),
            'NASH': np.random.choice(['Yes', 'No'], n_samples, p=[0.2, 0.8]),
            'Diabetes': np.random.choice(['Yes', 'No'], n_samples, p=[0.35, 0.65]),
            'BMI': np.random.normal(26, 4, n_samples),
            'Survival_Days': [np.random.normal(2000, 600) if s in ['I', 'II'] else 
                            np.random.normal(800, 400) for s in stages],
            'Status': [np.random.choice(['Alive', 'Dead'], p=[0.85, 0.15]) if s in ['I', 'II'] else
                      np.random.choice(['Alive', 'Dead'], p=[0.4, 0.6]) for s in stages]
        })
        
        # 基因表达数据 - 创建亚型
        selected_genes = (self.common_genes + self.immune_genes + 
                         self.metabolic_genes + self.stem_cell_markers)
        additional_genes = [f"GENE_{i:04d}" for i in range(len(selected_genes), n_genes)]
        all_genes = selected_genes + additional_genes
        
        expression_data = pd.DataFrame(
            index=patient_ids,
            columns=all_genes
        )
        
        # 定义3个分子亚型
        subtype_assignments = np.random.choice(['Immune', 'Metabolic', 'Proliferative'], 
                                             n_samples, p=[0.3, 0.35, 0.35])
        
        for i, (patient_id, subtype) in enumerate(zip(patient_ids, subtype_assignments)):
            if subtype == 'Immune':
                # 免疫亚型：高免疫浸润
                for gene in self.immune_genes:
                    if gene in all_genes:
                        expression_data.loc[patient_id, gene] = np.random.normal(8.5, 1.3)
                for gene in self.metabolic_genes:
                    if gene in all_genes:
                        expression_data.loc[patient_id, gene] = np.random.normal(6, 1.2)
                        
            elif subtype == 'Metabolic':
                # 代谢亚型：代谢重编程
                for gene in self.metabolic_genes:
                    if gene in all_genes:
                        expression_data.loc[patient_id, gene] = np.random.normal(9, 1.4)
                for gene in self.immune_genes:
                    if gene in all_genes:
                        expression_data.loc[patient_id, gene] = np.random.normal(5.5, 1.1)
                        
            else:  # Proliferative
                # 增殖亚型：细胞周期基因高表达
                for gene in ['MYC', 'CCND1', 'CDK4', 'E2F1']:
                    if gene in all_genes:
                        expression_data.loc[patient_id, gene] = np.random.normal(9.5, 1.5)
                for gene in self.stem_cell_markers:
                    if gene in all_genes:
                        expression_data.loc[patient_id, gene] = np.random.normal(8, 1.3)
            
            # 其他基因
            for gene in additional_genes:
                if pd.isna(expression_data.loc[patient_id, gene]):
                    expression_data.loc[patient_id, gene] = np.random.normal(5.5, 2)
                    
        # 补充缺失值
        expression_data = expression_data.fillna(np.random.normal(5.5, 2))
        
        # 突变数据 - 亚型特异性
        mutation_genes = ['TP53', 'CTNNB1', 'TERT', 'ARID1A', 'AXIN1', 
                         'CDKN2A', 'RB1', 'PTEN', 'PIK3CA', 'KRAS', 
                         'NFE2L2', 'KEAP1', 'ALB', 'APOB']
        mutation_data = pd.DataFrame(
            index=patient_ids,
            columns=mutation_genes
        )
        
        for i, (patient_id, subtype) in enumerate(zip(patient_ids, subtype_assignments)):
            if subtype == 'Immune':
                # 免疫亚型突变模式
                mutation_data.loc[patient_id, 'TP53'] = np.random.choice([0, 1], p=[0.6, 0.4])
                mutation_data.loc[patient_id, 'CTNNB1'] = np.random.choice([0, 1], p=[0.8, 0.2])
            elif subtype == 'Metabolic':
                # 代谢亚型突变模式
                mutation_data.loc[patient_id, 'NFE2L2'] = np.random.choice([0, 1], p=[0.5, 0.5])
                mutation_data.loc[patient_id, 'KEAP1'] = np.random.choice([0, 1], p=[0.6, 0.4])
            else:
                # 增殖亚型突变模式
                mutation_data.loc[patient_id, 'TP53'] = np.random.choice([0, 1], p=[0.3, 0.7])
                mutation_data.loc[patient_id, 'RB1'] = np.random.choice([0, 1], p=[0.5, 0.5])
                
            # 其他突变随机
            for gene in mutation_genes:
                if pd.isna(mutation_data.loc[patient_id, gene]):
                    mutation_data.loc[patient_id, gene] = np.random.choice([0, 1], p=[0.7, 0.3])
                    
        # 添加亚型信息到临床数据
        clinical_data['Molecular_Subtype'] = subtype_assignments
        
        return {
            'name': '混合队列（全阶段）',
            'description': '300例混合肝癌患者，包含所有分期，具有明显的分子亚型',
            'clinical_data': clinical_data,
            'expression_data': expression_data,
            'mutation_data': mutation_data,
            'metadata': {
                'n_samples': n_samples,
                'n_genes': n_genes,
                'stage_distribution': {'I': 20, 'II': 30, 'III': 30, 'IV': 20},
                'survival_rate': 50,
                'subtype_distribution': {'Immune': 30, 'Metabolic': 35, 'Proliferative': 35},
                'characteristics': ['高异质性', '明显分子亚型', '多病因', '适合精准医学分析']
            }
        }
    
    def save_dataset(self, dataset, dataset_id):
        """保存数据集到文件"""
        # 创建数据集目录
        base_dir = '/Users/goodgoodstudy/Desktop/aicode/mrna2/data/demo_datasets'
        dataset_dir = os.path.join(base_dir, dataset_id)
        os.makedirs(dataset_dir, exist_ok=True)
        
        # 保存临床数据
        dataset['clinical_data'].to_csv(
            os.path.join(dataset_dir, 'clinical_data.csv'), 
            index=False
        )
        
        # 保存表达数据
        dataset['expression_data'].to_csv(
            os.path.join(dataset_dir, 'expression_data.csv')
        )
        
        # 保存突变数据
        dataset['mutation_data'].to_csv(
            os.path.join(dataset_dir, 'mutation_data.csv')
        )
        
        # 保存元数据
        metadata = {
            'dataset_id': dataset_id,
            'name': dataset['name'],
            'description': dataset['description'],
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'data_types': ['clinical', 'expression', 'mutation'],
            'statistics': dataset['metadata']
        }
        
        with open(os.path.join(dataset_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
            
        print(f"数据集 '{dataset['name']}' 已保存到: {dataset_dir}")
        
    def generate_all_datasets(self):
        """生成所有演示数据集"""
        print("开始生成演示数据集...")
        
        # 数据集1：早期肝癌
        print("\n生成数据集1：早期肝癌队列...")
        dataset1 = self.generate_dataset_1_early_stage()
        self.save_dataset(dataset1, 'demo_early_stage')
        
        # 数据集2：晚期肝癌
        print("\n生成数据集2：晚期肝癌队列...")
        dataset2 = self.generate_dataset_2_advanced_stage()
        self.save_dataset(dataset2, 'demo_advanced_stage')
        
        # 数据集3：混合队列
        print("\n生成数据集3：混合队列...")
        dataset3 = self.generate_dataset_3_mixed_cohort()
        self.save_dataset(dataset3, 'demo_mixed_cohort')
        
        print("\n所有数据集生成完成！")
        
        # 生成数据集概览
        summary = {
            'datasets': [
                {
                    'id': 'demo_early_stage',
                    'name': dataset1['name'],
                    'description': dataset1['description'],
                    'n_samples': dataset1['metadata']['n_samples'],
                    'characteristics': dataset1['metadata']['characteristics']
                },
                {
                    'id': 'demo_advanced_stage',
                    'name': dataset2['name'],
                    'description': dataset2['description'],
                    'n_samples': dataset2['metadata']['n_samples'],
                    'characteristics': dataset2['metadata']['characteristics']
                },
                {
                    'id': 'demo_mixed_cohort',
                    'name': dataset3['name'],
                    'description': dataset3['description'],
                    'n_samples': dataset3['metadata']['n_samples'],
                    'characteristics': dataset3['metadata']['characteristics']
                }
            ]
        }
        
        with open(os.path.join('/Users/goodgoodstudy/Desktop/aicode/mrna2/data/demo_datasets', 
                              'datasets_summary.json'), 'w') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    generator = DemoDatasetGenerator()
    generator.generate_all_datasets()