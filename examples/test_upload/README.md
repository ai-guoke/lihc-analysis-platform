# Test Upload Data

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
