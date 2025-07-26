# LIHC多维度预后分析系统

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

> 🧬 **基于多维度网络分析的肝癌预后分析平台**  
> 通过五维度肿瘤微环境分析发现关键治疗靶点

---

## 📋 目录

- [项目概述](#-项目概述)
- [系统功能](#-系统功能)
- [设计理念](#-设计理念)
- [科学原理](#-科学原理)
- [技术架构](#-技术架构)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [许可证](#-许可证)
- [致谢](#-致谢)

---

## 🎯 项目概述

### 背景与意义

肝细胞癌（LIHC）是全球第六大常见癌症，传统的生物标志物发现方法往往停留在统计关联层面，缺乏深层的机制解释。本项目通过创新的"多维度网络分析"理念，实现了从肿瘤微环境到临床预后的完整证据链分析。

### 科学创新

**传统方法的局限**:
```
表达数据 → 统计关联 → 候选基因 (缺乏机制解释)
```

**我们的创新方法**:
```
五维度分析 → 网络整合 → 关键节点识别 → 治疗靶点发现
     ↑                                         ↓
     └────── 完整的系统生物学分析链条 ←──────────┘
```

### 应用价值

- 🔬 **科学价值**: 首创五维度肿瘤微环境分析方法学
- 💊 **临床价值**: 提供具有完整机制解释的治疗靶点
- 🌐 **商业价值**: 服务制药公司、研究机构、临床中心
- 📈 **学术价值**: 推动生物信息学向系统分析转型

---

## 🆕 最新更新 (2025-07-27)

### v2.3 版本更新

1. **📝 完整报告下载系统** ✨
   - 修复了所有下载功能的500错误
   - 支持PDF、HTML、Word三种格式的自定义报告生成
   - 添加了openpyxl和python-docx依赖，支持Excel和Word文档导出
   - 优化了中文字体支持和报告内容结构

2. **🔧 技术优化**
   - 解决了数据表格下载缺少openpyxl依赖的问题
   - 改进了自定义报告生成逻辑，支持真正的PDF和Word文档
   - 增强了错误处理和容错机制
   - 优化了Docker构建和部署流程

3. **🎨 用户体验提升**
   - 所有下载按钮现在都能正常工作
   - 报告生成速度更快，内容更丰富
   - 改进了报告格式和样式

### v2.2 版本历史更新

1. **🎨 全新平台概览页面**
   - 专业的功能展示界面
   - 快速导航到各分析模块
   - 关键统计数据一览

2. **📊 统一数据统计卡片**
   - 所有分析页面现在都包含数据统计展示
   - 一致的视觉设计和用户体验
   - 实时数据指标更新

## 🚀 系统功能

### 1. 多维度肿瘤微环境分析

**五个生物学维度**：

| 维度 | 分析内容 | 关键基因示例 | 临床意义 |
|------|----------|-------------|----------|
| 🦠 **肿瘤细胞** | 癌细胞增殖、凋亡、代谢 | TP53, MYC, RAS, EGFR | 癌症驱动机制 |
| 🛡️ **免疫细胞** | T细胞、B细胞、NK细胞活性 | CD8A, FOXP3, PD-1, CTLA-4 | 免疫治疗指导 |
| 🧱 **基质细胞** | 成纤维细胞、内皮细胞 | COL1A1, VIM, ACTA2, FAP | 肿瘤支持环境 |
| 🕸️ **细胞外基质** | ECM重塑、侵袭转移 | MMP1, MMP9, TIMP1, LAMA1 | 转移风险评估 |
| 📡 **细胞因子** | 炎症反应、信号传导 | TNF, IL6, VEGFA, TGFB1 | 靶向治疗选择 |

### 2. 跨维度网络分析

**网络构建方法**：
- **相关性网络**: 基于Pearson/Spearman相关系数
- **调控网络**: 转录因子-靶基因关系
- **蛋白互作网络**: 基于STRING数据库
- **通路网络**: KEGG通路间的crosstalk

### 3. 关键靶点识别（Linchpin算法）

**Linchpin评分系统**：

```python
Linchpin Score = w1×预后评分 + w2×网络中心性 + w3×跨维度连接性 + w4×调控重要性

其中：
- 预后评分 (40%): 基于Cox回归的生存预测能力
- 网络中心性 (30%): 在分子网络中的重要位置
- 跨维度连接性 (20%): 连接不同生物学维度的能力  
- 调控重要性 (10%): 作为转录调控因子的影响力
```

### 4. 生存分析系统 ✨

**Kaplan-Meier生存曲线分析**：

| 分析类型 | 分析内容 | 统计方法 | 临床应用 |
|---------|----------|----------|----------|
| 📊 **总生存期 (OS)** | 从诊断到死亡的时间 | Kaplan-Meier + Log-rank | 预后评估 |
| 🔄 **无复发生存期 (RFS)** | 从治疗到复发的时间 | Kaplan-Meier + Log-rank | 治疗效果评估 |
| 🎯 **基因表达分组** | 根据中位数分为高/低表达组 | 中位数分组策略 | 个性化治疗 |
| 📈 **交互式可视化** | 生存曲线图表和统计结果 | Plotly交互图表 | 直观结果展示 |

### 5. 多组学数据整合 🧬 (新功能)

**支持的组学数据类型**：
- **RNA-seq表达数据**: 基因表达谱分析
- **拷贝数变异(CNV)**: 基因组结构变异
- **突变数据**: 体细胞突变谱
- **甲基化数据**: 表观遗传调控

**整合方法**：
- **简单拼接**: 直接特征合并
- **相似性网络融合(SNF)**: 基于网络的整合
- **多组学因子分析(MOFA)**: 因子模型整合

### 6. ClosedLoop因果推理分析 🔄 (新功能)

**五种证据类型整合**：
1. **差异表达证据**: 肿瘤vs正常组织
2. **生存关联证据**: 基因表达与预后关联
3. **CNV驱动证据**: 拷贝数变异驱动表达
4. **甲基化调控证据**: 表观遗传调控
5. **突变频率证据**: 体细胞突变富集

**因果评分系统**：
```
因果评分 = Σ(证据评分 × 权重) / Σ(权重)
```

**输出结果**：
- 高置信度因果基因列表
- 证据链追踪报告
- 因果网络可视化
- 通路富集分析

### 7. 智能分析引擎

**核心分析能力**：
- **🧠 智能推荐**: AI驱动的分析路径推荐
- **⚡ 实时分析**: 支持动态数据加载和在线分析
- **📊 批量处理**: 多数据集并行分析能力
- **🎯 精准医学**: 个性化治疗方案推荐
- **🔄 因果推理**: ClosedLoop多证据整合
- **🌐 多组学整合**: RNA-seq、CNV、突变、甲基化数据融合
- **💡 科学原理**: 每个模块配备详细的科学背景说明
- **🌍 国际化**: 完整的中英文双语支持

### 8. 完整报告下载系统 ✨ (新功能)

**多格式报告生成**：

| 格式类型 | 支持功能 | 技术实现 | 特色优势 |
|---------|----------|----------|----------|
| 📄 **PDF报告** | 自定义内容、中文字体、专业排版 | ReportLab + 中文字体支持 | 专业出版级质量 |
| 🌐 **HTML报告** | 响应式设计、交互元素、样式优化 | 现代CSS + 语义化标签 | 在线查看友好 |
| 📝 **Word文档** | 可编辑格式、标准排版、兼容性好 | python-docx库 | 二次编辑便利 |
| 📊 **Excel表格** | 数据导出、公式计算、图表嵌入 | openpyxl库 | 数据分析专用 |

**下载功能特色**：
- **🚀 一键生成**: 支持完整报告和自定义报告两种模式
- **📱 多设备兼容**: 所有格式都针对不同设备优化
- **🎨 专业排版**: 包含图表、表格、统计结果的完整版面
- **🔧 错误恢复**: 智能降级机制，确保下载成功
- **📦 批量导出**: 支持打包下载所有分析结果

### 9. 交互式数据可视化

**专业Dashboard界面**：
- **📱 概览中心**: 系统总览、快速导航、功能介绍
- **📤 数据管理**: 支持多格式上传、模板下载、数据验证
- **📊 分析结果**: 交互式图表、实时更新、导出报告
- **📈 生存分析**: Kaplan-Meier曲线、Cox回归、风险评估
- **🕸️ 网络分析**: 3D分子网络、社区检测、路径分析
- **🌐 多语言支持**: 中英文双语界面（i18n国际化）

---

## 💡 设计理念

### 系统设计哲学

**以用户为中心的设计**：
- **直觉性**: 复杂的生物信息学分析通过简洁界面实现
- **专业性**: 保持科学严谨性的同时提供友好的用户体验
- **可扩展性**: 模块化架构支持功能快速迭代和扩展
- **开放性**: 支持多种数据格式和分析流程的灵活配置

### 核心设计原则

**1. 科学严谨性**
```
统计学基础 + 生物学验证 + 临床可解释性 = 可信的分析结果
```

**2. 系统完整性**
```
数据输入 → 质量控制 → 多维分析 → 结果验证 → 报告输出
```

**3. 用户友好性**
```
零编程基础 + 一键式分析 + 可视化结果 + 专业报告
```

**4. 性能优化**
```
并行计算 + 智能缓存 + 增量更新 + 资源管理
```

### 创新架构特点

- **微服务架构**: 分析引擎、可视化、数据管理独立部署
- **容器化部署**: Docker支持一键部署和横向扩展
- **智能队列**: Celery任务队列支持大规模批量分析
- **实时协作**: WebSocket支持多用户实时数据共享
- **云原生**: 支持本地部署和云端SaaS两种模式

---

## 🔬 科学原理

### 多维度肿瘤微环境理论

**理论基础**：
肿瘤不是孤立的细胞群体，而是由肿瘤细胞、免疫细胞、基质细胞、细胞外基质和细胞因子构成的复杂生态系统。传统的单一维度分析无法捕捉这种复杂性。

**五维度分析框架**：

| 维度 | 生物学意义 | 分析方法 | 临床价值 |
|------|-----------|----------|----------|
| 🦠 **肿瘤细胞** | 癌症驱动机制 | 差异表达、通路富集 | 靶向治疗选择 |
| 🛡️ **免疫细胞** | 免疫应答状态 | 免疫评分、浸润分析 | 免疫治疗指导 |
| 🧱 **基质细胞** | 肿瘤支持环境 | 基质评分、纤维化分析 | 耐药机制预测 |
| 🕸️ **细胞外基质** | 侵袭转移能力 | ECM重塑、MMP活性 | 转移风险评估 |
| 📡 **细胞因子** | 微环境调节 | 信号通路、炎症反应 | 联合治疗策略 |

### 网络生物学原理

**理论依据**：
生物系统是由分子间相互作用构成的复杂网络。关键的治疗靶点往往位于网络的关键节点（hub nodes）或连接不同功能模块的桥接节点（bridge nodes）。

**Linchpin算法数学模型**：

```mathematics
Linchpin Score = Σ(wi × Si)

其中：
S1 = Prognostic Score = -log(p_value) × sign(β)  # Cox回归系数
S2 = Network Centrality = (Degree + Betweenness + Closeness) / 3
S3 = Cross-dimensional Connectivity = Σ(connections_across_dimensions)
S4 = Regulatory Importance = TF_score + miRNA_score

权重分配：w1=0.4, w2=0.3, w3=0.2, w4=0.1
```

### ClosedLoop因果推理原理

**科学背景**：
传统的关联分析无法区分因果关系和相关关系。ClosedLoop方法通过整合多层证据，构建因果推理链条。

**五证据整合模型**：

```mathematics
Causal Score = Σ(Ei × Wi) / Σ(Wi)

证据类型：
E1 = Differential Expression Evidence  # 差异表达证据
E2 = Survival Association Evidence     # 生存关联证据 
E3 = CNV Driving Evidence             # 拷贝数驱动证据
E4 = Methylation Regulation Evidence  # 甲基化调控证据
E5 = Mutation Frequency Evidence      # 突变频率证据

动态权重：Wi = confidence_score × evidence_strength
```

### 多组学数据整合理论

**整合策略**：
- **早期整合**: 特征层面的数据融合
- **中期整合**: 相似性网络融合(SNF)
- **晚期整合**: 结果层面的集成学习

**数学框架**：
```mathematics
# 相似性网络融合(SNF)
P(t+1) = S × (Σ P(t)k / m) × S^T

其中：
S = 相似性矩阵
P(t) = 第t次迭代的网络矩阵
m = 组学数据类型数量
```

### 统计学基础

**生存分析**：
- **Kaplan-Meier估计**: 非参数生存概率估计
- **Cox比例风险模型**: 多变量生存分析
- **Log-rank检验**: 生存曲线差异显著性检验

**网络分析**：
- **社区检测**: Louvain算法识别功能模块
- **中心性度量**: 度中心性、介数中心性、紧密中心性
- **路径分析**: 最短路径和关键路径识别

---

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    Web前端界面层                         │
│           Dash + Plotly + Bootstrap                   │
├─────────────────────────────────────────────────────────┤
│                    业务逻辑层                           │
│  ┌─────────────────┬─────────────────┬─────────────────┐ │
│  │   数据处理模块   │    分析算法模块   │   可视化模块     │ │
│  │                │                │                │ │
│  │ • 数据加载      │ • 差异分析      │ • 图表生成      │ │
│  │ • 质量控制      │ • 网络分析      │ • 交互设计      │ │
│  │ • 格式转换      │ • 生存分析      │ • 响应式布局     │ │
│  └─────────────────┴─────────────────┴─────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    数据访问层                           │
│           Pandas + NumPy + SciPy                     │
├─────────────────────────────────────────────────────────┤
│                    数据存储层                           │
│        CSV + HDF5 + JSON + Parquet                   │
└─────────────────────────────────────────────────────────┘
```

### 核心技术栈

**后端技术**:
```python
Python 3.9+              # 主开发语言
Flask/Dash               # Web框架
Pandas + NumPy           # 数据处理
SciPy + Scikit-learn     # 科学计算
Lifelines                # 生存分析
NetworkX                 # 网络分析
Plotly                   # 数据可视化
ReportLab                # PDF生成
python-docx              # Word文档生成
openpyxl                 # Excel文档处理
```

**容器化技术**:
```yaml
Docker                   # 容器运行时
Docker Compose           # 容器编排
PostgreSQL               # 数据库（生产环境）
Redis                    # 缓存服务
Nginx                    # 反向代理
Prometheus + Grafana     # 监控服务
```

---

## 🚀 快速开始

### Docker部署（推荐）

```bash
# 克隆项目
git clone https://github.com/your-username/lihc-analysis-platform.git
cd lihc-analysis-platform

# 使用Docker Compose启动
docker-compose up -d

# 访问应用
打开浏览器访问: http://localhost:8050
```

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行专业版界面
python main.py --dashboard --professional

# 或运行经典版界面
python main.py --dashboard
```

---

## 📖 使用指南

### 1. 访问应用

**访问地址**: http://localhost:8050

**界面模式**:

#### 经典布局（默认）
```bash
python main.py --dashboard
```

#### 专业布局（新增）✨
```bash
python main.py --dashboard --professional
```

专业布局特点：
- 顶部导航栏：数据管理、测试Demo、系统设置
- 侧边导航栏：分析功能、高级分析、分析结果
- 响应式设计，移动端友好
- 更清晰的功能组织

**主要页面**:

1. **📱 概览页面** (`/`)
   - 平台介绍和功能概述
   - 快速开始指南
   
2. **📊 演示结果** (`/demo`)
   - TCGA-LIHC完整分析结果
   - Top 20关键靶点展示
   
3. **📤 数据上传** (`/upload`)
   - 支持多种数据格式
   - 实时数据验证
   
4. **📈 生存分析** (`/survival`)
   - Kaplan-Meier生存曲线
   - 基因表达分组分析
   
5. **🕸️ 网络分析** (`/networks`)
   - 交互式分子网络
   - 网络拓扑分析

### 2. 数据格式要求

**临床数据** (`clinical_data.csv`):
```csv
sample_id,os_time,os_status,age,gender,stage,grade
TCGA-001,365,1,65,Male,II,G2
TCGA-002,1200,0,58,Female,I,G1
```

**表达数据** (`expression_data.csv`):
```csv
gene_id,TCGA-001,TCGA-002,TCGA-003
TP53,8.25,7.89,9.12
EGFR,6.78,7.45,6.23
```

### 3. 生存分析使用步骤

1. 访问"📈 Survival Analysis"标签
2. 选择目标基因（如TP53、MYC等）
3. 选择数据集（TCGA-LIHC演示数据）
4. 点击"📊 Generate Survival Curves"
5. 查看生存曲线和统计结果

---

## 📚 API文档

### REST API接口（开发中）

**基础信息**:
- **Base URL**: `http://localhost:8050/api/v1`
- **数据格式**: JSON

### 主要接口

```http
# 提交分析任务
POST /api/v1/analysis/submit

# 获取分析状态
GET /api/v1/analysis/status/{job_id}

# 获取结果
GET /api/v1/results/{job_id}
```

---

## 💻 开发指南

### 环境准备

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements-minimal.txt  # 快速开始
# 或
pip install -r requirements.txt  # 完整功能

# 运行测试
pytest tests/ --no-cov  # 快速测试
# 或
pytest tests/ --cov=src --cov-report=html  # 带覆盖率
```

### 代码规范

```bash
# 格式化代码
black src/ tests/
isort src/ tests/

# 代码检查
flake8 src/ tests/
mypy src/
```

---

## 📁 项目结构

```
lihc-analysis-platform/
├── 📁 src/                       # 源代码
│   ├── 📁 analysis/              # 分析算法
│   │   ├── stage1_multidimensional.py    # 多维度分析
│   │   ├── stage2_network.py             # 网络分析
│   │   ├── stage3_linchpin.py            # 关键靶点识别
│   │   ├── survival_analysis.py          # 生存分析
│   │   ├── closedloop_analyzer.py        # ClosedLoop因果分析
│   │   └── integrated_analysis.py        # 集成分析流程
│   ├── 📁 data_processing/       # 数据处理
│   │   ├── multi_omics_integrator.py     # 多组学整合
│   │   ├── multi_omics_loader.py         # 多组学加载器
│   │   └── quality_control.py            # 数据质量控制
│   ├── 📁 visualization/         # 可视化
│   │   └── unified_dashboard.py  # 统一仪表板
│   ├── 📁 utils/                 # 工具函数
│   │   ├── i18n.py              # 国际化支持
│   │   ├── logging_system.py    # 日志系统
│   │   └── common.py            # 通用工具
│   └── 📁 api/                  # API接口
│       └── main.py              # REST API
├── 📁 tests/                     # 测试代码
│   ├── test_multi_omics_integration.py   # 多组学测试
│   ├── test_closedloop_analyzer.py       # ClosedLoop测试
│   └── test_integrated_analysis.py       # 集成分析测试
├── 📁 examples/                  # 示例代码
│   ├── demo_integrated_analysis.py        # 完整演示
│   └── demo_data/               # 演示数据
├── 📁 docs/                      # 文档
│   ├── multi_omics_integration_guide.md  # 多组学指南
│   └── closedloop_analysis_guide.md      # ClosedLoop指南
├── 📄 Dockerfile                 # Docker镜像定义
├── 📄 main.py                    # 主程序入口
├── 📄 requirements.txt           # Python依赖
├── 📄 docker-compose.yml         # Docker编排配置
├── 📄 README.md                  # 项目说明
├── 📄 QUICKSTART.md              # 快速开始指南
└── 📄 FEATURE_SUMMARY.md         # 功能总结
```

---

## ❓ 常见问题

### Docker相关

**Q: Docker构建速度慢？**
```bash
# 使用Docker缓存层或配置镜像加速器
docker-compose build --no-cache=false

# 或使用国内镜像源
```

**Q: 端口被占用？**
```bash
# 查看端口占用
lsof -i :8050

# 使用其他端口
docker-compose up -d -e PORT=8051
```

### 功能相关

**Q: 生存分析功能不可用？**
- 确保使用的是更新后的镜像（包含lifelines和scipy）
- 检查Docker日志：`docker logs lihc-platform`

**Q: 如何使用自己的数据？**
1. 准备符合格式要求的数据文件
2. 访问"数据上传"页面
3. 上传数据并运行分析

**Q: 如何使用新的多组学整合功能？**
```python
# 参考 examples/demo_integrated_analysis.py
from src.data_processing.multi_omics_integrator import MultiOmicsIntegrator

integrator = MultiOmicsIntegrator()
# 加载各种组学数据
integrator.load_expression_data("expression.csv")
integrator.load_cnv_data("cnv.csv")
# 整合
integrated = integrator.integrate_omics()
```

**Q: ClosedLoop分析需要什么数据？**
- 必需：RNA表达数据 + 临床数据（含生存信息）
- 可选：CNV、突变、甲基化数据（提高准确性）

---

## 🤝 贡献指南

### 开发工作流

1. Fork项目
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建Pull Request

### 提交规范

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关

---

## 📊 升级规划

### 短期目标（3-6个月）

- ✅ 建立完善的测试体系
- ✅ 实现错误处理和日志系统
- ✅ 多组学数据整合（已完成）
- ✅ ClosedLoop因果推理分析（已完成）
- 📅 RESTful API接口

### 中长期目标

- 📅 云端SaaS版本
- 📅 机器学习集成
- 📅 多癌种支持
- 📅 插件系统架构

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

### 引用格式

如果本项目对您的研究有帮助，请引用：

```bibtex
@software{lihc_platform_2025,
  title={LIHC Multi-dimensional Prognostic Analysis Platform},
  author={AI-GuoKe Research Team},
  year={2025},
  url={https://github.com/ai-guoke/lihc-platform},
  version={v1.0}
}
```

---

## 🎉 致谢

感谢所有为本项目做出贡献的研究者、开发者和用户！

- 🙏 **TCGA研究网络** - 提供高质量的肿瘤基因组数据
- 🐍 **Python生态系统** - Pandas, NumPy, SciPy等
- 📈 **Plotly团队** - 优秀的交互式可视化库
- 🚀 **Dash框架** - Web应用开发框架

---

## 📄 版权信息

**版权所有 © 中国科学院大学杭州高等研究院**

本项目由中国科学院大学杭州高等研究院开发和维护。

**联系方式**：
- 机构：中国科学院大学杭州高等研究院
- 地址：浙江省杭州市
- 网站：[UCAS Hangzhou Institute](https://www.ucas.edu.cn/)

---

*最后更新: 2025年7月27日*  
*版本: v2.3* 🎉  
*项目状态: 积极维护*  

**平台特色**：
- 🧠 **创新算法**: 首创五维度肿瘤微环境分析框架
- 🔬 **科学严谨**: 基于统计学和生物学双重验证的分析流程
- 🎯 **精准医学**: 提供个性化治疗靶点和用药指导
- 🚀 **高性能**: 支持大规模数据并行处理和实时分析
- 🌐 **用户友好**: 零编程基础的Web界面和一键式分析
- 🔄 **完整生态**: 从数据输入到结果输出的完整解决方案