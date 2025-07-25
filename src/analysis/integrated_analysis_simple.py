"""
Simplified Integrated Analysis Pipeline: Multi-omics + ClosedLoop
整合多组学数据和闭环因果推理的完整分析流程（简化版）
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

from data_processing.multi_omics_integrator import MultiOmicsIntegrator
from analysis.closedloop_analyzer import ClosedLoopAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleIntegratedPipeline:
    """简化的整合分析流程"""
    
    def __init__(self, data_dir: str = "data", results_dir: str = "results"):
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        
        # 初始化分析器
        self.multi_omics = MultiOmicsIntegrator(data_dir)
        
        # Use more lenient parameters for demo
        closedloop_config = {
            'p_value_threshold': 0.1,  # More lenient
            'effect_size_threshold': 0.2,  # Lower threshold
            'causal_score_threshold': 0.4  # Lower threshold for demo
        }
        self.closedloop = ClosedLoopAnalyzer(closedloop_config)
        
        self.integrated_results = {}
    
    def run_integrated_analysis(self, 
                              expression_file: Optional[str] = None,
                              cnv_file: Optional[str] = None,
                              mutation_file: Optional[str] = None,
                              methylation_file: Optional[str] = None,
                              clinical_file: Optional[str] = None) -> Dict:
        """运行完整的整合分析流程"""
        logger.info("Starting simplified integrated analysis pipeline...")
        
        # Step 1: 多组学数据整合
        logger.info("Step 1: Multi-omics data integration")
        integrated_data = self._load_and_integrate_omics(
            expression_file, cnv_file, mutation_file, methylation_file
        )
        
        # Step 2: ClosedLoop因果分析
        logger.info("Step 2: ClosedLoop causal inference analysis")
        closedloop_results = self._run_closedloop_analysis(clinical_file)
        
        # Step 3: 结果整合
        logger.info("Step 3: Integrating results")
        final_results = self._integrate_results(closedloop_results)
        
        # Step 4: 生成报告
        logger.info("Step 4: Generating report")
        self._generate_report(final_results)
        
        self.integrated_results = final_results
        return final_results
    
    def _load_and_integrate_omics(self, expr_file, cnv_file, mut_file, meth_file):
        """加载和整合多组学数据"""
        
        # 加载各种组学数据
        loaded_count = 0
        
        if expr_file:
            self.multi_omics.load_expression_data(expr_file)
            loaded_count += 1
        
        if cnv_file:
            self.multi_omics.load_cnv_data(cnv_file)
            loaded_count += 1
        
        if mut_file:
            self.multi_omics.load_mutation_data(mut_file)
            loaded_count += 1
        
        if meth_file:
            self.multi_omics.load_methylation_data(meth_file)
            loaded_count += 1
        
        if loaded_count == 0:
            raise ValueError("No omics data loaded")
        
        # 整合数据
        integrated = self.multi_omics.integrate_omics(
            integration_method="concatenate"
        )
        
        # 保存整合数据
        self.multi_omics.save_integrated_data(str(self.results_dir / "multi_omics"))
        
        return integrated
    
    def _run_closedloop_analysis(self, clinical_file):
        """运行ClosedLoop因果分析"""
        
        # 获取组学数据
        expr_data = self.multi_omics.omics_data.get('expression')
        cnv_data = self.multi_omics.omics_data.get('cnv')
        mut_data = self.multi_omics.omics_data.get('mutation')
        meth_data = self.multi_omics.omics_data.get('methylation')
        
        # 加载或生成临床数据
        if clinical_file:
            clinical_data = pd.read_csv(clinical_file, index_col=0)
        else:
            clinical_data = self._generate_demo_clinical_data()
        
        # 分析因果关系
        result = self.closedloop.analyze_causal_relationships(
            rna_data=expr_data,
            clinical_data=clinical_data,
            cnv_data=cnv_data,
            methylation_data=meth_data,
            mutation_data=mut_data
        )
        
        return {
            'causal_genes': result.causal_genes,
            'evidence_network': result.evidence_network,
            'pathway_analysis': result.pathway_analysis,
            'validation_metrics': result.validation_metrics
        }
    
    def _integrate_results(self, closedloop_results):
        """整合分析结果"""
        
        # 提取因果基因
        causal_genes = closedloop_results['causal_genes']
        
        # 创建结果表
        gene_scores = []
        for gene in causal_genes:
            gene_scores.append({
                'gene_id': gene.gene_id,
                'causal_score': gene.causal_score,
                'confidence_level': gene.confidence_level,
                'n_evidence_types': len(gene.evidence_scores)
            })
        
        integrated_scores = pd.DataFrame(gene_scores)
        
        if not integrated_scores.empty:
            integrated_scores = integrated_scores.set_index('gene_id')
            integrated_scores = integrated_scores.sort_values('causal_score', ascending=False)
        
        # 创建top targets列表
        top_targets = []
        for gene in causal_genes[:20]:  # Top 20
            target_info = {
                'gene': gene.gene_id,
                'causal_score': gene.causal_score,
                'confidence': gene.confidence_level,
                'evidence_chain': gene.evidence_chain
            }
            top_targets.append(target_info)
        
        return {
            'integrated_scores': integrated_scores,
            'top_targets': top_targets,
            'pathway_analysis': closedloop_results['pathway_analysis'],
            'validation_metrics': closedloop_results['validation_metrics']
        }
    
    def _generate_report(self, results):
        """生成分析报告"""
        report_dir = self.results_dir / "integrated_report"
        report_dir.mkdir(exist_ok=True)
        
        # 保存综合评分表
        if 'integrated_scores' in results and not results['integrated_scores'].empty:
            results['integrated_scores'].to_csv(report_dir / "causal_gene_scores.csv")
        
        # 保存Top靶点
        if results['top_targets']:
            top_targets_df = pd.DataFrame(results['top_targets'])
            top_targets_df.to_csv(report_dir / "top_targets.csv", index=False)
        
        # 生成简单的文本报告
        with open(report_dir / "analysis_summary.txt", 'w') as f:
            f.write("LIHC Integrated Analysis Summary\n")
            f.write("="*50 + "\n\n")
            
            if 'integrated_scores' in results and not results['integrated_scores'].empty:
                f.write(f"Total causal genes identified: {len(results['integrated_scores'])}\n")
                f.write(f"High confidence genes: {sum(results['integrated_scores']['confidence_level'] == 'High')}\n")
                f.write(f"Medium confidence genes: {sum(results['integrated_scores']['confidence_level'] == 'Medium')}\n")
                f.write(f"Low confidence genes: {sum(results['integrated_scores']['confidence_level'] == 'Low')}\n\n")
                
                f.write("Top 10 Causal Genes:\n")
                for i, (gene, row) in enumerate(results['integrated_scores'].head(10).iterrows(), 1):
                    f.write(f"{i}. {gene}: Score={row['causal_score']:.3f}, Confidence={row['confidence_level']}\n")
            
            if 'validation_metrics' in results:
                f.write(f"\nValidation Metrics:\n")
                for metric, value in results['validation_metrics'].items():
                    f.write(f"  {metric}: {value:.3f}\n")
        
        logger.info(f"Report saved to {report_dir}")
    
    def _generate_demo_clinical_data(self):
        """生成演示用临床数据"""
        # Get sample names from expression data
        expr_data = self.multi_omics.omics_data.get('expression')
        if expr_data is None or expr_data.empty:
            n_samples = 100
            sample_names = [f"Sample_{i:03d}" for i in range(n_samples)]
        else:
            sample_names = expr_data.columns
            n_samples = len(sample_names)
        
        clinical_data = pd.DataFrame({
            'survival_time': np.random.exponential(1000, n_samples),
            'survival_status': np.random.binomial(1, 0.3, n_samples),
            'age': np.random.normal(60, 10, n_samples),
            'gender': np.random.choice(['M', 'F'], n_samples),
            'stage': np.random.choice(['I', 'II', 'III', 'IV'], n_samples)
        }, index=sample_names)
        
        return clinical_data


def demo_simple_integrated_analysis():
    """运行简化的整合分析演示"""
    
    # 创建分析流程
    pipeline = SimpleIntegratedPipeline()
    
    # 准备演示数据文件路径
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成演示数据
    from data_processing.multi_omics_integrator import demo_multi_omics_integration
    demo_multi_omics_integration()
    
    # 运行整合分析
    results = pipeline.run_integrated_analysis(
        expression_file="data/raw/test_expression.csv",
        cnv_file="data/raw/test_cnv.csv",
        mutation_file="data/raw/test_mutations.csv"
    )
    
    print("\n=== Integrated Analysis Complete ===")
    print(f"Top 10 causal genes:")
    if 'integrated_scores' in results and not results['integrated_scores'].empty:
        print(results['integrated_scores'].head(10))
    
    print("\nResults saved to: results/integrated_report/")
    
    return results


if __name__ == "__main__":
    # 运行演示
    demo_simple_integrated_analysis()