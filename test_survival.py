#!/usr/bin/env python3
"""
Test Survival Analysis Functionality
"""

import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir
sys.path.insert(0, str(project_root))

from src.analysis.survival_analysis import SurvivalAnalyzer, create_demo_survival_data
import plotly.graph_objects as go

def test_survival_analysis():
    """Test survival analysis with different genes"""
    
    print("🧬 LIHC生存分析测试")
    print("=" * 50)
    
    # Initialize analyzer and demo data
    analyzer = SurvivalAnalyzer()
    clinical_data, expression_data = create_demo_survival_data()
    
    # Test genes
    test_genes = ['TP53', 'MYC', 'KRAS', 'EGFR']
    
    for gene in test_genes:
        print(f"\n🎯 分析基因: {gene}")
        print("-" * 30)
        
        # Perform survival analysis
        results = analyzer.perform_survival_analysis(
            clinical_data, expression_data, gene, 'TCGA-LIHC'
        )
        
        if results.get('error'):
            print(f"❌ 错误: {results['error']}")
            continue
            
        # Display results
        print(f"📊 基因: {results['gene_name']}")
        print(f"📚 数据集: {results['dataset_name']}")
        
        if results.get('os_analysis'):
            os = results['os_analysis']
            significance = "显著" if os['p_value'] < 0.05 else "不显著"
            print(f"⚰️  总生存期 (OS):")
            print(f"   - 样本数: {os['total_samples']}")
            print(f"   - 高表达组: n={os['high_count']}")
            print(f"   - 低表达组: n={os['low_count']}")
            print(f"   - Log-rank p值: {os['p_value']:.4f} ({significance})")
        
        if results.get('rfs_analysis'):
            rfs = results['rfs_analysis']
            significance = "显著" if rfs['p_value'] < 0.05 else "不显著"
            print(f"🔄 无复发生存期 (RFS):")
            print(f"   - 样本数: {rfs['total_samples']}")
            print(f"   - 高表达组: n={rfs['high_count']}")
            print(f"   - 低表达组: n={rfs['low_count']}")
            print(f"   - Log-rank p值: {rfs['p_value']:.4f} ({significance})")
        
        # Create and validate plots
        try:
            survival_fig = analyzer.create_survival_plots(results)
            print(f"✅ Kaplan-Meier曲线生成成功")
        except Exception as e:
            print(f"❌ 图表生成失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 生存分析测试完成!")
    
    # Generate example usage instructions
    print("\n📋 使用方法:")
    print("1. 在仪表板中选择'📈 Survival Analysis'标签")
    print("2. 在下拉菜单中选择目标基因 (如 TP53)")
    print("3. 选择数据集 (TCGA-LIHC)")
    print("4. 点击'📊 Generate Survival Curves'按钮")
    print("5. 查看Kaplan-Meier生存曲线和统计结果")
    
    print("\n🔍 结果解读:")
    print("• 红色曲线: 高表达组")
    print("• 蓝色曲线: 低表达组")
    print("• P < 0.05: 统计学显著差异")
    print("• 曲线越高: 生存概率越好")

if __name__ == "__main__":
    test_survival_analysis()