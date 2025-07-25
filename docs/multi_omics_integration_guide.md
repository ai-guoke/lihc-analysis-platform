# Multi-omics Data Integration Guide

## Overview

The LIHC platform now supports comprehensive multi-omics data integration, allowing researchers to combine RNA-seq, CNV, mutation, and methylation data for more powerful analyses.

## Features

### 1. Data Loading

The `MultiOmicsIntegrator` class supports loading multiple omics data types:

```python
from src.data_processing.multi_omics_integrator import MultiOmicsIntegrator

# Initialize integrator
integrator = MultiOmicsIntegrator(data_dir="data")

# Load different omics data
integrator.load_expression_data("data/raw/expression.csv")
integrator.load_cnv_data("data/raw/cnv.csv")
integrator.load_mutation_data("data/raw/mutations.csv")
integrator.load_methylation_data("data/raw/methylation.csv")
```

### 2. Integration Methods

Three integration methods are available:

#### a) Concatenation (Simple)
```python
# Simple feature concatenation
integrated_data = integrator.integrate_omics(integration_method="concatenate")
```

#### b) Similarity Network Fusion (SNF)
```python
# Network-based integration
integrated_data = integrator.integrate_omics(integration_method="similarity_network")
```

#### c) Multi-Omics Factor Analysis (MOFA)
```python
# Factor analysis-based integration
integrated_data = integrator.integrate_omics(integration_method="mofa")
```

### 3. Feature Importance

Calculate feature importance for downstream analysis:

```python
# Calculate importance relative to a target variable
target = pd.Series(...)  # e.g., survival status
importance_scores = integrator.calculate_feature_importance(target)
```

## Data Format Requirements

### Expression Data (RNA-seq)
- Format: CSV with genes as rows, samples as columns
- Values: Raw counts or TPM/FPKM values
- Example:
```
        Sample_001  Sample_002  Sample_003
Gene_1  234.5      189.3       345.2
Gene_2  45.6       67.8        23.4
```

### CNV Data
- Format: CSV with genes as rows, samples as columns
- Values: Log2 copy number ratios
- Range: Typically -2 to +2

### Mutation Data
- Format: CSV with columns: gene_id, sample_id, mutation_type
- Example:
```
gene_id,sample_id,mutation_type
TP53,Sample_001,missense
KRAS,Sample_001,nonsense
TP53,Sample_002,frameshift
```

### Methylation Data
- Format: CSV with probes/genes as rows, samples as columns
- Values: Beta values (0-1)

## Example Workflow

```python
from src.data_processing.multi_omics_integrator import MultiOmicsIntegrator
import pandas as pd

# 1. Initialize
integrator = MultiOmicsIntegrator()

# 2. Load data
integrator.load_expression_data("expression.csv")
integrator.load_cnv_data("cnv.csv")
integrator.load_mutation_data("mutations.csv")

# 3. Integrate
integrated = integrator.integrate_omics(integration_method="concatenate")

# 4. Calculate feature importance
clinical = pd.read_csv("clinical.csv", index_col=0)
importance = integrator.calculate_feature_importance(clinical['survival_status'])

# 5. Save results
integrator.save_integrated_data("results/multi_omics")
```

## Best Practices

1. **Data Quality Control**
   - Ensure sample names are consistent across all omics types
   - Remove samples with excessive missing data
   - Log-transform expression data before integration

2. **Integration Method Selection**
   - Use `concatenate` for simple exploratory analysis
   - Use `similarity_network` when sample relationships are important
   - Use `mofa` for factor-based dimensionality reduction

3. **Performance Considerations**
   - For large datasets (>1000 samples), consider using batch processing
   - SNF and MOFA methods are computationally intensive

## Troubleshooting

### Common Issues

1. **Sample Mismatch**
   - Error: "No common samples found"
   - Solution: Ensure sample IDs match exactly across all data files

2. **Memory Issues**
   - Error: "MemoryError"
   - Solution: Reduce feature space or use batch processing

3. **Missing Data**
   - Warning: "Missing values detected"
   - Solution: Imputation is performed automatically for methylation data

## API Reference

### MultiOmicsIntegrator

#### Methods

- `load_expression_data(file_path: str) -> pd.DataFrame`
- `load_cnv_data(file_path: str) -> pd.DataFrame`
- `load_mutation_data(file_path: str) -> pd.DataFrame`
- `load_methylation_data(file_path: str) -> pd.DataFrame`
- `integrate_omics(integration_method: str = "concatenate") -> pd.DataFrame`
- `calculate_feature_importance(target: pd.Series) -> pd.DataFrame`
- `save_integrated_data(output_dir: str) -> None`

#### Attributes

- `omics_data`: Dictionary containing loaded omics data
- `integrated_features`: DataFrame with integrated features
- `feature_info`: DataFrame with feature metadata