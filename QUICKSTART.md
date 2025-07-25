# LIHC多维度预后分析系统 - 快速开始指南

## 🚀 5分钟快速上手

### 1. 启动系统

```bash
# 使用Docker启动（推荐）
docker-compose -f docker-compose.professional.yml up -d

# 或使用Python直接运行
python main.py --professional
```

### 2. 访问Web界面

在浏览器中打开：
- 本地访问: http://localhost:8050
- HTTPS访问: https://localhost:8443

### 3. 运行第一个分析

#### 方式A: 使用Web界面
1. 点击导航栏中的"数据管理"
2. 上传您的表达数据（CSV格式）
3. 选择"运行分析"
4. 在仪表板中查看结果

#### 方式B: 使用Python API

```python
from src.analysis.integrated_analysis import IntegratedAnalysisPipeline

# 初始化分析流程
pipeline = IntegratedAnalysisPipeline()

# 运行分析
results = pipeline.run_integrated_analysis(
    expression_file="data/expression.csv",
    clinical_file="data/clinical.csv"
)

# 查看Top靶点
print(results['top_targets'][:10])
```

## 🧬 新功能特性：多组学数据整合

### 简单多组学分析

```python
from src.data_processing.multi_omics_integrator import MultiOmicsIntegrator

# 加载和整合数据
integrator = MultiOmicsIntegrator()
integrator.load_expression_data("expression.csv")
integrator.load_cnv_data("cnv.csv")
integrator.load_mutation_data("mutations.csv")

# 使用拼接方法整合
integrated = integrator.integrate_omics(method="concatenate")

# 保存结果
integrator.save_integrated_data("results/")
```

### ClosedLoop因果分析

```python
from src.analysis.closedloop_analyzer import ClosedLoopAnalyzer

# 运行因果推理
analyzer = ClosedLoopAnalyzer()
result = analyzer.analyze_causal_relationships(
    rna_data=expression_df,
    clinical_data=clinical_df,
    cnv_data=cnv_df
)

# 获取Top因果基因
top_genes = result.causal_genes[:20]
```

## 📊 演示分析

使用模拟数据运行完整演示：

```bash
cd examples
python demo_integrated_analysis.py
```

这将执行以下步骤：
1. 生成演示多组学数据
2. 运行集成分析
3. 识别因果驱动基因
4. 生成可视化图表
5. 创建HTML报告

## 📁 数据格式示例

### 表达数据 (CSV)
```
Gene,Sample_001,Sample_002,Sample_003
TP53,12.5,8.3,15.2
KRAS,5.6,7.8,4.3
EGFR,20.1,18.5,22.3
```

### 临床数据 (CSV)
```
Sample,survival_time,survival_status,age,stage
Sample_001,850,1,65,III
Sample_002,1200,0,58,II
Sample_003,450,1,72,IV
```

### 突变数据 (CSV)
```
gene_id,sample_id,mutation_type
TP53,Sample_001,missense
KRAS,Sample_002,nonsense
TP53,Sample_003,frameshift
```

## 🔧 常用操作

### 1. 筛选高置信度靶点
```python
# 获取综合评分 > 0.8 的基因
high_conf = results['integrated_scores']
high_conf = high_conf[high_conf['integrated_score'] > 0.8]
```

### 2. 导出结果
```python
# 导出到Excel
results['integrated_scores'].to_excel("top_targets.xlsx")

# 导出到CSV
results['top_targets'].to_csv("causal_genes.csv")
```

### 3. 可视化网络
```python
import matplotlib.pyplot as plt
import networkx as nx

# 绘制证据网络
G = results['evidence_network']
nx.draw(G, with_labels=True)
plt.show()
```

## 🐛 故障排除

### 问题："No module named 'src'"
**解决方案**：从项目根目录运行或添加到Python路径：
```python
import sys
sys.path.append('/path/to/mrna2')
```

### 问题："No common samples found"
**解决方案**：确保所有文件中的样本ID完全匹配（区分大小写）

### 问题：Docker容器无法启动
**解决方案**：
```bash
# 查看日志
docker-compose logs

# 重启容器
./docker-stop.sh
./docker-start.sh
```

## 📚 下一步

1. 阅读完整文档：
   - [多组学整合指南](docs/multi_omics_integration_guide.md)
   - [ClosedLoop分析指南](docs/closedloop_analysis_guide.md)

2. 探索示例教程：
   - `examples/multi_omics_tutorial.ipynb`
   - `examples/causal_analysis_demo.ipynb`

3. 加入社区：
   - 在GitHub上报告问题
   - 分享您的分析结果
   - 贡献代码改进

## 💡 获得最佳结果的建议

1. **数据质量**：确保表达数据经过适当的标准化
2. **样本数量**：建议最少50个样本以获得可靠结果
3. **整合方法**：从"concatenate"开始，复杂关系可尝试"SNF"
4. **结果验证**：始终检查bootstrap稳定性评分

## 🆘 获取帮助

- **文档资料**：查看 `/docs` 目录
- **示例代码**：参考 `/examples` 目录
- **问题报告**：GitHub Issues页面
- **邮件支持**：support@lihc-platform.org

---

祝您分析愉快！🧬🔬📊