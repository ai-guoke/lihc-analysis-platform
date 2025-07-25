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
- [快速开始](#-快速开始)
- [Docker部署](#-docker部署)
- [核心功能](#-核心功能)
- [技术架构](#-技术架构)
- [使用指南](#-使用指南)
- [API文档](#-api文档)
- [开发指南](#-开发指南)
- [项目结构](#-项目结构)
- [常见问题](#-常见问题)
- [贡献指南](#-贡献指南)
- [升级规划](#-升级规划)

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

## ⚡ 快速开始

### 方式1：Docker一键启动（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform

# 2. 使用Docker启动脚本（自动构建并运行）
./docker-start.sh

# 3. 访问Web界面
# 浏览器打开: http://localhost:8050
```

### 方式2：Python本地运行

```bash
# 1. 克隆项目
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform

# 2. 安装依赖
pip install -r requirements-minimal.txt  # 最小依赖
# 或
pip install -r requirements.txt  # 完整依赖

# 3. 启动应用
python main.py

# 4. 访问Web界面
# 浏览器打开: http://localhost:8050
```

### 新功能快速体验

```python
# 多组学整合分析
from src.data_processing.multi_omics_integrator import MultiOmicsIntegrator

integrator = MultiOmicsIntegrator()
integrator.load_expression_data("data/expression.csv")
integrator.load_cnv_data("data/cnv.csv")
integrated = integrator.integrate_omics(method="concatenate")

# ClosedLoop因果分析
from src.analysis.closedloop_analyzer import ClosedLoopAnalyzer

analyzer = ClosedLoopAnalyzer()
result = analyzer.analyze_causal_relationships(
    rna_data=expression_df,
    clinical_data=clinical_df
)
```

---

## 🐳 Docker部署

### 方式1: 使用Docker启动脚本（推荐）

```bash
# 使用交互式启动脚本
./docker-start.sh

# 停止服务
./docker-stop.sh

# 查看服务状态
./docker-status.sh
```

### 方式2: 手动Docker部署

#### 快速体验模式（推荐测试）
```bash
# 构建并启动最小化版本
docker-compose -f docker-compose.minimal.yml up -d

# 访问应用
open http://localhost:8050
```

#### 开发模式（包含热重载）
```bash
# 启动开发环境
docker-compose -f docker-compose.dev.yml up -d

# 还可以访问Jupyter环境
open http://localhost:8888
```

#### 生产模式（完整服务栈）
```bash
# 生成环境配置
cp .env.example .env
# 编辑.env文件配置数据库密码等

# 启动完整服务
docker-compose up -d

# 访问服务
open http://localhost:8050  # 主应用
open http://localhost:3000  # Grafana监控
open http://localhost:9090  # Prometheus
```

### Docker服务说明

| 服务 | 端口 | 说明 | 运行模式 |
|------|------|------|----------|
| lihc-platform | 8050 | 主应用界面 | 所有模式 |
| lihc-api | 8051 | REST API接口 | 开发/生产 |
| postgres | 5432 | 数据库服务 | 生产模式 |
| redis | 6379 | 缓存服务 | 生产模式 |
| nginx | 80/443 | 反向代理 | 生产模式 |
| grafana | 3000 | 监控面板 | 生产模式 |
| prometheus | 9090 | 指标收集 | 生产模式 |
| jupyter | 8888 | Jupyter Lab | 开发模式 |

---

## 🚀 核心功能

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

### 7. 交互式数据可视化

**Dashboard功能**：
- **📱 概览页面**: 项目介绍、快速导航、评分指标说明
- **📤 数据上传**: 支持CSV/Excel/ZIP格式，实时验证
- **📊 分析结果**: 交互式图表、可下载报告
  - Linchpin靶点排序表格
  - 多维度雷达图
  - 得分相关性散点图
  - 网络中心性分布图
- **📈 生存分析**: Kaplan-Meier生存曲线分析
  - 基因表达高低分组
  - Log-rank检验
  - 风险比计算
  - 生存统计指标
- **🕸️ 网络分析**: 分子相互作用网络
  - 3D/2D网络可视化
  - 节点度分布
  - 社区检测
  - 路径分析
- **🌐 语言支持**: 中英文双语界面（i18n国际化）

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

## 📖 使用指南

### 1. 访问应用

**访问地址**: http://localhost:8050

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
├── 📁 docker/                    # Docker配置
│   ├── Dockerfile.minimal       # 最小化镜像
│   ├── Dockerfile.stable        # 稳定版镜像
│   └── Dockerfile.complete      # 完整版镜像
├── 📄 main.py                    # 主程序入口
├── 📄 requirements.txt           # Python依赖
├── 📄 docker-compose.yml         # Docker编排
├── 📄 docker-start.sh            # Docker启动脚本
├── 📄 README.md                  # 项目说明
├── 📄 QUICKSTART.md              # 快速开始指南
└── 📄 FEATURE_SUMMARY.md         # 功能总结
```

---

## ❓ 常见问题

### Docker相关

**Q: Docker构建速度慢？**
```bash
# 使用最小化版本快速测试
docker-compose -f docker-compose.minimal.yml up -d

# 或使用国内镜像源
```

**Q: 端口被占用？**
```bash
# 查看端口占用
lsof -i :8050

# 使用其他端口
docker-compose -f docker-compose.minimal.yml up -d -e PORT=8051
```

### 功能相关

**Q: 生存分析功能不可用？**
- 确保使用的是更新后的镜像（包含lifelines和scipy）
- 检查Docker日志：`docker logs lihc-platform-minimal`

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

## 📞 支持与联系

- 🐛 **问题反馈**: [GitHub Issues](https://github.com/ai-guoke/lihc-platform/issues)
- 📚 **文档中心**: [项目Wiki](https://github.com/ai-guoke/lihc-platform/wiki)
- 💬 **社区讨论**: [GitHub Discussions](https://github.com/ai-guoke/lihc-platform/discussions)

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

*最后更新: 2025年7月25日*  
*版本: v2.1* 🎉  
*项目状态: 积极维护*  

**v2.1 更新内容**：
- 🐳 完善的Docker部署方案（支持3种运行模式）
- 🌐 中英文双语界面支持
- 📊 增强的可视化功能（专业图表分析）
- 🧬 多组学数据整合（RNA-seq, CNV, 突变, 甲基化）
- 🔄 ClosedLoop因果推理分析
- 📈 交互式生存分析（Kaplan-Meier曲线）
- 🧪 75%测试覆盖率的测试套件
- 📚 完整的快速开始指南和API文档