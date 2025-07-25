# Quick Start Guide - LIHC Multi-omics Analysis Platform

## 🚀 Getting Started in 5 Minutes

### 1. Start the Platform

```bash
# Using Docker (recommended)
./docker-start.sh

# Or using Python directly
python main.py
```

### 2. Access the Web Interface

Open your browser and navigate to:
- Local: http://localhost:8050
- With SSL: https://localhost:8443

### 3. Run Your First Analysis

#### Option A: Using the Web Interface
1. Click "Upload Data" in the navigation
2. Upload your expression data (CSV format)
3. Select "Run Analysis" 
4. View results in the dashboard

#### Option B: Using Python API

```python
from src.analysis.integrated_analysis import IntegratedAnalysisPipeline

# Initialize pipeline
pipeline = IntegratedAnalysisPipeline()

# Run analysis
results = pipeline.run_integrated_analysis(
    expression_file="data/expression.csv",
    clinical_file="data/clinical.csv"
)

# View top targets
print(results['top_targets'][:10])
```

## 🧬 New Features: Multi-omics Integration

### Simple Multi-omics Analysis

```python
from src.data_processing.multi_omics_integrator import MultiOmicsIntegrator

# Load and integrate data
integrator = MultiOmicsIntegrator()
integrator.load_expression_data("expression.csv")
integrator.load_cnv_data("cnv.csv")
integrator.load_mutation_data("mutations.csv")

# Integrate using concatenation
integrated = integrator.integrate_omics(method="concatenate")

# Save results
integrator.save_integrated_data("results/")
```

### ClosedLoop Causal Analysis

```python
from src.analysis.closedloop_analyzer import ClosedLoopAnalyzer

# Run causal inference
analyzer = ClosedLoopAnalyzer()
result = analyzer.analyze_causal_relationships(
    rna_data=expression_df,
    clinical_data=clinical_df,
    cnv_data=cnv_df
)

# Get top causal genes
top_genes = result.causal_genes[:20]
```

## 📊 Demo Analysis

Run the complete demo with simulated data:

```bash
cd examples
python demo_integrated_analysis.py
```

This will:
1. Generate demo multi-omics data
2. Run integrated analysis
3. Identify causal driver genes
4. Generate visualizations
5. Create HTML report

## 📁 Data Format Examples

### Expression Data (CSV)
```
Gene,Sample_001,Sample_002,Sample_003
TP53,12.5,8.3,15.2
KRAS,5.6,7.8,4.3
EGFR,20.1,18.5,22.3
```

### Clinical Data (CSV)
```
Sample,survival_time,survival_status,age,stage
Sample_001,850,1,65,III
Sample_002,1200,0,58,II
Sample_003,450,1,72,IV
```

### Mutation Data (CSV)
```
gene_id,sample_id,mutation_type
TP53,Sample_001,missense
KRAS,Sample_002,nonsense
TP53,Sample_003,frameshift
```

## 🔧 Common Tasks

### 1. Filter High-Confidence Targets
```python
# Get genes with integrated score > 0.8
high_conf = results['integrated_scores']
high_conf = high_conf[high_conf['integrated_score'] > 0.8]
```

### 2. Export Results
```python
# Export to Excel
results['integrated_scores'].to_excel("top_targets.xlsx")

# Export to CSV
results['top_targets'].to_csv("causal_genes.csv")
```

### 3. Visualize Networks
```python
import matplotlib.pyplot as plt
import networkx as nx

# Plot evidence network
G = results['evidence_network']
nx.draw(G, with_labels=True)
plt.show()
```

## 🐛 Troubleshooting

### Issue: "No module named 'src'"
**Solution**: Run from project root directory or add to Python path:
```python
import sys
sys.path.append('/path/to/mrna2')
```

### Issue: "No common samples found"
**Solution**: Ensure sample IDs match exactly across all files (case-sensitive)

### Issue: Docker container won't start
**Solution**: 
```bash
# Check logs
docker-compose logs

# Restart containers
./docker-stop.sh
./docker-start.sh
```

## 📚 Next Steps

1. Read the full documentation:
   - [Multi-omics Integration Guide](docs/multi_omics_integration_guide.md)
   - [ClosedLoop Analysis Guide](docs/closedloop_analysis_guide.md)

2. Explore example notebooks:
   - `examples/multi_omics_tutorial.ipynb`
   - `examples/causal_analysis_demo.ipynb`

3. Join the community:
   - Report issues on GitHub
   - Share your results
   - Contribute improvements

## 💡 Tips for Best Results

1. **Data Quality**: Ensure proper normalization of expression data
2. **Sample Size**: Minimum 50 samples recommended for reliable results
3. **Integration Method**: Start with "concatenate", try "SNF" for complex relationships
4. **Validation**: Always check bootstrap stability scores

## 🆘 Getting Help

- **Documentation**: Check `/docs` folder
- **Examples**: See `/examples` folder
- **Issues**: GitHub Issues page
- **Email**: support@lihc-platform.org

---

Happy analyzing! 🧬🔬📊