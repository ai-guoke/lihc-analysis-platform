"""
Integrated Analysis Pipeline: Multi-omics + ClosedLoop
整合多组学数据和闭环因果推理的完整分析流程
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
from analysis.stage1_multidimensional import Stage1Analyzer
from analysis.stage2_network import Stage2Analyzer
from analysis.stage3_linchpin import Stage3Analyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntegratedAnalysisPipeline:
    """整合的多组学+因果推理分析流程"""
    
    def __init__(self, data_dir: str = "data", results_dir: str = "results"):
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        
        # 初始化各个分析器
        self.multi_omics = MultiOmicsIntegrator(data_dir)
        self.closedloop = ClosedLoopAnalyzer(data_dir, results_dir)
        self.stage1 = Stage1Analyzer(data_dir, results_dir)
        self.stage2 = Stage2Analyzer(data_dir, results_dir)
        self.stage3 = Stage3Analyzer(data_dir, results_dir)
        
        self.integrated_results = {}
    
    def run_integrated_analysis(self, 
                              expression_file: Optional[str] = None,
                              cnv_file: Optional[str] = None,
                              mutation_file: Optional[str] = None,
                              methylation_file: Optional[str] = None,
                              clinical_file: Optional[str] = None) -> Dict:
        """运行完整的整合分析流程"""
        logger.info("Starting integrated multi-omics analysis pipeline...")
        
        # Step 1: 多组学数据整合
        logger.info("Step 1: Multi-omics data integration")
        integrated_data = self._load_and_integrate_omics(
            expression_file, cnv_file, mutation_file, methylation_file
        )
        
        # Step 2: ClosedLoop因果分析
        logger.info("Step 2: ClosedLoop causal inference analysis")
        closedloop_results = self._run_closedloop_analysis(clinical_file)
        
        # Step 3: 经典三阶段分析（使用整合数据）
        logger.info("Step 3: Classic three-stage analysis with integrated data")
        classic_results = self._run_classic_analysis_integrated()
        
        # Step 4: 结果整合和优先级排序
        logger.info("Step 4: Integrating results and prioritizing targets")
        final_results = self._integrate_all_results(
            closedloop_results, classic_results
        )
        
        # Step 5: 生成综合报告
        logger.info("Step 5: Generating comprehensive report")
        self._generate_integrated_report(final_results)
        
        self.integrated_results = final_results
        return final_results
    
    def _load_and_integrate_omics(self, expr_file, cnv_file, mut_file, meth_file):
        """加载和整合多组学数据"""
        
        # 加载各种组学数据
        if expr_file:
            self.multi_omics.load_expression_data(expr_file)
        
        if cnv_file:
            self.multi_omics.load_cnv_data(cnv_file)
        
        if mut_file:
            self.multi_omics.load_mutation_data(mut_file)
        
        if meth_file:
            self.multi_omics.load_methylation_data(meth_file)
        
        # 整合数据
        integrated = self.multi_omics.integrate_omics(
            integration_method="concatenate"  # 可选: "similarity_network", "mofa"
        )
        
        # 保存整合数据
        self.multi_omics.save_integrated_data(str(self.results_dir / "multi_omics"))
        
        return integrated
    
    def _run_closedloop_analysis(self, clinical_file):
        """运行ClosedLoop因果分析"""
        
        # 加载临床数据
        if clinical_file:
            clinical_data = pd.read_csv(clinical_file, index_col=0)
        else:
            # 使用演示数据
            clinical_data = self._generate_demo_clinical_data()
        
        # 获取组学数据
        expr_data = self.multi_omics.omics_data.get('expression')
        cnv_data = self.multi_omics.omics_data.get('cnv')
        mut_data = self.multi_omics.omics_data.get('mutation')
        meth_data = self.multi_omics.omics_data.get('methylation')
        
        # 分析基因组因果关系
        genomic_scores = self.closedloop.analyze_genomic_causality(
            expr_data, cnv_data, mut_data, meth_data, clinical_data
        )
        
        # 分析表型因果关系
        phenotypic_scores = self.closedloop.analyze_phenotypic_causality(
            expr_data, clinical_data, 'survival_status'
        )
        
        # 构建因果网络
        self.closedloop.build_causal_network(genomic_scores, phenotypic_scores)
        
        # 计算ClosedLoop评分
        closedloop_scores = self.closedloop.calculate_closedloop_scores()
        
        # 生成证据报告
        evidence_report = self.closedloop.generate_evidence_report(top_n=50)
        
        return {
            'closedloop_scores': closedloop_scores,
            'evidence_report': evidence_report,
            'causal_network': self.closedloop.causal_graph
        }
    
    def _run_classic_analysis_integrated(self):
        """使用整合数据运行经典分析"""
        
        # 准备整合后的表达数据
        integrated_expr = self.multi_omics.integrated_features
        
        # 保存为临时文件供经典分析使用
        temp_expr_file = self.data_dir / "processed" / "integrated_expression.csv"
        temp_expr_file.parent.mkdir(exist_ok=True)
        integrated_expr.to_csv(temp_expr_file)
        
        # 运行三阶段分析
        # Stage 1: 多维度分析
        stage1_results = self.stage1.run_analysis()
        
        # Stage 2: 网络分析
        stage2_results = self.stage2.run_analysis()
        
        # Stage 3: Linchpin识别
        stage3_results = self.stage3.run_analysis()
        
        return {
            'stage1': stage1_results,
            'stage2': stage2_results,
            'stage3': stage3_results
        }
    
    def _integrate_all_results(self, closedloop_results, classic_results):
        """整合所有分析结果"""
        
        # 获取各种评分
        closedloop_scores = closedloop_results['closedloop_scores']
        linchpin_scores = classic_results['stage3']['linchpin_scores'] if classic_results['stage3'] else pd.DataFrame()
        
        # 找出共同基因
        if not linchpin_scores.empty and not closedloop_scores.empty:
            common_genes = list(set(closedloop_scores.index) & set(linchpin_scores.index))
        else:
            common_genes = []
        
        # 创建综合评分表
        integrated_scores = pd.DataFrame(index=common_genes)
        
        if common_genes:
            # 添加各种评分
            integrated_scores['closedloop_score'] = closedloop_scores.loc[common_genes, 'closedloop_score']
            integrated_scores['linchpin_score'] = linchpin_scores.loc[common_genes, 'linchpin_score']
            
            # 标准化评分
            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler()
            
            integrated_scores['closedloop_normalized'] = scaler.fit_transform(
                integrated_scores[['closedloop_score']]
            )
            integrated_scores['linchpin_normalized'] = scaler.fit_transform(
                integrated_scores[['linchpin_score']]
            )
            
            # 计算综合评分（可调整权重）
            integrated_scores['integrated_score'] = (
                integrated_scores['closedloop_normalized'] * 0.6 +  # ClosedLoop权重更高
                integrated_scores['linchpin_normalized'] * 0.4
            )
            
            # 排序
            integrated_scores = integrated_scores.sort_values('integrated_score', ascending=False)
        
        # 添加额外信息
        final_results = self._enrich_results(integrated_scores, closedloop_results, classic_results)
        
        return final_results
    
    def _enrich_results(self, integrated_scores, closedloop_results, classic_results):
        """丰富结果信息"""
        
        enriched_results = {
            'integrated_scores': integrated_scores,
            'top_targets': [],
            'evidence_summary': {},
            'network_properties': {},
            'multi_omics_features': {}
        }
        
        # 为Top靶点添加详细信息
        for gene in integrated_scores.head(20).index:
            target_info = {
                'gene': gene,
                'integrated_score': integrated_scores.loc[gene, 'integrated_score'],
                'closedloop_score': integrated_scores.loc[gene, 'closedloop_score'],
                'linchpin_score': integrated_scores.loc[gene, 'linchpin_score'],
                'evidence_chain': self._get_evidence_chain(gene, closedloop_results),
                'network_centrality': self._get_network_centrality(gene, classic_results),
                'multi_omics_profile': self._get_multiomics_profile(gene),
                'therapeutic_potential': self._assess_therapeutic_potential(gene)
            }
            enriched_results['top_targets'].append(target_info)
        
        return enriched_results
    
    def _get_evidence_chain(self, gene, closedloop_results):
        """获取基因的证据链"""
        if gene in self.closedloop.evidence_chains:
            return [
                {
                    'type': e.evidence_type,
                    'score': e.score,
                    'p_value': e.p_value,
                    'direction': e.direction
                }
                for e in self.closedloop.evidence_chains[gene]
            ]
        return []
    
    def _get_network_centrality(self, gene, classic_results):
        """获取网络中心性信息"""
        # 从Stage 2结果中提取
        return {}
    
    def _get_multiomics_profile(self, gene):
        """获取多组学特征谱"""
        profile = {}
        
        for omics_type, data in self.multi_omics.omics_data.items():
            if gene in data.index:
                profile[omics_type] = {
                    'mean': float(data.loc[gene].mean()),
                    'std': float(data.loc[gene].std()),
                    'min': float(data.loc[gene].min()),
                    'max': float(data.loc[gene].max())
                }
        
        return profile
    
    def _assess_therapeutic_potential(self, gene):
        """评估治疗潜力"""
        # 这里可以集成药物数据库信息
        return {
            'druggability': 'Unknown',
            'known_drugs': [],
            'clinical_trials': 0
        }
    
    def _generate_integrated_report(self, results):
        """生成综合分析报告"""
        report_dir = self.results_dir / "integrated_report"
        report_dir.mkdir(exist_ok=True)
        
        # 1. 保存综合评分表
        if 'integrated_scores' in results and not results['integrated_scores'].empty:
            results['integrated_scores'].to_csv(report_dir / "integrated_target_scores.csv")
        
        # 2. 生成Top靶点报告
        if results['top_targets']:
            top_targets_df = pd.DataFrame(results['top_targets'])
            top_targets_df.to_csv(report_dir / "top_therapeutic_targets.csv", index=False)
        
        # 3. 可视化因果网络
        self.closedloop.visualize_causal_network(
            str(report_dir / "integrated_causal_network.png"),
            top_n=30
        )
        
        # 4. 生成HTML报告
        self._create_html_report(results, report_dir)
        
        logger.info(f"Integrated analysis report saved to {report_dir}")
    
    def _create_html_report(self, results, output_dir):
        """创建HTML格式的综合报告"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>LIHC Integrated Multi-omics Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2, h3 { color: #333; }
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .score-high { color: #d73027; font-weight: bold; }
                .score-medium { color: #fee08b; }
                .score-low { color: #1a9850; }
            </style>
        </head>
        <body>
            <h1>LIHC Integrated Multi-omics Analysis Report</h1>
            <h2>Executive Summary</h2>
            <p>This report presents the integrated results from multi-omics data integration 
            and ClosedLoop causal inference analysis.</p>
            
            <h2>Top Therapeutic Targets</h2>
            <table>
                <tr>
                    <th>Rank</th>
                    <th>Gene</th>
                    <th>Integrated Score</th>
                    <th>ClosedLoop Score</th>
                    <th>Linchpin Score</th>
                    <th>Evidence Types</th>
                </tr>
        """
        
        # 添加Top靶点
        for i, target in enumerate(results['top_targets'][:20], 1):
            evidence_types = len(target.get('evidence_chain', []))
            score_class = 'score-high' if target['integrated_score'] > 0.8 else 'score-medium'
            
            html_content += f"""
                <tr>
                    <td>{i}</td>
                    <td><b>{target['gene']}</b></td>
                    <td class="{score_class}">{target['integrated_score']:.3f}</td>
                    <td>{target['closedloop_score']:.3f}</td>
                    <td>{target['linchpin_score']:.3f}</td>
                    <td>{evidence_types} types</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h2>Analysis Details</h2>
            <h3>Multi-omics Integration</h3>
            <p>Data types integrated: Expression, CNV, Mutation, Methylation</p>
            
            <h3>ClosedLoop Causal Analysis</h3>
            <p>Causal network constructed with genomic and phenotypic evidence</p>
            
            <h3>Network Analysis</h3>
            <p>Cross-dimensional network analysis performed</p>
            
            <hr>
            <p><i>Generated by LIHC Analysis Platform</i></p>
        </body>
        </html>
        """
        
        with open(output_dir / "integrated_analysis_report.html", 'w') as f:
            f.write(html_content)
    
    def _generate_demo_clinical_data(self):
        """生成演示用临床数据"""
        n_samples = 100
        sample_names = [f"Sample_{i:03d}" for i in range(n_samples)]
        
        clinical_data = pd.DataFrame({
            'survival_time': np.random.exponential(1000, n_samples),
            'survival_status': np.random.binomial(1, 0.6, n_samples),
            'age': np.random.normal(60, 10, n_samples),
            'gender': np.random.choice(['M', 'F'], n_samples),
            'stage': np.random.choice(['I', 'II', 'III', 'IV'], n_samples),
            'grade': np.random.choice([1, 2, 3], n_samples)
        }, index=sample_names)
        
        return clinical_data


def demo_integrated_analysis():
    """运行整合分析演示"""
    
    # 创建分析流程
    pipeline = IntegratedAnalysisPipeline()
    
    # 准备演示数据文件路径
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成演示数据（实际使用时替换为真实数据路径）
    from data_processing.multi_omics_integrator import demo_multi_omics_integration
    demo_multi_omics_integration()
    
    # 运行整合分析
    results = pipeline.run_integrated_analysis(
        expression_file="data/raw/test_expression.csv",
        cnv_file="data/raw/test_cnv.csv",
        mutation_file="data/raw/test_mutations.csv",
        methylation_file=None,  # 可选
        clinical_file=None  # 将使用演示数据
    )
    
    print("\n=== Integrated Analysis Complete ===")
    print(f"Top 10 integrated targets:")
    if 'integrated_scores' in results and not results['integrated_scores'].empty:
        print(results['integrated_scores'].head(10))
    
    print("\nResults saved to: results/integrated_report/")
    
    return results


if __name__ == "__main__":
    # 运行演示
    demo_integrated_analysis()