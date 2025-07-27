"""
Generate realistic demo data with real gene names for CAFs analysis
生成包含真实基因名的逼真示例数据，支持CAFs分析
"""

import pandas as pd
import numpy as np
import os
from typing import List, Dict

class RealisticDemoDataGenerator:
    """Generate realistic demo data with real gene symbols"""
    
    def __init__(self, n_samples=200, n_genes=5000):
        self.n_samples = n_samples
        self.n_genes = n_genes
        self.sample_names = [f"Patient_{i:03d}" for i in range(n_samples)]
        
        # Define essential gene sets for different analyses
        self.gene_sets = self._define_gene_sets()
        
    def _define_gene_sets(self) -> Dict[str, List[str]]:
        """Define gene sets for different analyses"""
        return {
            # CAFs markers (from cafs_analyzer.py)
            'icafs_markers': [
                'IL6', 'IL8', 'CXCL8', 'IL1B', 'TNF',
                'CCL2', 'CCL5', 'CCL20', 'CXCL1', 'CXCL2', 'CXCL12',
                'PDGFRA', 'PDGFRB', 'FGFR1', 'EGFR',
                'NFKB1', 'RELA', 'STAT3', 'IRF1', 'IRF3',
                'C3', 'CFB', 'C1S', 'C1R',
                'PTGS2', 'NOS2', 'TNFAIP3', 'SOCS3'
            ],
            'mycafs_markers': [
                'ACTA2', 'ACTG2', 'MYH11', 'MYL9',
                'TAGLN', 'TAGLN2', 'CNN1', 'CALD1',
                'MYL6', 'MYL12A', 'MYL12B', 'MYLK',
                'COL1A1', 'COL1A2', 'COL3A1', 'COL5A1', 'COL6A1',
                'MMP2', 'MMP11', 'MMP14', 'TIMP1', 'TIMP2',
                'LOX', 'LOXL1', 'LOXL2', 'LOXL4',
                'TPM1', 'TPM2', 'MYLPF', 'ACTBP2'
            ],
            'apcafs_markers': [
                'HLA-DRA', 'HLA-DRB1', 'HLA-DQA1', 'HLA-DQB1',
                'HLA-DPA1', 'HLA-DPB1',
                'CD74', 'CTSS', 'CTSL', 'CTSD',
                'CD80', 'CD86', 'CD40', 'ICOS',
                'IL12A', 'IL12B', 'IL15', 'IL18',
                'CCL19', 'CCL21', 'CXCL9', 'CXCL10',
                'SLPI', 'C3', 'CFI', 'SERPING1',
                'IDO1', 'TNFSF4', 'TNFRSF14', 'ICOSLG'
            ],
            # TAMs markers (from tams_analyzer.py)
            'm1_markers': [
                'CD80', 'CD86', 'CD68', 'CD64', 'CD16',
                'HLA-DRA', 'HLA-DRB1', 'NOS2', 'IL1B', 'IL6',
                'TNF', 'IL12A', 'IL12B', 'IL23A', 'CXCL9',
                'CXCL10', 'CXCL11', 'CCL5', 'IRF1', 'IRF5',
                'STAT1', 'SOCS3', 'CD40', 'FCGR1A', 'FCGR3A'
            ],
            'm2_markers': [
                'CD163', 'MRC1', 'MSR1', 'CD200R1', 'CSF1R',
                'IL10', 'TGFB1', 'ARG1', 'CCL17', 'CCL18',
                'CCL22', 'CCL24', 'VEGFA', 'EGF', 'MMP9',
                'MMP12', 'PPARG', 'IRF4', 'MAF', 'KLF4',
                'STAB1', 'MARCO', 'CD276', 'VSIG4', 'MS4A4A'
            ],
            # Tregs markers (from tregs_analyzer.py)
            'tregs_markers': [
                'FOXP3', 'IL2RA', 'CTLA4', 'CD4', 'IKZF2',
                'IL10', 'TGFB1', 'TGFB2', 'IL35', 'EBI3',
                'IL12A', 'TNFRSF18', 'LAG3', 'TIGIT', 'ICOS',
                'CCR4', 'CCR8', 'PDCD1', 'HAVCR2', 'IDO1',
                'ENTPD1', 'NT5E', 'ITGAE', 'LRRC32', 'FCRL3'
            ],
            # CD8+ T cell markers (from cd8t_analyzer.py)
            'cd8t_exhaustion': [
                'PDCD1', 'CTLA4', 'HAVCR2', 'LAG3', 'TIGIT',
                'BTLA', 'CD160', 'CD244', 'VISTA', 'TIM3'
            ],
            'cd8t_cytotoxic': [
                'GZMA', 'GZMB', 'GZMH', 'GZMK', 'PRF1',
                'GNLY', 'NKG7', 'KLRK1', 'KLRD1', 'FCGR3A'
            ],
            # Common cancer-related genes
            'oncogenes': [
                'MYC', 'KRAS', 'EGFR', 'HER2', 'BRAF',
                'PIK3CA', 'AKT1', 'MTOR', 'CCND1', 'CDK4'
            ],
            'tumor_suppressors': [
                'TP53', 'RB1', 'PTEN', 'CDKN2A', 'VHL',
                'APC', 'BRCA1', 'BRCA2', 'MLH1', 'MSH2'
            ],
            # Housekeeping genes
            'housekeeping': [
                'GAPDH', 'ACTB', 'B2M', 'HPRT1', 'RPL13A',
                'YWHAZ', 'UBC', 'GUSB', 'TBP', 'PPIA'
            ],
            # Additional immune genes
            'other_immune': [
                'CD3D', 'CD3E', 'CD8A', 'CD8B', 'CD4',
                'CD19', 'CD20', 'CD56', 'NCAM1', 'CD14',
                'CD15', 'CD33', 'CD34', 'CD38', 'CD45'
            ],
            # Stromal function genes
            'collagen_synthesis': [
                'COL1A1', 'COL1A2', 'COL3A1', 'COL4A1', 'COL5A1',
                'COL6A1', 'COL6A2', 'COL8A1', 'COL12A1', 'COL14A1'
            ],
            'matrix_remodeling': [
                'MMP1', 'MMP2', 'MMP3', 'MMP9', 'MMP11', 'MMP14',
                'TIMP1', 'TIMP2', 'TIMP3', 'TIMP4',
                'PLOD1', 'PLOD2', 'PLOD3', 'P4HA1', 'P4HA2'
            ],
            'angiogenesis': [
                'VEGFA', 'VEGFB', 'VEGFC', 'ANGPT1', 'ANGPT2',
                'PDGFA', 'PDGFB', 'FGF2', 'HGF', 'EGF'
            ]
        }
    
    def _get_all_essential_genes(self) -> List[str]:
        """Get all essential genes from gene sets"""
        all_genes = []
        for gene_list in self.gene_sets.values():
            all_genes.extend(gene_list)
        # Remove duplicates while preserving order
        seen = set()
        unique_genes = []
        for gene in all_genes:
            if gene not in seen:
                seen.add(gene)
                unique_genes.append(gene)
        return unique_genes
    
    def _generate_random_genes(self, n_random: int) -> List[str]:
        """Generate random gene names to fill up to n_genes"""
        # Common gene name patterns
        prefixes = ['ATP', 'SLC', 'KIAA', 'FAM', 'DNAH', 'PCDH', 'ZNF', 
                   'KCNQ', 'CACNA', 'GPR', 'OR', 'OLFR', 'TAS', 'HTR',
                   'GABR', 'GRIN', 'DLG', 'SYNE', 'ANK', 'PLEC']
        
        random_genes = []
        for i in range(n_random):
            if i < len(prefixes) * 10:
                prefix = prefixes[i % len(prefixes)]
                suffix = f"{(i // len(prefixes)) + 1}"
                gene = f"{prefix}{suffix}"
            else:
                # Generate more unique names
                gene = f"LOC{100000 + i}"
            random_genes.append(gene)
        
        return random_genes
    
    def generate_expression_data(self) -> pd.DataFrame:
        """Generate realistic gene expression data"""
        # Get essential genes
        essential_genes = self._get_all_essential_genes()
        n_essential = len(essential_genes)
        
        # Generate random genes to fill up to n_genes
        n_random = max(0, self.n_genes - n_essential)
        random_genes = self._generate_random_genes(n_random)
        
        # Combine all genes
        all_genes = essential_genes + random_genes[:n_random]
        
        # Initialize expression matrix
        expression_data = pd.DataFrame(
            index=all_genes,
            columns=self.sample_names
        )
        
        # Generate expression values with realistic patterns
        np.random.seed(42)  # For reproducibility
        
        # 1. Housekeeping genes - high expression, low variance
        for gene in self.gene_sets['housekeeping']:
            if gene in all_genes:
                base_expr = np.random.uniform(10, 12)
                expression_data.loc[gene] = np.random.normal(base_expr, 0.5, self.n_samples)
        
        # 2. CAFs markers - variable expression to create different subtypes
        # Create sample groups with different CAFs profiles
        n_icafs = self.n_samples // 3
        n_mycafs = self.n_samples // 3
        n_apcafs = self.n_samples - n_icafs - n_mycafs
        
        sample_groups = {
            'icafs': self.sample_names[:n_icafs],
            'mycafs': self.sample_names[n_icafs:n_icafs+n_mycafs],
            'apcafs': self.sample_names[n_icafs+n_mycafs:]
        }
        
        # iCAFs markers - high in iCAFs group
        for gene in self.gene_sets['icafs_markers']:
            if gene in all_genes:
                expr_values = np.random.normal(6, 1, self.n_samples)
                # Increase expression in iCAFs samples
                for sample in sample_groups['icafs']:
                    idx = self.sample_names.index(sample)
                    expr_values[idx] = np.random.normal(10, 1)
                expression_data.loc[gene] = expr_values
        
        # myCAFs markers - high in myCAFs group
        for gene in self.gene_sets['mycafs_markers']:
            if gene in all_genes:
                expr_values = np.random.normal(6, 1, self.n_samples)
                # Increase expression in myCAFs samples
                for sample in sample_groups['mycafs']:
                    idx = self.sample_names.index(sample)
                    expr_values[idx] = np.random.normal(10, 1)
                expression_data.loc[gene] = expr_values
        
        # apCAFs markers - high in apCAFs group
        for gene in self.gene_sets['apcafs_markers']:
            if gene in all_genes:
                expr_values = np.random.normal(6, 1, self.n_samples)
                # Increase expression in apCAFs samples
                for sample in sample_groups['apcafs']:
                    idx = self.sample_names.index(sample)
                    expr_values[idx] = np.random.normal(10, 1)
                expression_data.loc[gene] = expr_values
        
        # 3. TAMs markers - create M1/M2 polarization patterns
        m1_samples = self.sample_names[::2]  # Every other sample
        m2_samples = self.sample_names[1::2]
        
        for gene in self.gene_sets['m1_markers']:
            if gene in all_genes and pd.isna(expression_data.loc[gene].iloc[0]):
                expr_values = np.random.normal(5, 1, self.n_samples)
                for sample in m1_samples:
                    idx = self.sample_names.index(sample)
                    expr_values[idx] = np.random.normal(9, 1)
                expression_data.loc[gene] = expr_values
        
        for gene in self.gene_sets['m2_markers']:
            if gene in all_genes and pd.isna(expression_data.loc[gene].iloc[0]):
                expr_values = np.random.normal(5, 1, self.n_samples)
                for sample in m2_samples:
                    idx = self.sample_names.index(sample)
                    expr_values[idx] = np.random.normal(9, 1)
                expression_data.loc[gene] = expr_values
        
        # 4. Fill remaining genes with random expression
        for gene in all_genes:
            if pd.isna(expression_data.loc[gene].iloc[0]):
                # Random expression with log-normal distribution
                mean_expr = np.random.uniform(2, 8)
                std_expr = np.random.uniform(0.5, 2)
                expression_data.loc[gene] = np.random.normal(mean_expr, std_expr, self.n_samples)
        
        # Ensure all values are positive (gene expression can't be negative)
        expression_data = expression_data.clip(lower=0)
        
        # Add some zeros for dropout effect (common in RNA-seq)
        dropout_mask = np.random.random(expression_data.shape) < 0.05
        expression_data[dropout_mask] = 0
        
        return expression_data
    
    def generate_clinical_data(self) -> pd.DataFrame:
        """Generate realistic clinical data"""
        np.random.seed(42)
        
        clinical_data = pd.DataFrame(index=self.sample_names)
        
        # Age - normal distribution around 60
        clinical_data['age'] = np.random.normal(60, 12, self.n_samples).clip(30, 85).astype(int)
        
        # Gender - roughly 60% male for liver cancer
        clinical_data['gender'] = np.random.choice(['M', 'F'], self.n_samples, p=[0.6, 0.4])
        
        # Stage - realistic distribution
        clinical_data['stage'] = np.random.choice(
            ['I', 'II', 'III', 'IV'], 
            self.n_samples, 
            p=[0.2, 0.3, 0.35, 0.15]
        )
        
        # Overall survival time (days) - stage-dependent
        os_time = []
        os_status = []
        for stage in clinical_data['stage']:
            if stage == 'I':
                time = np.random.exponential(1500) + 365
            elif stage == 'II':
                time = np.random.exponential(1200) + 200
            elif stage == 'III':
                time = np.random.exponential(800) + 100
            else:  # Stage IV
                time = np.random.exponential(400) + 50
            
            # Censoring (30% of patients)
            if np.random.random() < 0.3:
                time = min(time, np.random.uniform(100, 1000))
                status = 0
            else:
                status = 1
            
            os_time.append(time)
            os_status.append(status)
        
        clinical_data['os_time'] = os_time
        clinical_data['os_status'] = os_status
        
        # Risk score - correlated with stage and survival
        risk_scores = []
        for i, stage in enumerate(clinical_data['stage']):
            base_risk = {'I': -0.5, 'II': 0, 'III': 0.5, 'IV': 1.0}[stage]
            # Add noise
            risk = base_risk + np.random.normal(0, 0.3)
            # Adjust based on survival
            if os_status[i] == 1 and os_time[i] < 500:
                risk += 0.5
            elif os_status[i] == 0 or os_time[i] > 1500:
                risk -= 0.3
            risk_scores.append(risk)
        
        clinical_data['risk_score'] = risk_scores
        
        # Additional clinical features
        clinical_data['tumor_size'] = np.random.gamma(2, 2, self.n_samples).clip(1, 15)
        clinical_data['afp'] = np.random.lognormal(3, 2, self.n_samples).clip(1, 10000)
        clinical_data['alt'] = np.random.gamma(2, 20, self.n_samples).clip(10, 200)
        clinical_data['ast'] = np.random.gamma(2, 25, self.n_samples).clip(15, 250)
        
        # Viral status
        clinical_data['hbv'] = np.random.choice([0, 1], self.n_samples, p=[0.3, 0.7])
        clinical_data['hcv'] = np.random.choice([0, 1], self.n_samples, p=[0.8, 0.2])
        
        # Treatment info
        clinical_data['surgery'] = np.random.choice([0, 1], self.n_samples, p=[0.4, 0.6])
        clinical_data['chemotherapy'] = np.random.choice([0, 1], self.n_samples, p=[0.5, 0.5])
        clinical_data['targeted_therapy'] = np.random.choice([0, 1], self.n_samples, p=[0.7, 0.3])
        
        return clinical_data
    
    def save_demo_data(self, output_dir='examples/demo_data'):
        """Save generated demo data"""
        os.makedirs(output_dir, exist_ok=True)
        
        print("Generating realistic demo data...")
        
        # Generate data
        expression_data = self.generate_expression_data()
        clinical_data = self.generate_clinical_data()
        
        # Save expression data
        expression_file = os.path.join(output_dir, 'expression_realistic.csv')
        expression_data.to_csv(expression_file)
        print(f"Saved expression data: {expression_file}")
        print(f"  - Samples: {expression_data.shape[1]}")
        print(f"  - Genes: {expression_data.shape[0]}")
        print(f"  - Essential genes included: {len(self._get_all_essential_genes())}")
        
        # Save clinical data
        clinical_file = os.path.join(output_dir, 'clinical_realistic.csv')
        clinical_data.to_csv(clinical_file)
        print(f"Saved clinical data: {clinical_file}")
        print(f"  - Samples: {clinical_data.shape[0]}")
        print(f"  - Features: {clinical_data.shape[1]}")
        
        # Create a summary report
        summary = {
            'data_generation_info': {
                'date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'n_samples': self.n_samples,
                'n_genes': len(expression_data),
                'n_essential_genes': len(self._get_all_essential_genes())
            },
            'gene_sets_included': {
                name: len(genes) for name, genes in self.gene_sets.items()
            },
            'clinical_features': list(clinical_data.columns),
            'sample_groups': {
                'CAFs_subtypes': {
                    'iCAFs_dominant': self.n_samples // 3,
                    'myCAFs_dominant': self.n_samples // 3,
                    'apCAFs_dominant': self.n_samples - 2 * (self.n_samples // 3)
                },
                'TAMs_polarization': {
                    'M1_dominant': len(self.sample_names[::2]),
                    'M2_dominant': len(self.sample_names[1::2])
                }
            }
        }
        
        summary_file = os.path.join(output_dir, 'data_generation_summary.json')
        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Saved generation summary: {summary_file}")
        
        return expression_file, clinical_file


if __name__ == '__main__':
    # Generate demo data
    generator = RealisticDemoDataGenerator(n_samples=200, n_genes=5000)
    generator.save_demo_data()
    
    print("\nDemo data generation completed!")
    print("The generated files contain realistic gene expression patterns suitable for:")
    print("- CAFs subtype analysis (iCAFs, myCAFs, apCAFs)")
    print("- TAMs polarization analysis (M1/M2)")
    print("- Tregs functional analysis")
    print("- CD8+ T cell exhaustion analysis")
    print("- Stromal function analysis")
    print("- And other TME-related analyses")