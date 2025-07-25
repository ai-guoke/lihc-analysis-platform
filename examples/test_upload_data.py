#!/usr/bin/env python3
"""Create test data files for upload functionality testing"""

import pandas as pd
import numpy as np
from pathlib import Path

# Create test directory
test_dir = Path("examples/test_upload")
test_dir.mkdir(exist_ok=True)

# 1. Create clinical data
clinical_data = pd.DataFrame({
    'sample_id': [f'PATIENT_{i:03d}' for i in range(1, 51)],
    'age': np.random.randint(30, 80, 50),
    'gender': np.random.choice(['Male', 'Female'], 50),
    'stage': np.random.choice(['Stage I', 'Stage II', 'Stage III', 'Stage IV'], 50),
    'grade': np.random.choice(['G1', 'G2', 'G3'], 50),
    'os_time': np.random.randint(30, 3000, 50),  # Days
    'os_status': np.random.choice([0, 1], 50)  # 0=alive, 1=dead
})
clinical_data.to_csv(test_dir / "clinical_data.csv", index=False)
print("✅ Created clinical_data.csv")

# 2. Create expression data (genes as rows, samples as columns)
gene_names = [f'GENE_{i}' for i in range(1, 101)]
sample_names = [f'PATIENT_{i:03d}' for i in range(1, 51)]

expression_data = pd.DataFrame(
    np.random.lognormal(mean=2, sigma=1, size=(100, 50)),
    index=gene_names,
    columns=sample_names
)
expression_data.to_csv(test_dir / "expression_data.csv")
print("✅ Created expression_data.csv")

# 3. Create mutation data
mutation_records = []
for i in range(300):  # 300 mutations
    mutation_records.append({
        'sample_id': np.random.choice(sample_names),
        'gene': np.random.choice(gene_names),
        'mutation_type': np.random.choice(['Missense', 'Nonsense', 'Frame_Shift', 'Silent']),
        'variant_class': np.random.choice(['SNP', 'INDEL']),
        'protein_change': f'p.{np.random.choice(["A", "T", "G", "C"])}{np.random.randint(1, 500)}{np.random.choice(["A", "T", "G", "C"])}'
    })

mutation_data = pd.DataFrame(mutation_records)
mutation_data.to_csv(test_dir / "mutation_data.csv", index=False)
print("✅ Created mutation_data.csv")

# Create a README
readme_content = """# Test Upload Data

This directory contains test data files for testing the upload functionality:

1. **clinical_data.csv** - Clinical and survival information for 50 patients
2. **expression_data.csv** - Gene expression matrix (100 genes × 50 samples)
3. **mutation_data.csv** - Mutation data with 300 mutation records

## Usage:
1. Go to http://localhost:8050
2. Click "数据管理" (Data Management)
3. Upload these files individually or as a ZIP package
4. Follow the validation and analysis steps

## Data Format:
- Clinical: sample_id, age, gender, stage, grade, os_time, os_status
- Expression: Genes as rows, samples as columns
- Mutation: sample_id, gene, mutation_type, variant_class, protein_change
"""

with open(test_dir / "README.md", "w") as f:
    f.write(readme_content)

print("\n✅ Test data created successfully!")
print(f"📁 Location: {test_dir.absolute()}")
print("\n📋 Files created:")
for file in test_dir.glob("*.csv"):
    print(f"   - {file.name}")