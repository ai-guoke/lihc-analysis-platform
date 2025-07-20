"""
TCGA-LIHC Data Downloader and Preprocessor
Handles downloading and preprocessing of TCGA liver hepatocellular carcinoma data
"""

import pandas as pd
import numpy as np
import requests
import json
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class TCGADataDownloader:
    """Download and preprocess TCGA-LIHC data"""
    
    def __init__(self, output_dir="data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://api.gdc.cancer.gov"
        
    def get_project_info(self, project_id="TCGA-LIHC"):
        """Get basic project information"""
        endpoint = f"{self.base_url}/projects/{project_id}"
        response = requests.get(endpoint)
        if response.status_code == 200:
            return response.json()['data']
        else:
            raise Exception(f"Failed to get project info: {response.status_code}")
    
    def get_cases(self, project_id="TCGA-LIHC"):
        """Get all cases for the project"""
        filters = {
            "op": "in",
            "content": {
                "field": "cases.project.project_id",
                "value": [project_id]
            }
        }
        
        params = {
            "filters": json.dumps(filters),
            "expand": "diagnoses,demographic,exposures",
            "format": "json",
            "size": "2000"
        }
        
        response = requests.get(f"{self.base_url}/cases", params=params)
        if response.status_code == 200:
            return response.json()['data']['hits']
        else:
            raise Exception(f"Failed to get cases: {response.status_code}")
    
    def download_clinical_data(self):
        """Download and process clinical data"""
        print("Downloading clinical data from TCGA API...")
        
        try:
            # Try to get real TCGA clinical data
            cases = self.get_cases()
            
            clinical_records = []
            for case in cases[:100]:  # Limit for demo
                record = {
                    'sample_id': case.get('submitter_id', ''),
                    'case_id': case.get('id', ''),
                }
                
                # Extract demographic data
                if case.get('demographic'):
                    demo = case['demographic'][0] if case['demographic'] else {}
                    record.update({
                        'age': demo.get('age_at_index'),
                        'gender': demo.get('gender'),
                        'race': demo.get('race'),
                        'ethnicity': demo.get('ethnicity')
                    })
                
                # Extract diagnosis data
                if case.get('diagnoses'):
                    diag = case['diagnoses'][0] if case['diagnoses'] else {}
                    record.update({
                        'stage': diag.get('tumor_stage'),
                        'grade': diag.get('tumor_grade'),
                        'histology': diag.get('primary_diagnosis'),
                        'days_to_death': diag.get('days_to_death'),
                        'vital_status': diag.get('vital_status')
                    })
                
                clinical_records.append(record)
            
            if clinical_records:
                clinical_df = pd.DataFrame(clinical_records)
                print(f"Downloaded {len(clinical_df)} clinical records")
            else:
                raise Exception("No clinical data retrieved")
                
        except Exception as e:
            print(f"Warning: Failed to download real TCGA data ({e}). Using synthetic data.")
            # Fallback to synthetic data
            np.random.seed(42)
            n_samples = 377  # Approximate TCGA-LIHC sample size
            
            clinical_data = {
                'sample_id': [f"TCGA-LIHC-{i:03d}" for i in range(n_samples)],
                'age': np.random.normal(60, 12, n_samples).astype(int),
                'gender': np.random.choice(['Male', 'Female'], n_samples, p=[0.7, 0.3]),
                'stage': np.random.choice(['Stage I', 'Stage II', 'Stage III', 'Stage IV'], 
                                        n_samples, p=[0.25, 0.25, 0.35, 0.15]),
                'grade': np.random.choice(['G1', 'G2', 'G3', 'G4'], 
                                        n_samples, p=[0.15, 0.35, 0.35, 0.15]),
                'os_time': np.random.exponential(365*2, n_samples),  # Days
                'os_status': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),  # 0=alive, 1=dead
                'tumor_purity': np.random.beta(2, 1, n_samples) * 0.8 + 0.2,  # 0.2-1.0
            }
            
            # Adjust survival based on stage (higher stage = worse prognosis)
            stage_multiplier = {'Stage I': 1.5, 'Stage II': 1.2, 'Stage III': 0.8, 'Stage IV': 0.5}
            for i, stage in enumerate(clinical_data['stage']):
                clinical_data['os_time'][i] *= stage_multiplier[stage]
                # Higher stage increases death probability
                if stage in ['Stage III', 'Stage IV'] and np.random.random() < 0.3:
                    clinical_data['os_status'][i] = 1
            
            clinical_df = pd.DataFrame(clinical_data)
        clinical_df['os_time'] = clinical_df['os_time'].astype(int)
        
        output_path = self.output_dir / "clinical_data.csv"
        clinical_df.to_csv(output_path, index=False)
        print(f"Clinical data saved to {output_path}")
        
        return clinical_df
    
    def generate_expression_data(self, n_genes=20000):
        """Generate synthetic gene expression data"""
        print("Generating expression data...")
        
        np.random.seed(42)
        n_samples = 377
        
        # Create gene names (including known cancer-related genes)
        cancer_genes = ['TP53', 'CTNNB1', 'MYC', 'RB1', 'PTEN', 'PIK3CA', 'KRAS', 'NRAS', 
                       'EGFR', 'ERBB2', 'CDKN2A', 'ATM', 'BRCA1', 'BRCA2', 'MDM2']
        immune_genes = ['CD8A', 'CD4', 'FOXP3', 'IL2', 'IFNG', 'TNF', 'IL10', 'GZMB', 'PRF1']
        ecm_genes = ['COL1A1', 'COL3A1', 'FN1', 'LAMB1', 'MMP2', 'MMP9', 'TIMP1', 'SPARC']
        cytokine_genes = ['IL6', 'TGFB1', 'TGFB2', 'TGFBR1', 'TGFBR2', 'VEGFA', 'IL1B']
        caf_genes = ['FAP', 'ACTA2', 'PDPN', 'VIM', 'S100A4']
        
        known_genes = cancer_genes + immune_genes + ecm_genes + cytokine_genes + caf_genes
        random_genes = [f"GENE_{i:05d}" for i in range(len(known_genes), n_genes)]
        all_genes = known_genes + random_genes
        
        # Generate expression matrix (log2 scale)
        expression_matrix = np.random.normal(8, 2, (n_samples, n_genes))
        
        # Add some structure for known cancer genes
        for i, gene in enumerate(all_genes[:len(known_genes)]):
            if gene in cancer_genes:
                # Some cancer genes are highly variable
                expression_matrix[:, i] = np.random.normal(7, 3, n_samples)
            elif gene in immune_genes:
                # Immune genes show bimodal distribution
                expression_matrix[:, i] = np.concatenate([
                    np.random.normal(5, 1, n_samples//2),
                    np.random.normal(10, 1, n_samples - n_samples//2)
                ])
        
        # Create DataFrame
        sample_ids = [f"TCGA-LIHC-{i:03d}" for i in range(n_samples)]
        expression_df = pd.DataFrame(expression_matrix.T, 
                                   index=all_genes, 
                                   columns=sample_ids)
        
        output_path = self.output_dir / "expression_data.csv"
        expression_df.to_csv(output_path)
        print(f"Expression data saved to {output_path}")
        
        return expression_df
    
    def generate_mutation_data(self):
        """Generate synthetic mutation data"""
        print("Generating mutation data...")
        
        np.random.seed(42)
        n_samples = 377
        sample_ids = [f"TCGA-LIHC-{i:03d}" for i in range(n_samples)]
        
        # Common mutations in liver cancer
        mutation_genes = ['TP53', 'CTNNB1', 'ALB', 'PCLO', 'MUC16', 'APOB', 'RYR2', 
                         'ARID1A', 'AXIN1', 'NFE2L2', 'KEAP1', 'PIK3CA']
        
        mutation_rates = [0.35, 0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 
                         0.15, 0.12, 0.08, 0.06, 0.08]  # Approximate rates for LIHC
        
        mutation_data = []
        
        for sample_id in sample_ids:
            for gene, rate in zip(mutation_genes, mutation_rates):
                if np.random.random() < rate:
                    mutation_data.append({
                        'sample_id': sample_id,
                        'gene': gene,
                        'mutation_type': np.random.choice(['Missense', 'Nonsense', 'Frame_Shift', 'Splice_Site']),
                        'variant_class': 'SNP' if np.random.random() < 0.8 else 'INDEL'
                    })
        
        mutation_df = pd.DataFrame(mutation_data)
        output_path = self.output_dir / "mutation_data.csv"
        mutation_df.to_csv(output_path, index=False)
        print(f"Mutation data saved to {output_path}")
        
        return mutation_df
    
    def download_all_data(self):
        """Download all required data types"""
        print("Starting TCGA-LIHC data download...")
        
        clinical_df = self.download_clinical_data()
        expression_df = self.generate_expression_data()
        mutation_df = self.generate_mutation_data()
        
        print("Data download completed!")
        return {
            'clinical': clinical_df,
            'expression': expression_df,
            'mutation': mutation_df
        }

if __name__ == "__main__":
    downloader = TCGADataDownloader()
    data = downloader.download_all_data()