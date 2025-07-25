"""
Demo: Complete Integrated Analysis Pipeline
This script demonstrates the full workflow of multi-omics integration
and ClosedLoop causal inference analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Add parent directory to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.analysis.integrated_analysis_simple import SimpleIntegratedPipeline
from src.data_processing.multi_omics_integrator import MultiOmicsIntegrator
from src.analysis.closedloop_analyzer import ClosedLoopAnalyzer


def generate_demo_data(output_dir: Path):
    """Generate demo multi-omics data for testing"""
    print("Generating demo data...")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parameters
    n_samples = 200
    n_genes = 500
    
    # Sample and gene names
    samples = [f"Patient_{i:03d}" for i in range(n_samples)]
    genes = [f"Gene_{i:04d}" for i in range(n_genes)]
    
    # Generate correlated multi-omics data
    np.random.seed(42)
    
    # 1. Expression data (log-normal distribution)
    expr_data = pd.DataFrame(
        np.random.lognormal(8, 2, (n_genes, n_samples)),
        index=genes,
        columns=samples
    )
    
    # Add some highly variable genes (potential drivers)
    driver_genes = np.random.choice(n_genes, 50, replace=False)
    expr_data.iloc[driver_genes, :] *= np.random.uniform(2, 5, (50, n_samples))
    
    expr_data.to_csv(output_dir / "expression.csv")
    
    # 2. CNV data (correlated with expression)
    cnv_data = pd.DataFrame(
        np.random.normal(0, 0.3, (n_genes, n_samples)),
        index=genes,
        columns=samples
    )
    
    # Add CNV-driven genes
    cnv_drivers = np.random.choice(driver_genes, 20, replace=False)
    for gene_idx in cnv_drivers:
        # CNV correlates with expression
        cnv_data.iloc[gene_idx, :] = (
            expr_data.iloc[gene_idx, :].values / expr_data.iloc[gene_idx, :].mean() - 1
        ) * 0.5 + np.random.normal(0, 0.1, n_samples)
    
    cnv_data.to_csv(output_dir / "cnv.csv")
    
    # 3. Mutation data
    mutation_records = []
    for gene_idx in range(n_genes):
        # Driver genes have higher mutation frequency
        if gene_idx in driver_genes:
            mut_freq = 0.2
        else:
            mut_freq = 0.05
        
        n_mutations = int(n_samples * mut_freq)
        mutated_samples = np.random.choice(samples, n_mutations, replace=False)
        
        for sample in mutated_samples:
            mutation_records.append({
                'gene_id': genes[gene_idx],
                'sample_id': sample,
                'mutation_type': np.random.choice(['missense', 'nonsense', 'frameshift'])
            })
    
    mutation_df = pd.DataFrame(mutation_records)
    mutation_df.to_csv(output_dir / "mutations.csv", index=False)
    
    # 4. Methylation data (anti-correlated with expression for some genes)
    methylation_data = pd.DataFrame(
        np.random.beta(2, 5, (n_genes, n_samples)),
        index=genes,
        columns=samples
    )
    
    # Add methylation-regulated genes
    meth_regulated = np.random.choice(driver_genes, 15, replace=False)
    for gene_idx in meth_regulated:
        # Methylation anti-correlates with expression
        methylation_data.iloc[gene_idx, :] = 1 - (
            expr_data.iloc[gene_idx, :].values / expr_data.iloc[gene_idx, :].max()
        ) * 0.8 + np.random.normal(0, 0.05, n_samples)
    
    methylation_data = methylation_data.clip(0, 1)
    methylation_data.to_csv(output_dir / "methylation.csv")
    
    # 5. Clinical data
    # Create survival data correlated with driver gene expression
    risk_score = expr_data.iloc[driver_genes, :].mean(axis=0)
    risk_score = (risk_score - risk_score.mean()) / risk_score.std()
    
    # Higher expression of driver genes -> shorter survival
    base_survival = 1000
    survival_times = base_survival * np.exp(-risk_score * 0.3) * np.random.lognormal(0, 0.5, n_samples)
    
    # Ensure survival probability is within valid range
    survival_prob = 0.7 - risk_score * 0.1
    survival_prob = np.clip(survival_prob, 0.1, 0.9)  # Keep within [0.1, 0.9]
    survival_status = np.random.binomial(1, survival_prob, n_samples)
    
    clinical_data = pd.DataFrame({
        'survival_time': survival_times,
        'survival_status': survival_status,
        'age': np.random.normal(60, 10, n_samples),
        'gender': np.random.choice(['M', 'F'], n_samples),
        'stage': np.random.choice(['I', 'II', 'III', 'IV'], n_samples, p=[0.2, 0.3, 0.3, 0.2]),
        'risk_score': risk_score
    }, index=samples)
    
    clinical_data.to_csv(output_dir / "clinical.csv")
    
    print(f"Demo data generated in {output_dir}")
    return driver_genes, genes


def run_integrated_analysis_demo():
    """Run complete integrated analysis demo"""
    
    # Setup directories
    data_dir = Path("demo_data")
    results_dir = Path("demo_results")
    results_dir.mkdir(exist_ok=True)
    
    # Generate demo data
    driver_indices, all_genes = generate_demo_data(data_dir)
    driver_genes = [all_genes[i] for i in driver_indices]
    
    print("\n" + "="*60)
    print("Starting Integrated Multi-omics Analysis")
    print("="*60)
    
    # Initialize pipeline
    pipeline = SimpleIntegratedPipeline(
        data_dir=str(data_dir.parent),
        results_dir=str(results_dir)
    )
    
    # Run integrated analysis
    results = pipeline.run_integrated_analysis(
        expression_file=str(data_dir / "expression.csv"),
        cnv_file=str(data_dir / "cnv.csv"),
        mutation_file=str(data_dir / "mutations.csv"),
        methylation_file=str(data_dir / "methylation.csv"),
        clinical_file=str(data_dir / "clinical.csv")
    )
    
    print("\n" + "="*60)
    print("Analysis Results")
    print("="*60)
    
    # Display top targets
    if 'integrated_scores' in results and not results['integrated_scores'].empty:
        top_targets = results['integrated_scores'].head(20)
        print("\nTop 20 Therapeutic Targets:")
        print(top_targets)
        
        # Check how many true drivers were identified
        identified_drivers = [g for g in top_targets.index if g in driver_genes]
        print(f"\nTrue positive rate: {len(identified_drivers)}/20 = {len(identified_drivers)/20:.1%}")
    
    # Visualize results
    visualize_results(results, results_dir)
    
    print(f"\nResults saved to {results_dir}")
    print("Check the integrated_report directory for detailed HTML report")
    
    return results


def visualize_results(results, output_dir):
    """Create visualizations of analysis results"""
    
    if 'integrated_scores' not in results or results['integrated_scores'].empty:
        print("No integrated scores to visualize")
        return
    
    # Create figure directory
    fig_dir = output_dir / "figures"
    fig_dir.mkdir(exist_ok=True)
    
    # 1. Score distribution plot
    plt.figure(figsize=(10, 6))
    scores_df = results['integrated_scores'].head(30)
    
    # Create bar plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Integrated scores
    ax1.bar(range(len(scores_df)), scores_df['integrated_score'], color='darkblue')
    ax1.set_xticks(range(len(scores_df)))
    ax1.set_xticklabels(scores_df.index, rotation=45, ha='right')
    ax1.set_ylabel('Integrated Score')
    ax1.set_title('Top 30 Causal Genes - Integrated Scores')
    ax1.grid(axis='y', alpha=0.3)
    
    # Component scores
    if 'closedloop_score' in scores_df.columns and 'linchpin_score' in scores_df.columns:
        x = np.arange(len(scores_df))
        width = 0.35
        
        ax2.bar(x - width/2, scores_df['closedloop_score'], width, 
                label='ClosedLoop Score', color='steelblue')
        ax2.bar(x + width/2, scores_df['linchpin_score'], width, 
                label='Linchpin Score', color='darkorange')
        
        ax2.set_xticks(x)
        ax2.set_xticklabels(scores_df.index, rotation=45, ha='right')
        ax2.set_ylabel('Score')
        ax2.set_title('Component Scores Comparison')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(fig_dir / "causal_gene_scores.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Score correlation plot
    if 'closedloop_score' in scores_df.columns and 'linchpin_score' in scores_df.columns:
        plt.figure(figsize=(8, 8))
        plt.scatter(scores_df['closedloop_score'], scores_df['linchpin_score'], 
                   s=100, alpha=0.6, c=scores_df['integrated_score'], cmap='viridis')
        plt.xlabel('ClosedLoop Score', fontsize=12)
        plt.ylabel('Linchpin Score', fontsize=12)
        plt.title('ClosedLoop vs Linchpin Scores', fontsize=14)
        plt.colorbar(label='Integrated Score')
        
        # Add correlation
        corr = scores_df['closedloop_score'].corr(scores_df['linchpin_score'])
        plt.text(0.05, 0.95, f'Correlation: {corr:.3f}', 
                transform=plt.gca().transAxes, fontsize=12,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.grid(True, alpha=0.3)
        plt.savefig(fig_dir / "score_correlation.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    # 3. Evidence summary for top targets
    if results.get('top_targets'):
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.ravel()
        
        for i, target in enumerate(results['top_targets'][:4]):
            ax = axes[i]
            
            # Extract evidence chain info
            evidence_types = []
            evidence_scores = []
            
            if target.get('evidence_chain'):
                for evidence in target['evidence_chain']:
                    evidence_types.append(evidence['type'].value.replace('_', '\n'))
                    evidence_scores.append(evidence['score'])
            
            if evidence_types:
                ax.bar(evidence_types, evidence_scores, color='teal')
                ax.set_title(f"{target['gene']} - Evidence Profile", fontsize=12)
                ax.set_ylabel('Evidence Score')
                ax.set_ylim(0, 1)
                ax.grid(axis='y', alpha=0.3)
            else:
                ax.text(0.5, 0.5, 'No evidence data', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title(f"{target['gene']}", fontsize=12)
        
        plt.suptitle('Evidence Profiles for Top 4 Targets', fontsize=14)
        plt.tight_layout()
        plt.savefig(fig_dir / "evidence_profiles.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"\nVisualizations saved to {fig_dir}")


def analyze_demo_performance():
    """Analyze performance metrics of the integrated analysis"""
    
    # This would typically include:
    # - Computation time analysis
    # - Memory usage profiling  
    # - Accuracy metrics (if ground truth is known)
    # - Stability analysis across multiple runs
    
    pass


if __name__ == "__main__":
    # Run the integrated analysis demo
    results = run_integrated_analysis_demo()
    
    # Additional analysis can be performed here
    # analyze_demo_performance()