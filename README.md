# LIHC多维度预后分析系统

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

> 🧬 **基于多维度网络分析的肝癌预后分析平台**  
> 通过五维度肿瘤微环境分析发现关键治疗靶点

---

## 📋 目录

- [项目概述](#-项目概述)
- [核心功能](#-核心功能)
- [技术架构](#-技术架构)
- [快速开始](#-快速开始)
- [开发环境搭建](#-开发环境搭建)
- [生产环境部署](#-生产环境部署)
- [详细使用指南](#-详细使用指南)
- [API文档](#-api文档)
- [项目结构](#-项目结构)
- [常见问题](#-常见问题)
- [贡献指南](#-贡献指南)

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

**分析输出**：
- 差异表达基因列表（log2FC, p-value, 调整后p值）
- 生存分析结果（Cox回归、风险比）
- 功能富集分析（GO、KEGG通路）
- 维度间相关性分析

### 2. 跨维度网络分析

**网络构建方法**：
- **相关性网络**: 基于Pearson/Spearman相关系数
- **调控网络**: 转录因子-靶基因关系
- **蛋白互作网络**: 基于STRING数据库
- **通路网络**: KEGG通路间的crosstalk

**网络特征计算**：
- **中心性指标**: 度中心性、介数中心性、接近中心性
- **社区发现**: Louvain算法识别功能模块
- **网络拓扑**: 聚类系数、平均路径长度
- **动态特性**: 网络稳定性、鲁棒性分析

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

**输出结果**：
- Top 20关键靶点排序
- 每个靶点的详细评分
- 可药性评估
- 已知药物信息
- 临床试验状态

### 4. 生存分析系统 🆕

**Kaplan-Meier生存曲线分析**：

| 分析类型 | 分析内容 | 统计方法 | 临床应用 |
|---------|----------|----------|----------|
| 📊 **总生存期 (OS)** | 从诊断到死亡的时间 | Kaplan-Meier + Log-rank | 预后评估 |
| 🔄 **无复发生存期 (RFS)** | 从治疗到复发的时间 | Kaplan-Meier + Log-rank | 治疗效果评估 |
| 🎯 **基因表达分组** | 根据中位数分为高/低表达组 | 中位数分组策略 | 个性化治疗 |
| 📈 **交互式可视化** | 生存曲线图表和统计结果 | Plotly交互图表 | 直观结果展示 |

**功能特色**：
- 🧬 **基因选择**: 支持TP53、MYC、KRAS、EGFR等关键基因
- 📊 **双终点分析**: 同时分析OS和RFS两个生存终点
- 📈 **专业图表**: 生成符合学术发表标准的Kaplan-Meier曲线
- 🔬 **统计检验**: Log-rank检验比较组间差异，显示P值和样本量
- 🏥 **临床解读**: 提供预后价值评估和治疗策略建议

**分组策略**：
```python
# 基于基因表达中位数分组
高表达组 = 表达量 ≥ median(基因表达)
低表达组 = 表达量 < median(基因表达)

# 生存分析输出
Log-rank p-value < 0.05  # 统计显著性
样本量标注: High n=100, Low n=100
```

### 5. 可药性评估系统

**评估维度**：
- **结构可药性**: 蛋白质结构域、活性位点分析
- **已知药物**: FDA批准药物、临床试验药物
- **化合物库**: ChEMBL、DrugBank数据库匹配
- **副作用预测**: 基于药物-靶点-疾病网络

**可药性分级**：
- 💊 **高可药性** (>0.8): 已有多个上市药物
- 🔬 **中等可药性** (0.5-0.8): 有候选化合物或临床试验
- ❓ **低可药性** (<0.5): 需要新药开发
- 👑 **调控靶点**: 转录因子等间接靶点

### 6. 交互式数据可视化 🆕 **完整版**

**Dashboard功能**：
- **概览页面**: 项目介绍、快速导航
- **数据上传**: 支持CSV/Excel格式，实时验证
- **分析结果**: 交互式图表、可下载报告
- **生存分析**: Kaplan-Meier生存曲线分析 🆕
- **专业图表对比**: 多维度可视化分析 🆕
- **网络可视化**: 3D/2D网络图，节点筛选
- **靶点详情**: 基因信息卡片、药物信息
- **比较分析**: 多数据集对比功能

**🆕 新增专业图表功能**：
- **📊 评分对比分析**:
  - 条形图对比: 直观显示Top基因的三个评分对比
  - 雷达图分析: 多维度评分的雷达图展示（Top 5基因）
  - 散点图关联: 预后评分vs网络中心性的关联分析
- **🌳 多维度分析图表**:
  - 饼图分布: 五个生物学维度的基因分布
  - 条形图对比: 各维度基因数量的直观对比
- **🕸️ 网络分析图表**:
  - 中心性分布: 网络中心性评分的分布直方图
  - 网络拓扑图: 基因网络的交互式可视化 🆕

**可视化组件**：
- Plotly交互式图表（条形图、雷达图、散点图、饼图、直方图）
- Cytoscape.js网络图
- DataTable数据表格
- Bootstrap响应式布局
- 专业级图表导出功能

### 7. 语言国际化功能 🆕

**多语言支持**：
- **中文界面**: 完整的中文用户界面
- **英文界面**: 国际化英文界面
- **动态切换**: 实时语言切换，无需刷新页面
- **专业术语保持**: 生物医学专业术语在两种语言中保持一致

**功能特色**:
- 🌐 **一键切换**: 右上角语言切换按钮
- 📝 **全面翻译**: 覆盖所有界面文本和功能标签
- 🔬 **术语一致性**: 基因名、分析方法等专业术语保持原文
- 🎯 **用户友好**: 中英文用户都能流畅使用平台

### 8. 容器化部署支持 🆕

**Docker化部署**：
- **一键部署**: Docker Compose自动化部署
- **环境隔离**: 容器化确保环境一致性
- **数据持久化**: 分析结果和配置文件持久化存储
- **实时更新**: 代码热重载支持开发调试

**部署特色**:
- 🐳 **Docker支持**: 使用Docker容器化部署
- 📦 **依赖隔离**: 避免环境冲突问题
- 🔄 **热重载**: 开发模式下支持代码实时更新
- 💾 **数据持久**: 分析结果和用户数据持久化保存

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

**前端技术**:
```javascript
Dash                     # Python web框架
Plotly.js               # 交互式图表
Bootstrap 5             # UI组件库
HTML5 + CSS3            # 基础技术
```

**数据科学工具**:
```python
# 生物信息学
BioPython               # 生物数据处理
Scanpy                  # 单细胞分析
Anndata                 # 注释数据结构

# 统计分析
Statsmodels             # 统计建模
Lifelines               # 生存分析
Scikit-learn            # 机器学习

# 性能优化
Numba                   # JIT编译
Dask                    # 并行计算
```

---

## ⚡ 快速开始

### 最简启动（5分钟）

```bash
# 1. 克隆项目
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform

# 2. 一键启动（自动安装依赖并运行）
python main.py --setup-demo --run-analysis --dashboard

# 3. 访问Web界面
# 浏览器打开: http://localhost:8050
```

### Docker快速部署

```bash
# 使用Docker一键部署
docker-compose up -d

# 访问应用
open http://localhost:8050

# 🆕 访问增强功能:
# - 📊 Demo Results: 查看专业图表对比分析
# - 📈 Survival Analysis: Kaplan-Meier生存曲线分析
# - 📝 Templates: 下载数据模板
```

---

## 💻 开发环境搭建

### 1. 系统要求

**最低配置**:
- **操作系统**: Linux, macOS, Windows 10+
- **Python**: 3.9+ (推荐 3.10 或 3.11)
- **内存**: 8GB+ (推荐 16GB+)
- **存储**: 10GB 可用空间
- **网络**: 稳定互联网连接（首次下载依赖）

**推荐配置**:
- **CPU**: 4核心以上
- **内存**: 32GB+
- **存储**: SSD，50GB+可用空间
- **GPU**: 可选，用于大规模数据分析加速

### 2. 环境准备

**安装Python**:
```bash
# 使用pyenv管理Python版本（推荐）
curl https://pyenv.run | bash
pyenv install 3.10.12
pyenv local 3.10.12

# 或使用conda
conda create -n lihc-env python=3.10
conda activate lihc-env
```

**安装系统依赖**:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y build-essential python3-dev python3-pip git

# macOS
brew install python@3.10 git

# Windows
# 安装 Python from python.org
# 安装 Git from git-scm.com
```

### 3. 项目安装

**克隆项目**:
```bash
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform
```

**创建虚拟环境**:
```bash
# 方法1: 使用venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 方法2: 使用conda
conda create -n lihc-env python=3.10
conda activate lihc-env
```

**安装依赖**:
```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证安装
python -c "import pandas, numpy, networkx, dash; print('✅ 安装成功')"
```

### 4. 配置文件设置

**创建配置文件**:
```bash
# 复制配置模板
cp config/config.example.py config/config.py

# 编辑配置文件
vim config/config.py
```

**配置示例**:
```python
# config/config.py
import os

# 基础配置
DEBUG = True
SECRET_KEY = 'your-secret-key-here'

# 分析参数
ANALYSIS_CONFIG = {
    'p_value_threshold': 0.05,
    'correlation_threshold': 0.4,
    'survival_threshold_years': 5,
    'min_sample_size': 50
}

# Linchpin评分权重
LINCHPIN_WEIGHTS = {
    'prognostic_score': 0.4,
    'network_hub_score': 0.3,
    'cross_domain_score': 0.2,
    'regulator_score': 0.1
}

# 性能配置
PERFORMANCE_CONFIG = {
    'n_jobs': -1,                    # 并行处理核心数
    'memory_limit': '8GB',           # 内存限制
    'batch_size': 1000,              # 批处理大小
    'cache_enabled': True            # 启用缓存
}

# 数据路径
DATA_PATHS = {
    'raw_data': 'data/raw',
    'processed_data': 'data/processed',
    'results': 'results',
    'cache': 'cache'
}
```

### 5. 开发工具配置

**代码格式化**:
```bash
# 安装开发工具
pip install black isort flake8 mypy pytest pytest-cov

# 配置pre-commit hooks
pip install pre-commit
pre-commit install
```

**IDE配置** (推荐 VS Code):
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.testing.pytestEnabled": true
}
```

---

## 🚀 生产环境部署

### 1. Docker部署（推荐）

**Dockerfile构建**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app
USER app

# 暴露端口
EXPOSE 8050

# 启动命令
CMD ["python", "main.py", "--dashboard", "--host", "0.0.0.0"]
```

**Docker Compose部署**:
```yaml
# docker-compose.yml
version: '3.8'

services:
  lihc-platform:
    build: .
    ports:
      - "8050:8050"
    volumes:
      - ./data:/app/data
      - ./results:/app/results
      - ./config:/app/config
    environment:
      - PYTHONPATH=/app
      - DEBUG=False
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - lihc-platform
    restart: unless-stopped
```

**部署命令**:
```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f lihc-platform

# 停止服务
docker-compose down

# 更新服务
docker-compose pull && docker-compose up -d
```

### 2. 传统服务器部署

**系统准备**:
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y python3 python3-pip python3-venv nginx supervisor

# 创建用户
sudo useradd -m -s /bin/bash lihc
sudo su - lihc
```

**应用部署**:
```bash
# 克隆代码
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform

# 设置虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置环境变量
cat > .env << EOF
PYTHONPATH=/home/lihc/lihc-analysis-platform
DEBUG=False
SECRET_KEY=your-production-secret-key
HOST=0.0.0.0
PORT=8050
EOF
```

**Supervisor配置**:
```ini
# /etc/supervisor/conf.d/lihc-platform.conf
[program:lihc-platform]
command=/home/lihc/lihc-analysis-platform/venv/bin/python main.py --dashboard --host 0.0.0.0
directory=/home/lihc/lihc-analysis-platform
user=lihc
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/lihc-platform.log
environment=PYTHONPATH="/home/lihc/lihc-analysis-platform"
```

**Nginx配置**:
```nginx
# /etc/nginx/sites-available/lihc-platform
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/lihc/lihc-analysis-platform/static/;
        expires 1y;
    }
}
```

**启动服务**:
```bash
# 启动supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start lihc-platform

# 启动nginx
sudo ln -s /etc/nginx/sites-available/lihc-platform /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# 检查状态
sudo supervisorctl status
sudo systemctl status nginx
```

### 3. 云平台部署

**AWS部署**:
```bash
# 使用AWS ECS + ECR
aws ecr create-repository --repository-name lihc-platform
docker build -t lihc-platform .
docker tag lihc-platform:latest 123456789.dkr.ecr.region.amazonaws.com/lihc-platform:latest
docker push 123456789.dkr.ecr.region.amazonaws.com/lihc-platform:latest
```

**Google Cloud部署**:
```bash
# 使用Cloud Run
gcloud run deploy lihc-platform \
  --image gcr.io/PROJECT-ID/lihc-platform \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 📖 详细使用指南

### 1. 系统启动

**开发模式启动**:
```bash
# 完整流程（推荐首次使用）
python main.py --setup-demo --run-analysis --dashboard

# 分步执行
python main.py --setup-demo        # 生成演示数据
python main.py --run-analysis      # 运行分析
python main.py --dashboard         # 启动Web界面

# 调试模式
python main.py --dashboard --debug --port 8050
```

**生产模式启动**:
```bash
# 生产环境启动
python main.py --dashboard --host 0.0.0.0 --port 8050

# 后台运行
nohup python main.py --dashboard --host 0.0.0.0 > app.log 2>&1 &
```

### 2. Web界面导航

**访问地址**: http://localhost:8050

**主要页面**:

1. **📱 概览页面** (`/`)
   - 平台介绍和功能概述
   - 快速开始指南
   - 系统状态监控

2. **📊 演示结果** (`/demo`)
   - TCGA-LIHC完整分析结果
   - Top 20关键靶点展示
   - 交互式网络图

3. **📤 数据上传** (`/upload`)
   - 支持多种数据格式
   - 实时数据验证
   - 分析参数设置

4. **🎯 靶点发现** (`/targets`)
   - Linchpin评分排序
   - 可药性评估结果
   - 靶点详细信息

5. **🕸️ 网络分析** (`/networks`)
   - 交互式分子网络
   - 网络拓扑分析
   - 社区发现结果

6. **📈 生存分析** (`/survival`) 🆕
   - Kaplan-Meier生存曲线
   - Log-rank统计检验
   - 基因表达分组分析
   - 预后价值评估

7. **🌳 多维分析** (`/dimensions`)
   - 五个维度详细结果
   - 维度间相关性
   - 功能富集分析

### 3. 数据上传功能

**支持的数据格式**:

**临床数据** (`clinical_data.csv`):
```csv
sample_id,os_time,os_status,age,gender,stage,grade
TCGA-001,365,1,65,Male,II,G2
TCGA-002,1200,0,58,Female,I,G1
TCGA-003,800,1,72,Male,III,G3
```

**表达数据** (`expression_data.csv`):
```csv
gene_id,TCGA-001,TCGA-002,TCGA-003
TP53,8.25,7.89,9.12
EGFR,6.78,7.45,6.23
VEGFA,5.32,6.01,7.88
MYC,7.12,6.88,8.45
```

**突变数据** (`mutation_data.csv`):
```csv
sample_id,gene_id,mutation_type,amino_acid_change,consequence
TCGA-001,TP53,missense,R175H,pathogenic
TCGA-002,EGFR,nonsense,Q61*,likely_pathogenic
TCGA-003,KRAS,missense,G12D,pathogenic
```

**数据上传步骤**:
1. 访问数据上传页面
2. 选择数据文件（支持拖拽）
3. 设置分析参数
4. 点击"开始分析"
5. 实时查看分析进度
6. 下载分析结果

### 4. 分析结果解读

**Linchpin评分解读**:
- **分数区间**: 0-1 (越高越重要)
- **A级靶点** (>0.8): 强烈推荐，具有强证据支持
- **B级靶点** (0.6-0.8): 值得关注，证据较强
- **C级靶点** (0.4-0.6): 需要进一步验证
- **D级靶点** (<0.4): 证据不足

**可药性标识**:
- 💊 **已有药物**: 有FDA批准或临床试验药物
- 🔬 **候选化合物**: 有先导化合物或前临床研究
- ❓ **难成药**: 暂无直接药物，需要新药开发
- 👑 **间接靶点**: 转录因子等调控性靶点

**网络分析结果**:
- **节点大小**: 反映基因的重要性（度中心性）
- **连接线粗细**: 表示相关性强度
- **颜色分类**: 按生物学维度分组
- **社区结构**: 功能相关的基因集群

### 5. 高级分析功能

**自定义分析参数**:
```bash
# 修改统计阈值
python main.py --run-analysis --p-value 0.01 --correlation 0.5

# 指定分析阶段
python main.py --run-analysis --stage 1  # 仅多维度分析
python main.py --run-analysis --stage 2  # 仅网络分析
python main.py --run-analysis --stage 3  # 仅Linchpin识别

# 性能优化
python main.py --run-analysis --n-jobs 4 --batch-size 500
```

**批量分析**:
```python
# 使用Python API
from src.analysis.batch_analysis import BatchAnalyzer

analyzer = BatchAnalyzer()
results = analyzer.run_batch_analysis(
    datasets=['TCGA-LIHC', 'GEO-GSE12345'],
    methods=['classic', 'network', 'linchpin']
)
```

### 6. 结果导出

**支持的导出格式**:
- 📊 **CSV格式**: 兼容Excel和R语言
- 📈 **图表导出**: PNG/SVG/PDF格式
- 📋 **完整报告**: HTML/PDF格式
- 🔗 **网络文件**: GraphML/GEXF格式（支持Cytoscape）
- 📄 **JSON格式**: 程序化访问

**导出命令**:
```bash
# 导出所有结果
python main.py --export-results --format all

# 导出特定格式
python main.py --export-results --format csv,png

# 导出到指定目录
python main.py --export-results --output-dir /path/to/export
```

---

## 📚 API文档

### REST API接口

**基础信息**:
- **Base URL**: `http://localhost:8050/api/v1`
- **认证方式**: API Key (可选)
- **数据格式**: JSON
- **速率限制**: 100 requests/minute

### 主要接口

**1. 分析任务管理**

```http
# 提交分析任务
POST /api/v1/analysis/submit
Content-Type: application/json

{
  "dataset_name": "my_dataset",
  "data_files": {
    "clinical": "base64_encoded_data",
    "expression": "base64_encoded_data"
  },
  "parameters": {
    "p_value_threshold": 0.05,
    "correlation_threshold": 0.4
  }
}

# 响应
{
  "job_id": "job_12345",
  "status": "submitted",
  "estimated_time": "5 minutes"
}
```

```http
# 获取分析状态
GET /api/v1/analysis/status/{job_id}

# 响应
{
  "job_id": "job_12345",
  "status": "running",
  "progress": 65,
  "current_stage": "network_analysis",
  "estimated_remaining": "2 minutes"
}
```

**2. 结果查询**

```http
# 获取Linchpin结果
GET /api/v1/results/{job_id}/linchpins?top=20&threshold=0.5

# 响应
{
  "job_id": "job_12345",
  "total_genes": 1000,
  "linchpins": [
    {
      "gene_id": "VEGFR2",
      "linchpin_score": 0.809,
      "prognostic_score": 0.85,
      "network_hub_score": 0.92,
      "druggable": true,
      "known_drugs": ["Sunitinib", "Sorafenib"]
    }
  ]
}
```

```http
# 获取网络数据
GET /api/v1/results/{job_id}/network?format=json

# 响应
{
  "nodes": [
    {"id": "TP53", "group": "tumor_cells", "centrality": 0.85},
    {"id": "VEGFR2", "group": "stromal_cells", "centrality": 0.92}
  ],
  "edges": [
    {"source": "TP53", "target": "VEGFR2", "weight": 0.65}
  ]
}
```

**3. 数据管理**

```http
# 获取数据集列表
GET /api/v1/datasets

# 响应
{
  "datasets": [
    {
      "id": "tcga_lihc",
      "name": "TCGA-LIHC",
      "samples": 374,
      "genes": 20000,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Python SDK

**安装SDK**:
```bash
pip install lihc-platform-sdk
```

**使用示例**:
```python
from lihc_platform import LIHCClient

# 初始化客户端
client = LIHCClient(
    base_url="http://localhost:8050",
    api_key="your_api_key"  # 可选
)

# 提交分析任务
job = client.submit_analysis(
    dataset_name="my_analysis",
    clinical_data=clinical_df,
    expression_data=expression_df,
    parameters={
        'p_value_threshold': 0.05,
        'correlation_threshold': 0.4
    }
)

# 等待分析完成
client.wait_for_completion(job.id, timeout=300)

# 获取结果
results = client.get_results(job.id)
linchpins = results.get_linchpins(top=20)
network = results.get_network()

# 可视化结果
results.plot_linchpins()
results.plot_network()
```

**R语言接口**:
```r
# 安装R包
devtools::install_github("your-org/lihc-platform-r")

library(lihcplatform)

# 连接服务
client <- connect_lihc("http://localhost:8050")

# 提交分析
job <- submit_analysis(
  client,
  clinical_data = clinical_df,
  expression_data = expression_df
)

# 获取结果
results <- get_results(client, job$job_id)
linchpins <- get_linchpins(results, top = 20)
```

---

## 📁 项目结构

```
lihc-analysis-platform/
├── 📁 config/                    # 配置文件
│   ├── config.py                 # 主配置文件
│   └── config.example.py         # 配置模板
├── 📁 data/                      # 数据目录
│   ├── raw/                      # 原始数据
│   ├── processed/                # 处理后数据
│   ├── templates/                # 数据模板
│   └── user_uploads/             # 用户上传数据
├── 📁 src/                       # 源代码
│   ├── 📁 analysis/              # 分析算法
│   │   ├── stage1_multidimensional.py    # 多维度分析
│   │   ├── stage2_network.py             # 网络分析
│   │   ├── stage3_linchpin.py            # 关键靶点识别
│   │   ├── survival_analysis.py          # 生存分析 🆕
│   │   └── batch_analysis.py             # 批量分析
│   ├── 📁 api/                   # API接口
│   │   ├── main.py               # API主入口
│   │   ├── auth_endpoints.py     # 认证接口
│   │   └── tasks.py              # 异步任务
│   ├── 📁 data_processing/       # 数据处理
│   │   ├── multi_omics_loader.py # 多组学数据加载
│   │   ├── quality_control.py    # 质量控制
│   │   └── tcga_downloader.py    # TCGA数据下载
│   ├── 📁 utils/                 # 工具函数
│   │   ├── common.py             # 通用工具
│   │   ├── logging_system.py     # 日志系统
│   │   └── enhanced_config.py    # 配置管理
│   ├── 📁 visualization/         # 可视化
│   │   ├── unified_dashboard.py  # 统一仪表板
│   │   ├── dashboard.py          # 基础仪表板
│   │   └── apple_dashboard.py    # Apple风格界面
│   └── run_pipeline.py           # 分析流程主入口
├── 📁 results/                   # 分析结果
│   ├── figures/                  # 图表文件
│   ├── tables/                   # 表格数据
│   ├── networks/                 # 网络数据
│   └── linchpins/               # 关键靶点结果
├── 📁 tests/                     # 测试文件
│   ├── test_analysis.py          # 分析算法测试
│   ├── test_api.py               # API测试
│   └── load_testing.py           # 负载测试
├── 📁 docs/                      # 文档
│   ├── user_guide.md            # 用户指南
│   ├── api_reference.md         # API参考
│   └── development.md           # 开发指南
├── 📁 docker/                    # Docker相关
│   ├── Dockerfile               # Docker镜像定义
│   ├── docker-compose.yml       # 容器编排
│   └── nginx.conf               # Nginx配置
├── 📄 main.py                    # 主程序入口
├── 📄 requirements.txt           # Python依赖
├── 📄 setup.py                   # 包安装脚本
├── 📄 README.md                  # 项目说明（本文件）
└── 📄 LICENSE                    # 开源许可证
```

### 核心模块说明

**1. 分析模块** (`src/analysis/`)
- `stage1_multidimensional.py`: 五维度肿瘤微环境分析
- `stage2_network.py`: 跨维度网络构建和分析
- `stage3_linchpin.py`: 关键靶点识别和评分
- `survival_analysis.py`: Kaplan-Meier生存分析 🆕
- `batch_analysis.py`: 大规模批量分析支持

**2. 数据处理模块** (`src/data_processing/`)
- `multi_omics_loader.py`: 多组学数据加载和整合
- `quality_control.py`: 数据质量控制和预处理
- `tcga_downloader.py`: TCGA数据自动下载

**3. 可视化模块** (`src/visualization/`)
- `unified_dashboard.py`: 主要的Web界面
- `dashboard.py`: 基础仪表板组件
- `apple_dashboard.py`: 现代化UI设计

**4. API模块** (`src/api/`)
- `main.py`: RESTful API主入口
- `auth_endpoints.py`: 用户认证和权限管理
- `tasks.py`: 异步任务处理

---

## ❓ 常见问题

### 安装问题

**Q: 安装依赖时出现错误？**
```bash
# 解决方案1: 升级pip和setuptools
pip install --upgrade pip setuptools wheel

# 解决方案2: 使用conda管理依赖冲突
conda create -n lihc-env python=3.10
conda activate lihc-env
conda install -c conda-forge pandas numpy scipy

# 解决方案3: 安装系统依赖
# Ubuntu/Debian
sudo apt install python3-dev build-essential
# macOS
xcode-select --install
```

**Q: 内存不足错误？**
```bash
# 调整批处理大小
export BATCH_SIZE=500
export N_JOBS=2

# 或在配置文件中设置
# config/config.py
PERFORMANCE_CONFIG = {
    'batch_size': 500,
    'n_jobs': 2,
    'memory_limit': '4GB'
}
```

### 运行问题

**Q: 分析过程中断？**
```bash
# 查看日志文件
tail -f logs/LIHC_Platform_$(date +%Y%m%d).log

# 重新运行特定阶段
python main.py --run-analysis --stage 2 --force-restart

# 清理缓存
rm -rf cache/* && python main.py --run-analysis
```

**Q: Web界面无法访问？**
```bash
# 检查端口占用
lsof -i :8050
netstat -tulpn | grep 8050

# 使用不同端口
python main.py --dashboard --port 8051

# 检查防火墙设置
sudo ufw allow 8050
```

**Q: 分析结果不符合预期？**
```bash
# 检查输入数据格式
python main.py --validate-data --data-dir data/

# 使用严格的统计阈值
python main.py --run-analysis --p-value 0.01 --correlation 0.6

# 查看详细的分析报告
python main.py --run-analysis --verbose --generate-report
```

### 性能优化

**Q: 分析速度太慢？**
```bash
# 启用并行处理
export OMP_NUM_THREADS=4
python main.py --run-analysis --n-jobs 4

# 使用GPU加速（如果可用）
pip install cupy-cuda11x  # 根据CUDA版本选择
export CUDA_VISIBLE_DEVICES=0

# 减少数据量进行测试
python main.py --run-analysis --max-genes 1000 --max-samples 100
```

**Q: 内存使用过高？**
```python
# 在配置文件中调整内存设置
PERFORMANCE_CONFIG = {
    'memory_limit': '8GB',
    'enable_disk_cache': True,
    'lazy_loading': True,
    'chunk_size': 1000
}
```

### 数据问题

**Q: 数据格式错误？**
```bash
# 查看数据模板
ls data/templates/

# 验证数据格式
python main.py --validate-data --input-file your_data.csv

# 使用数据转换工具
python -m src.utils.data_converter \
  --input your_data.csv \
  --output formatted_data.csv \
  --format lihc
```

**Q: 缺失数据处理？**
```python
# 在分析参数中设置缺失值处理策略
ANALYSIS_CONFIG = {
    'missing_value_strategy': 'drop',  # 'drop', 'mean', 'median'
    'min_completeness': 0.8,           # 最小完整度要求
    'imputation_method': 'knn'         # 插值方法
}
```

---

## 🤝 贡献指南

### 开发工作流

1. **Fork项目** 到你的GitHub账户
2. **创建功能分支**: `git checkout -b feature/amazing-feature`
3. **编写代码** 并确保通过所有测试
4. **提交更改**: `git commit -m 'Add amazing feature'`
5. **推送分支**: `git push origin feature/amazing-feature`
6. **创建Pull Request**

### 代码规范

**Python代码规范**:
```bash
# 格式化代码
black src/ tests/
isort src/ tests/

# 代码检查
flake8 src/ tests/ --max-line-length=88
mypy src/

# 运行测试
pytest tests/ --cov=src
```

**提交信息规范**:
```
<type>(<scope>): <description>

<body>

<footer>
```

**提交类型**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建工具或辅助工具的变动

**示例**:
```
feat(analysis): add multi-omics integration algorithm

- Implement CNV-expression correlation analysis
- Add methylation-expression regulation detection
- Support batch processing for large datasets

Closes #123
```

### 测试要求

**运行测试**:
```bash
# 单元测试
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# 性能测试
pytest tests/performance/ -v

# 覆盖率测试
pytest tests/ --cov=src --cov-report=html
```

**测试覆盖率要求**: >85%

**添加新测试**:
```python
# tests/test_new_feature.py
import pytest
from src.analysis.new_feature import NewAnalyzer

class TestNewAnalyzer:
    @pytest.fixture
    def sample_data(self):
        """准备测试数据"""
        return {
            'expression': mock_expression_data(),
            'clinical': mock_clinical_data()
        }
    
    def test_new_analyzer_basic(self, sample_data):
        """测试基本功能"""
        analyzer = NewAnalyzer()
        result = analyzer.analyze(sample_data)
        
        assert result is not None
        assert 'linchpin_scores' in result
        assert len(result['linchpin_scores']) > 0
    
    def test_new_analyzer_edge_cases(self):
        """测试边界情况"""
        analyzer = NewAnalyzer()
        
        # 测试空数据
        with pytest.raises(ValueError):
            analyzer.analyze({})
        
        # 测试无效参数
        with pytest.raises(ValueError):
            analyzer.analyze(sample_data, p_threshold=-1)
```

### 文档贡献

**文档结构**:
```
docs/
├── user_guide/          # 用户指南
├── developer_guide/     # 开发者指南
├── api_reference/       # API参考
└── tutorials/           # 教程
```

**编写文档**:
```markdown
# 标题

## 概述
简要说明功能或概念

## 示例
```python
# 代码示例
from src.analysis import NewAnalyzer
analyzer = NewAnalyzer()
result = analyzer.analyze(data)
```

## 参数说明
- `param1` (str): 参数说明
- `param2` (int, optional): 可选参数，默认为0

## 返回值
返回包含分析结果的字典

## 注意事项
使用时需要注意的要点
```

---

## 📊 项目状态与发展

### 当前状态

- ✅ **核心分析引擎**: 100% 完成
- ✅ **Web可视化界面**: 100% 完成  
- ✅ **真实数据集成**: 100% 完成
- ✅ **Docker化部署**: 100% 完成
- ✅ **生存分析功能**: 100% 完成 🆕
- ✅ **专业图表对比**: 100% 完成 🆕
- ✅ **网络分析图表**: 100% 完成 🆕
- ✅ **语言国际化**: 100% 完成 🆕
- ✅ **数据准确性验证**: 100% 完成 🆕
- 🔄 **多组学整合**: 开发中 (70%)
- 🔄 **API接口**: 开发中 (60%)
- 🔄 **机器学习模块**: 规划中

### 性能指标

| 指标 | 当前值 | 目标值 | 状态 |
|------|--------|--------|------|
| 分析速度 | <5分钟 | <10分钟 | ✅ 优秀 |
| 内存使用 | 4-8GB | <16GB | ✅ 良好 |
| 界面响应 | <2秒 | <3秒 | ✅ 优秀 |
| 准确性 | >90% | >85% | ✅ 优秀 |
| 稳定性 | 稳定运行 | 稳定运行 | ✅ 优秀 |
| 可视化丰富度 | 高 | 中等 | ✅ 优秀 🆕 |

### 发展路线图

**2025 Q1**:
- [ ] 完成多组学数据整合模块
- [ ] 发布v2.0版本
- [ ] 添加机器学习预测功能

**2025 Q2**:
- [ ] 支持单细胞数据分析
- [ ] 云端部署解决方案
- [ ] 移动端适配

**2025 Q3**:
- [ ] 人工智能辅助诊断
- [ ] 联邦学习支持
- [ ] 国际多中心验证

---

## 📞 支持与联系

### 技术支持

- 🐛 **问题反馈**: [GitHub Issues](https://github.com/ai-guoke/lihc-platform/issues)
- 📚 **文档中心**: [项目文档](https://docs.lihc-platform.org)
- 💬 **社区讨论**: [GitHub Discussions](https://github.com/ai-guoke/lihc-platform/discussions)
- 📧 **邮件支持**: support@lihc-platform.org

### 快速获取帮助

**创建Issue模板**:
```markdown
**问题类型**: Bug报告 / 功能请求 / 使用疑问

**环境信息**:
- 操作系统: 
- Python版本: 
- 项目版本: 

**问题描述**:
详细描述遇到的问题

**重现步骤**:
1. 步骤一
2. 步骤二
3. 步骤三

**期望结果**:
描述期望的行为

**实际结果**:
描述实际发生的情况

**相关日志**:
```bash
# 粘贴相关的错误日志
```

**其他信息**:
任何可能有帮助的附加信息
```

### 社区资源

- 📖 **用户手册**: 详细的使用说明和教程
- 🎥 **视频教程**: YouTube频道和B站教学视频
- 📊 **示例数据**: 公开的测试数据集
- 🔬 **研究论文**: 相关的学术发表和预印本

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
  version={v1.0},
  note={An open-source platform for multi-dimensional tumor microenvironment analysis}
}
```

---

## 🎉 致谢

感谢所有为本项目做出贡献的研究者、开发者和用户：

### 数据提供者
- 🙏 **TCGA研究网络** - 提供高质量的公共肿瘤基因组数据
- 🔬 **GEO数据库** - 基因表达数据资源
- 📊 **STRING数据库** - 蛋白质相互作用网络数据

### 开源社区
- 🐍 **Python生态系统** - Pandas, NumPy, SciPy, Matplotlib等
- 📈 **Plotly团队** - 优秀的交互式可视化库
- 🕸️ **NetworkX开发者** - 网络分析工具
- 🚀 **Dash框架** - Web应用开发框架

### 学术支持
- 🏥 **临床合作伙伴** - 提供临床数据和验证
- 🎓 **学术机构** - 研究指导和理论支持
- 📝 **同行评议者** - 宝贵的反馈和建议

---

## 🚀 开始您的肿瘤靶点发现之旅

```bash
# 一键启动，开始探索
git clone https://github.com/ai-guoke/lihc-platform.git
cd lihc-platform
python main.py --setup-demo --run-analysis --dashboard

# 在浏览器中访问: http://localhost:8050
# 🎯 发现下一个突破性的肿瘤治疗靶点！
```

---

*最后更新: 2025年7月24日*  
*版本: v1.3 - 完善网络分析图表和多语言支持*  
*项目状态: 开源可用*  
*维护状态: 积极维护*