# LIHC Analysis Platform 🧬

<div align="center">

![Version](https://img.shields.io/badge/version-2.6-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey)

**基于多维度网络分析的肝癌预后分析平台**  
**Multi-dimensional Network Analysis Platform for Hepatocellular Carcinoma Prognosis**

[快速开始](#-快速开始) | [功能介绍](#-核心功能) | [部署文档](docs/DEPLOYMENT.md) | [开发指南](docs/DEVELOPMENT.md) | [English](README_EN.md)

<img src="docs/images/platform_screenshot.png" alt="Platform Screenshot" width="800"/>

</div>

---

## 🌟 项目简介

LIHC Analysis Platform 是一个专门针对肝细胞癌（Hepatocellular Carcinoma）的综合性生物信息学分析平台。平台整合了多组学数据，通过先进的网络分析和机器学习算法，为研究者提供全面的肝癌预后分析解决方案。

### 🎯 核心价值

- **🔬 科学创新**: 首创五维度肿瘤微环境综合分析方法
- **💊 临床转化**: 识别具有完整机制解释的治疗靶点
- **📊 数据整合**: 多组学数据融合分析
- **🎨 用户体验**: Apple风格UI设计，操作简洁流畅

## ✨ 核心功能

### 1. 五维度肿瘤微环境分析
<details>
<summary>点击展开详情</summary>

- **肿瘤细胞维度**: 增殖、凋亡、EMT相关基因分析
- **免疫细胞维度**: 28种免疫细胞浸润评估
- **基质细胞维度**: CAFs活化状态评估
- **细胞外基质维度**: ECM重塑相关分子分析
- **细胞因子维度**: 炎症因子网络分析

</details>

### 2. Linchpin靶点识别
<details>
<summary>点击展开详情</summary>

独创的Linchpin算法通过以下步骤识别关键治疗靶点：
1. 构建多层生物网络
2. 计算节点中心性指标
3. 模拟基因扰动影响
4. 评估靶点可成药性

</details>

### 3. AI生物标志物发现
<details>
<summary>点击展开详情</summary>

- 机器学习特征选择（LASSO、Random Forest、SVM-RFE）
- 深度学习预后模型（DeepSurv）
- 多组学特征整合
- 交叉验证与外部验证

</details>

### 4. 精准医学预测
<details>
<summary>点击展开详情</summary>

- 药物敏感性预测
- 免疫治疗响应评估
- 分子分型识别
- 个性化治疗方案推荐

</details>

## 🚀 快速开始

### 系统要求

- Python 3.8 或更高版本
- 8GB RAM（推荐16GB）
- 10GB 可用磁盘空间
- 现代浏览器（Chrome 90+, Firefox 88+, Safari 14+, Edge 90+）

### 一键部署（Docker）

```bash
# 克隆项目
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform

# 使用Docker Compose启动
docker-compose up -d

# 访问平台
open http://localhost:8050
```

### 本地安装

```bash
# 1. 克隆项目
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 Windows:
# venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动平台
python main.py --dashboard --port 8050

# 5. 访问平台
open http://localhost:8050
```

## 📁 项目结构

```
lihc-analysis-platform/
├── 📂 src/                        # 源代码目录
│   ├── 📊 analysis/              # 核心分析模块
│   │   ├── survival_analysis.py      # 生存分析
│   │   ├── network_analysis.py       # 网络分析
│   │   ├── five_dimension_prognostic.py  # 五维度分析
│   │   ├── ai_biomarker.py          # AI生物标志物
│   │   └── linchpin_target.py       # Linchpin靶点
│   ├── 🎨 visualization/         # 可视化模块
│   │   └── professional_dashboard.py # 主仪表板
│   ├── 📤 data_processing/       # 数据处理
│   │   ├── data_upload_manager.py   # 数据上传
│   │   └── data_preprocessor.py     # 数据预处理
│   └── 🔧 utils/                # 工具函数
├── 📂 data/                     # 数据目录
│   ├── demo/                   # 演示数据
│   ├── cache/                  # 缓存数据
│   └── user/                   # 用户上传数据
├── 📂 results/                  # 分析结果
├── 📂 docs/                     # 文档
│   ├── DEPLOYMENT.md           # 部署指南
│   ├── DEVELOPMENT.md          # 开发文档
│   └── API.md                  # API文档
├── 📂 tests/                    # 测试代码
├── 📂 docker/                   # Docker配置
├── 📄 requirements.txt          # Python依赖
├── 📄 docker-compose.yml        # Docker Compose配置
├── 📄 Dockerfile               # Docker镜像定义
└── 📄 main.py                  # 主程序入口
```

## 🔧 配置说明

### 基础配置

创建 `.env` 文件配置环境变量：

```env
# 应用配置
APP_ENV=production
APP_DEBUG=false
SECRET_KEY=your-secret-key-here

# 服务器配置
HOST=0.0.0.0
PORT=8050

# 数据配置
DATA_DIR=./data
RESULTS_DIR=./results
MAX_UPLOAD_SIZE=100MB

# 分析配置
PARALLEL_WORKERS=4
ANALYSIS_TIMEOUT=3600

# 缓存配置（可选）
CACHE_TYPE=redis
REDIS_URL=redis://localhost:6379/0
```

### 高级配置

编辑 `config/config.yaml` 自定义分析参数：

```yaml
analysis:
  survival:
    min_samples: 20
    p_value_threshold: 0.05
    confidence_interval: 0.95
  
  network:
    correlation_method: pearson
    correlation_threshold: 0.6
    min_node_degree: 3
  
  dimension_weights:
    tumor: 0.3
    immune: 0.25
    stromal: 0.2
    ecm: 0.15
    cytokine: 0.1
```

## 📊 使用指南

### 1. 数据准备

支持的数据格式：
- **表达矩阵**: CSV/TSV格式，行为基因，列为样本
- **临床数据**: 包含生存时间(OS.time)和状态(OS)列
- **突变数据**: MAF格式或简化的突变矩阵

示例数据结构：
```
# 表达矩阵 (expression_matrix.csv)
Gene_Symbol,Sample1,Sample2,Sample3,...
TP53,10.5,8.3,12.1,...
EGFR,5.2,6.8,4.9,...

# 临床数据 (clinical_data.csv)
Sample_ID,OS.time,OS,Age,Stage,...
Sample1,365,1,65,III,...
Sample2,730,0,58,II,...
```

### 2. 运行分析

1. **上传数据**: 点击"数据上传"，选择相应文件
2. **选择分析**: 在左侧导航栏选择分析模块
3. **设置参数**: 根据需要调整分析参数
4. **开始分析**: 点击"开始分析"按钮
5. **查看结果**: 分析完成后查看交互式结果

### 3. 结果解读

- **生存曲线**: Kaplan-Meier曲线展示不同组别生存差异
- **网络图**: 基因/蛋白相互作用网络，节点大小表示重要性
- **热图**: 基因表达模式可视化
- **评分表**: 各维度得分及综合评分

## 🧬 科学原理

### Linchpin算法原理

```python
def identify_linchpin_targets(network, expression_data):
    """
    识别网络中的关键调控节点
    
    原理：
    1. 拓扑重要性 = 度中心性 × 介数中心性 × 紧密中心性
    2. 生物学重要性 = 表达变异度 × 生存相关性
    3. Linchpin得分 = 拓扑重要性 × 生物学重要性 × 可成药性
    """
    pass
```

### 五维度评分算法

```python
def calculate_five_dimension_score(sample_data):
    """
    计算样本的五维度综合评分
    
    Score = Σ(Di × Wi)
    其中：
    - Di: 第i个维度的标准化得分
    - Wi: 第i个维度的权重（通过Cox回归优化）
    """
    pass
```

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 如何贡献

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范

- 代码风格：遵循 PEP 8
- 提交信息：使用语义化版本控制
- 文档：为新功能添加文档
- 测试：确保测试覆盖率 > 80%

## 📚 文档

- [部署指南](docs/DEPLOYMENT.md) - 详细的部署说明
- [开发文档](docs/DEVELOPMENT.md) - 开发者指南
- [API文档](docs/API.md) - API接口说明
- [算法文档](docs/ALGORITHMS.md) - 核心算法详解
- [常见问题](docs/FAQ.md) - 常见问题解答

## 🔬 引用

如果您在研究中使用了本平台，请引用：

```bibtex
@software{lihc_platform_2024,
  title = {LIHC Analysis Platform: A Multi-dimensional Network Analysis System for Hepatocellular Carcinoma},
  author = {Your Research Group},
  year = {2024},
  url = {https://github.com/ai-guoke/lihc-analysis-platform},
  version = {2.6}
}
```

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- **数据来源**: TCGA, GEO, ICGC数据库
- **算法参考**: NetworkX, scikit-learn, lifelines
- **UI框架**: Dash, Plotly, Bootstrap
- **开发支持**: 中国科学院大学杭州高等研究院

## 📧 联系我们

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/ai-guoke/lihc-analysis-platform/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/ai-guoke/lihc-analysis-platform/discussions)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=ai-guoke/lihc-analysis-platform&type=Date)](https://star-history.com/#ai-guoke/lihc-analysis-platform&Date)

---

<div align="center">

**Made with ❤️ for Cancer Research**

[返回顶部](#lihc-analysis-platform-)

</div>