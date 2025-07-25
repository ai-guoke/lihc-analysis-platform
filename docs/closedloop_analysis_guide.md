# ClosedLoop Causal Inference Analysis Guide

## Overview

The ClosedLoop algorithm is a comprehensive causal inference framework designed to identify cancer driver genes by integrating multiple lines of evidence. It combines statistical associations with biological knowledge to establish causal relationships.

## Key Concepts

### Evidence Types

1. **Differential Expression**: Genes showing significant expression differences between tumor and normal samples
2. **Survival Association**: Genes whose expression correlates with patient survival
3. **CNV Drivers**: Genes where copy number variations drive expression changes
4. **Methylation Regulation**: Genes regulated by DNA methylation
5. **Mutation Frequency**: Genes with recurrent mutations across samples

### Causal Score

The final causal score is a weighted combination of all evidence types, representing the likelihood that a gene is a true cancer driver.

## Usage

### Basic Analysis

```python
from src.analysis.closedloop_analyzer import ClosedLoopAnalyzer
import pandas as pd

# Initialize analyzer
analyzer = ClosedLoopAnalyzer()

# Load data
rna_data = pd.read_csv("expression.csv", index_col=0)
clinical_data = pd.read_csv("clinical.csv", index_col=0)
cnv_data = pd.read_csv("cnv.csv", index_col=0)
mutation_data = pd.read_csv("mutations.csv", index_col=0)

# Run analysis
result = analyzer.analyze_causal_relationships(
    rna_data=rna_data,
    clinical_data=clinical_data,
    cnv_data=cnv_data,
    mutation_data=mutation_data
)

# Access results
causal_genes = result.causal_genes
evidence_network = result.evidence_network
```

### Custom Configuration

```python
# Configure evidence weights
config = {
    'evidence_weights': {
        EvidenceType.DIFFERENTIAL_EXPRESSION: 0.3,
        EvidenceType.SURVIVAL_ASSOCIATION: 0.3,
        EvidenceType.CNV_DRIVER: 0.2,
        EvidenceType.METHYLATION_REGULATION: 0.1,
        EvidenceType.MUTATION_FREQUENCY: 0.1
    },
    'causal_score_threshold': 0.7,
    'p_value_threshold': 0.01
}

analyzer = ClosedLoopAnalyzer(config)
```

### Targeted Analysis

```python
# Analyze specific genes of interest
target_genes = ['TP53', 'KRAS', 'EGFR', 'MYC']

result = analyzer.analyze_causal_relationships(
    rna_data=rna_data,
    clinical_data=clinical_data,
    target_genes=target_genes
)
```

## Output Interpretation

### CausalGene Object

Each identified causal gene contains:
- `gene_id`: Gene identifier
- `causal_score`: Overall causal score (0-1)
- `evidence_scores`: Individual evidence type scores
- `confidence_level`: High/Medium/Low confidence classification
- `evidence_chain`: List of supporting evidence
- `biological_context`: Additional biological information

### Evidence Network

The evidence network shows relationships between causal genes based on:
- Shared evidence patterns
- Co-occurrence in pathways
- Functional similarities

### Validation Metrics

- **Cross-validation Score**: Consistency across data subsets
- **Bootstrap Stability**: Robustness of results
- **Literature Support**: Agreement with known cancer genes

## Algorithm Details

### 1. Evidence Collection Phase

For each evidence type, the algorithm:
1. Calculates statistical significance (p-value)
2. Measures effect size
3. Computes confidence score
4. Generates evidence score

### 2. Causal Score Calculation

```
Causal Score = Σ(Evidence Score × Weight) / Σ(Weights)
```

### 3. Network Construction

Genes are connected based on evidence similarity:
```
Similarity = 1 - |Score₁ - Score₂|
```

### 4. Pathway Analysis

Enrichment analysis identifies:
- Cancer-related pathways
- Metabolic pathways
- Immune pathways

## Example Workflow

```python
from src.analysis.closedloop_analyzer import ClosedLoopAnalyzer
import pandas as pd
import matplotlib.pyplot as plt

# 1. Initialize and configure
analyzer = ClosedLoopAnalyzer({
    'causal_score_threshold': 0.6,
    'bootstrap_iterations': 100
})

# 2. Load multi-omics data
rna = pd.read_csv("rna_seq.csv", index_col=0)
clinical = pd.read_csv("clinical.csv", index_col=0)
cnv = pd.read_csv("cnv.csv", index_col=0)
mutations = pd.read_csv("mutations.csv", index_col=0)

# 3. Run analysis
result = analyzer.analyze_causal_relationships(
    rna_data=rna,
    clinical_data=clinical,
    cnv_data=cnv,
    mutation_data=mutations
)

# 4. Filter top causal genes
top_genes = [g for g in result.causal_genes if g.causal_score > 0.8]
print(f"Found {len(top_genes)} high-confidence causal genes")

# 5. Examine top gene
if top_genes:
    top_gene = top_genes[0]
    print(f"\nTop causal gene: {top_gene.gene_id}")
    print(f"Causal score: {top_gene.causal_score:.3f}")
    print(f"Confidence: {top_gene.confidence_level}")
    print(f"Evidence types: {len(top_gene.evidence_scores)}")

# 6. Analyze pathways
pathways = result.pathway_analysis
print(f"\nPathway coverage: {pathways['pathway_coverage']:.2%}")
```

## Best Practices

1. **Data Preparation**
   - Ensure consistent sample IDs across all data types
   - Remove batch effects from expression data
   - Filter low-quality samples

2. **Parameter Tuning**
   - Start with default parameters
   - Adjust evidence weights based on data quality
   - Use cross-validation to select threshold

3. **Result Validation**
   - Check bootstrap stability (>0.8 is good)
   - Verify known cancer genes are identified
   - Compare with literature

## Troubleshooting

### Low Causal Scores
- Check data quality and preprocessing
- Ensure sufficient sample size (>50 recommended)
- Consider adjusting evidence weights

### No Significant Results
- Lower p-value threshold
- Check if survival data is informative
- Verify mutation frequencies

### Memory Issues
- Reduce number of genes analyzed
- Use targeted gene lists
- Process in batches

## Advanced Features

### Custom Evidence Types

```python
# Add custom evidence type
from src.analysis.closedloop_analyzer import EvidenceScore, EvidenceType

def analyze_protein_data(protein_data, clinical_data):
    # Custom analysis logic
    evidence_scores = {}
    # ... calculate scores ...
    return evidence_scores

# Integrate into analysis
custom_evidence = analyze_protein_data(protein_df, clinical_df)
analyzer._integrate_evidence(
    all_evidence_scores, 
    custom_evidence, 
    EvidenceType.CUSTOM
)
```

### Parallel Processing

```python
# Enable parallel processing for large datasets
analyzer = ClosedLoopAnalyzer({
    'n_jobs': 4,  # Number of parallel processes
    'chunk_size': 1000  # Genes per chunk
})
```

## References

The ClosedLoop algorithm is based on:
1. Integrative causal inference frameworks
2. Multi-omics data integration methods
3. Network-based driver gene identification

For more details, see the original research papers and methodology documentation.