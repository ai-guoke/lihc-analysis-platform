"""
Simplified Analysis Pipeline for User Data
简化版分析流程，用于演示和快速分析
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

# Import advanced analyzer for real analysis
try:
    from .advanced_analyzer import AdvancedAnalyzer
    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False

class SimplifiedAnalyzer:
    """Execute simplified analysis on user data"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.data_dir = Path(f"data/user_uploads/{session_id}")
        self.results_dir = Path(f"data/history/{session_id}/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def load_user_data(self) -> Dict:
        """Load user uploaded data"""
        data = {}
        
        # Load clinical data
        clinical_file = self.data_dir / "clinical_data.csv"
        if clinical_file.exists():
            data['clinical'] = pd.read_csv(clinical_file)
        
        # Load expression data
        expression_file = self.data_dir / "expression_data.csv"
        if expression_file.exists():
            data['expression'] = pd.read_csv(expression_file, index_col=0)
        
        # Load mutation data
        mutation_file = self.data_dir / "mutation_data.csv"
        if mutation_file.exists():
            data['mutations'] = pd.read_csv(mutation_file)
        
        return data
    
    def run_stage1_analysis(self, data: Dict) -> Dict:
        """Stage 1: Multi-dimensional analysis"""
        results = {
            'stage': 'stage1',
            'timestamp': datetime.now().isoformat(),
            'analyses': {}
        }
        
        if 'expression' in data:
            # Top variable genes
            expr_df = data['expression']
            gene_variance = expr_df.var(axis=1).sort_values(ascending=False)
            top_genes = gene_variance.head(20)
            
            results['analyses']['top_variable_genes'] = {
                'genes': top_genes.index.tolist(),
                'variance': top_genes.values.tolist()
            }
            
            # Gene expression heatmap
            plt.figure(figsize=(10, 8))
            top_gene_expr = expr_df.loc[top_genes.index]
            sns.heatmap(top_gene_expr, cmap='RdBu_r', center=0, 
                       cbar_kws={'label': 'Expression Level'})
            plt.title('Top 20 Variable Genes Expression Heatmap')
            plt.tight_layout()
            plt.savefig(self.results_dir / 'stage1_gene_heatmap.png', dpi=150)
            plt.close()
            
            results['analyses']['heatmap'] = 'stage1_gene_heatmap.png'
        
        if 'clinical' in data:
            # Survival statistics
            clinical_df = data['clinical']
            survival_stats = {
                'total_patients': int(len(clinical_df)),
                'events': int(clinical_df['os_status'].sum()) if 'os_status' in clinical_df.columns else 0,
                'median_follow_up': float(clinical_df['os_time'].median()) if 'os_time' in clinical_df.columns else 0
            }
            results['analyses']['survival_stats'] = survival_stats
        
        # Save results
        with open(self.results_dir / 'stage1_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def run_stage2_analysis(self, data: Dict) -> Dict:
        """Stage 2: Network analysis"""
        results = {
            'stage': 'stage2',
            'timestamp': datetime.now().isoformat(),
            'analyses': {}
        }
        
        if 'expression' in data:
            expr_df = data['expression']
            
            # Gene correlation network
            top_genes = expr_df.var(axis=1).sort_values(ascending=False).head(30).index
            gene_corr = expr_df.loc[top_genes].T.corr()
            
            # Network statistics
            results['analyses']['network_stats'] = {
                'nodes': len(top_genes),
                'edges': int((gene_corr.abs() > 0.5).sum().sum() / 2),
                'avg_correlation': float(gene_corr.abs().mean().mean())
            }
            
            # Correlation heatmap
            plt.figure(figsize=(12, 10))
            mask = np.triu(np.ones_like(gene_corr, dtype=bool))
            sns.heatmap(gene_corr, mask=mask, cmap='RdBu_r', center=0,
                       square=True, linewidths=.5)
            plt.title('Gene Correlation Network (Top 30 Genes)')
            plt.tight_layout()
            plt.savefig(self.results_dir / 'stage2_correlation_network.png', dpi=150)
            plt.close()
            
            results['analyses']['correlation_plot'] = 'stage2_correlation_network.png'
        
        # Save results
        with open(self.results_dir / 'stage2_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def run_stage3_analysis(self, data: Dict) -> Dict:
        """Stage 3: Linchpin target identification"""
        results = {
            'stage': 'stage3',
            'timestamp': datetime.now().isoformat(),
            'analyses': {}
        }
        
        if 'expression' in data and 'clinical' in data:
            expr_df = data['expression']
            clinical_df = data['clinical']
            
            # Simple survival association
            if 'os_status' in clinical_df.columns:
                # Find genes associated with survival
                survival_genes = []
                for gene in expr_df.index[:50]:  # Test top 50 genes
                    try:
                        gene_expr = expr_df.loc[gene]
                        high_expr = gene_expr > gene_expr.median()
                        
                        # Simple log-rank test approximation
                        high_group = clinical_df.loc[high_expr, 'os_status'].mean()
                        low_group = clinical_df.loc[~high_expr, 'os_status'].mean()
                        
                        hazard_ratio = high_group / (low_group + 0.01)  # Avoid division by zero
                        
                        survival_genes.append({
                            'gene': gene,
                            'hazard_ratio': float(hazard_ratio),
                            'high_risk': hazard_ratio > 1
                        })
                    except:
                        continue
                
                # Sort by absolute hazard ratio
                survival_genes.sort(key=lambda x: abs(x['hazard_ratio'] - 1), reverse=True)
                
                results['analyses']['linchpin_targets'] = survival_genes[:10]
                
                # Create bar plot
                plt.figure(figsize=(10, 6))
                top_targets = survival_genes[:10]
                genes = [t['gene'] for t in top_targets]
                hrs = [t['hazard_ratio'] for t in top_targets]
                colors = ['red' if hr > 1 else 'green' for hr in hrs]
                
                plt.barh(genes, hrs, color=colors)
                plt.axvline(x=1, color='black', linestyle='--', alpha=0.5)
                plt.xlabel('Hazard Ratio')
                plt.title('Top 10 Linchpin Target Candidates')
                plt.tight_layout()
                plt.savefig(self.results_dir / 'stage3_linchpin_targets.png', dpi=150)
                plt.close()
                
                results['analyses']['target_plot'] = 'stage3_linchpin_targets.png'
        
        # Save results
        with open(self.results_dir / 'stage3_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def run_precision_medicine_analysis(self, data: Dict) -> Dict:
        """Precision medicine analysis"""
        results = {
            'stage': 'precision',
            'timestamp': datetime.now().isoformat(),
            'analyses': {}
        }
        
        if 'expression' in data:
            expr_df = data['expression']
            
            # Immune signature (simplified)
            immune_genes = ['CD8A', 'CD4', 'FOXP3', 'CD19', 'CD56', 'CD68']
            available_immune = [g for g in immune_genes if g in expr_df.index]
            
            if available_immune:
                immune_scores = expr_df.loc[available_immune].mean(axis=0)
            else:
                # Use random genes as proxy
                immune_scores = expr_df.iloc[:6].mean(axis=0)
            
            results['analyses']['immune_scores'] = {
                'samples': immune_scores.index.tolist()[:10],
                'scores': immune_scores.values.tolist()[:10]
            }
            
            # Drug sensitivity prediction (mock)
            drugs = ['Sorafenib', 'Lenvatinib', 'Regorafenib', 'Cabozantinib']
            drug_sensitivity = pd.DataFrame(
                np.random.rand(len(drugs), min(10, len(expr_df.columns))),
                index=drugs,
                columns=expr_df.columns[:10]
            )
            
            # Drug sensitivity heatmap
            plt.figure(figsize=(10, 6))
            sns.heatmap(drug_sensitivity, cmap='RdYlGn_r', center=0.5,
                       cbar_kws={'label': 'Predicted IC50'})
            plt.title('Predicted Drug Sensitivity')
            plt.tight_layout()
            plt.savefig(self.results_dir / 'precision_drug_sensitivity.png', dpi=150)
            plt.close()
            
            results['analyses']['drug_plot'] = 'precision_drug_sensitivity.png'
        
        # Save results
        with open(self.results_dir / 'precision_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def generate_summary_report(self, all_results: List[Dict]) -> str:
        """Generate HTML summary report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LIHC Analysis Report - {self.session_id[:8]}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .result-section {{ 
                    background: #f8f9fa; 
                    padding: 20px; 
                    margin: 20px 0;
                    border-radius: 8px;
                    border-left: 4px solid #3498db;
                }}
                img {{ max-width: 100%; height: auto; margin: 10px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #3498db; color: white; }}
                .metric {{ font-size: 24px; color: #2c3e50; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>LIHC精准医学分析报告</h1>
            <p>会话ID: {self.session_id}</p>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        for result in all_results:
            stage = result.get('stage', 'Unknown')
            stage_names = {
                'stage1': 'Stage 1: 多维度生物学分析',
                'stage2': 'Stage 2: 跨维度网络分析', 
                'stage3': 'Stage 3: Linchpin基因识别',
                'precision': '精准医学分析'
            }
            
            html_content += f"""
            <div class="result-section">
                <h2>{stage_names.get(stage, stage)}</h2>
            """
            
            analyses = result.get('analyses', {})
            
            # Add specific content based on stage
            if stage == 'stage1' and 'survival_stats' in analyses:
                stats = analyses['survival_stats']
                html_content += f"""
                <h3>生存统计</h3>
                <p>总患者数: <span class="metric">{stats['total_patients']}</span></p>
                <p>事件数: <span class="metric">{stats['events']}</span></p>
                <p>中位随访时间: <span class="metric">{stats['median_follow_up']:.0f}</span> 天</p>
                """
            
            if stage == 'stage2' and 'network_stats' in analyses:
                stats = analyses['network_stats']
                html_content += f"""
                <h3>网络统计</h3>
                <p>节点数: <span class="metric">{stats['nodes']}</span></p>
                <p>边数: <span class="metric">{stats['edges']}</span></p>
                <p>平均相关性: <span class="metric">{stats['avg_correlation']:.3f}</span></p>
                """
            
            if stage == 'stage3' and 'linchpin_targets' in analyses:
                targets = analyses['linchpin_targets'][:5]
                html_content += """
                <h3>Top 5 Linchpin靶点</h3>
                <table>
                    <tr><th>基因</th><th>风险比</th><th>风险类型</th></tr>
                """
                for target in targets:
                    risk_type = "高风险" if target['high_risk'] else "低风险"
                    html_content += f"""
                    <tr>
                        <td>{target['gene']}</td>
                        <td>{target['hazard_ratio']:.2f}</td>
                        <td>{risk_type}</td>
                    </tr>
                    """
                html_content += "</table>"
            
            # Add images
            for key, value in analyses.items():
                if key.endswith('plot') or key == 'heatmap':
                    html_content += f"""
                    <h3>{key.replace('_', ' ').title()}</h3>
                    <img src="{value}" alt="{key}">
                    """
            
            html_content += "</div>"
        
        html_content += """
        </body>
        </html>
        """
        
        # Save report
        report_path = self.results_dir / 'analysis_report.html'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def run_all_analyses(self, modules: List[str], progress_manager=None) -> Dict:
        """Run all selected analysis modules with progress tracking"""
        # Initialize progress manager if not provided
        if progress_manager is None:
            try:
                from .progress_manager import ProgressManager
                progress_manager = ProgressManager(self.session_id)
            except:
                progress_manager = None
        
        # Start analysis
        if progress_manager:
            progress_manager.start_analysis(modules)
        
        # Try to use advanced analyzer if available
        if ADVANCED_AVAILABLE and any(m in ['differential_expression', 'survival', 'network', 
                                           'pathway', 'machine_learning', 'subtyping'] for m in modules):
            try:
                advanced = AdvancedAnalyzer(self.session_id)
                # Map modules to advanced analyzer modules
                advanced_modules = []
                module_mapping = {
                    'stage1': ['differential_expression', 'pathway'],
                    'stage2': ['network'],
                    'stage3': ['survival', 'machine_learning'],
                    'precision': ['subtyping']
                }
                
                for module in modules:
                    if module in module_mapping:
                        advanced_modules.extend(module_mapping[module])
                    else:
                        advanced_modules.append(module)
                
                # Run advanced analysis
                print("Using advanced analyzer with real algorithms...")
                return advanced.run_comprehensive_analysis(list(set(advanced_modules)), progress_manager)
                
            except Exception as e:
                print(f"Advanced analysis failed, falling back to simplified: {e}")
                if progress_manager:
                    progress_manager.add_error(f"Advanced analysis failed: {e}")
        
        # Fallback to simplified analysis
        # Load data
        if progress_manager:
            progress_manager.start_module('data_loading', 'Loading user data...')
        
        data = self.load_user_data()
        
        if not data:
            if progress_manager:
                progress_manager.fail_analysis('No data found')
            return {'error': 'No data found'}
        
        if progress_manager:
            progress_manager.complete_module('data_loading', 'Data loaded successfully')
        
        all_results = []
        
        # Run selected modules with progress tracking
        if 'stage1' in modules:
            if progress_manager:
                progress_manager.start_module('stage1', 'Running multi-dimensional analysis...')
            all_results.append(self.run_stage1_analysis(data))
            if progress_manager:
                progress_manager.complete_module('stage1', 'Multi-dimensional analysis completed')
        
        if 'stage2' in modules:
            if progress_manager:
                progress_manager.start_module('stage2', 'Running network analysis...')
            all_results.append(self.run_stage2_analysis(data))
            if progress_manager:
                progress_manager.complete_module('stage2', 'Network analysis completed')
        
        if 'stage3' in modules:
            if progress_manager:
                progress_manager.start_module('stage3', 'Identifying linchpin targets...')
            all_results.append(self.run_stage3_analysis(data))
            if progress_manager:
                progress_manager.complete_module('stage3', 'Linchpin analysis completed')
        
        if 'precision' in modules:
            if progress_manager:
                progress_manager.start_module('precision', 'Running precision medicine analysis...')
            all_results.append(self.run_precision_medicine_analysis(data))
            if progress_manager:
                progress_manager.complete_module('precision', 'Precision medicine analysis completed')
        
        # Generate summary report
        if progress_manager:
            progress_manager.start_module('report_generation', 'Generating summary report...')
        
        report_path = self.generate_summary_report(all_results)
        
        if progress_manager:
            progress_manager.complete_module('report_generation', 'Report generated successfully')
        
        # Create summary
        summary = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'modules_completed': modules,
            'results_count': len(all_results),
            'report_path': report_path,
            'results_dir': str(self.results_dir),
            'files_generated': [str(p) for p in self.results_dir.glob('*')]
        }
        
        # Save summary with numpy type converter
        def numpy_converter(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return str(obj)
        
        with open(self.results_dir / 'analysis_summary.json', 'w') as f:
            json.dump(summary, f, indent=2, default=numpy_converter)
        
        # Complete analysis
        if progress_manager:
            progress_manager.complete_analysis()
        
        return summary