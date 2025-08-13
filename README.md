# LIHC Analysis Platform 
# 肝癌多维度预后分析平台

<div align="center">
  
![Version](https://img.shields.io/badge/version-2.6-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Docker](https://img.shields.io/badge/docker-supported-blue)
![UI](https://img.shields.io/badge/UI-Apple%20Glassmorphism-purple)

**基于多维度网络分析的肝癌精准医学平台**

[English](#english) | [中文](#chinese)

</div>

---

<a name="chinese"></a>
## 🌟 项目简介

LIHC Analysis Platform 是一个专注于肝细胞癌(LIHC)的综合性生物信息学分析平台。该平台整合多组学数据，通过创新的五维度分析框架和AI算法，为肝癌研究提供全方位的数据分析和可视化解决方案。

### 核心特性

- 🧬 **多组学数据整合** - 支持基因组、转录组、蛋白组等多层次数据
- 🎯 **五维度分析框架** - 肿瘤、免疫、基质、ECM、细胞因子综合评估
- 🤖 **AI驱动的分析** - 机器学习算法识别关键生物标志物
- 📊 **交互式可视化** - 基于Plotly的动态图表和3D可视化
- 🎨 **现代化UI设计** - Apple风格磨砂玻璃界面，优雅简洁
- 🚀 **高性能计算** - 支持并行处理和批量分析

### 最新更新 (v2.6)

- ✨ Apple风格磨砂玻璃UI全面升级
- 📊 多数据集切换功能
- 🔧 Docker部署优化
- 🎯 性能提升30%

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 8GB+ RAM
- 现代浏览器 (Chrome/Edge/Safari)

### 安装步骤

#### 方式一：直接运行（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动平台
python main.py --dashboard

# 4. 访问界面
# 打开浏览器访问: http://localhost:8050
```

#### 方式二：Docker部署

```bash
# 1. 构建镜像
docker build -t lihc-platform:latest .

# 2. 运行容器
docker run -d \
  --name lihc-platform \
  -p 8050:8050 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  lihc-platform:latest

# 3. 查看日志
docker logs -f lihc-platform
```

#### 方式三：Docker Compose（生产环境）

```bash
# 启动所有服务
docker-compose up -d

# 停止服务
docker-compose down
```

---

## 📚 功能模块

### 1. 数据管理
- **数据上传**: 支持CSV、Excel、TSV格式
- **数据集管理**: 多数据集切换和版本控制
- **数据预处理**: 自动质控和标准化

### 2. 基础分析
- **多维度分析**: 五个生物学维度综合评估
- **网络分析**: 基因调控网络和蛋白互作网络
- **生存分析**: Kaplan-Meier和Cox回归分析
- **Linchpin靶点**: 识别关键治疗靶点

### 3. 高级分析
- **多组学整合**: 整合多层次组学数据
- **AI生物标志物**: 机器学习识别预后标志物
- **药物响应预测**: 预测药物敏感性
- **单细胞分析**: 单细胞转录组数据分析

### 4. 精准医学
- **免疫微环境**: 免疫浸润和检查点分析
- **分子分型**: 肿瘤亚型识别
- **代谢分析**: 代谢通路活性评估
- **药物组合**: 协同药物组合预测

---

## 💻 使用指南

### 基本工作流程

1. **数据准备**
   ```python
   # 上传表达数据
   expression_file = "data/expression_matrix.csv"
   clinical_file = "data/clinical_data.csv"
   ```

2. **运行分析**
   ```python
   from src.analysis.five_dimension_prognostic import FiveDimensionPrognosticAnalyzer
   
   analyzer = FiveDimensionPrognosticAnalyzer()
   results = analyzer.analyze(expression_data, clinical_data)
   ```

3. **查看结果**
   - 访问 http://localhost:8050
   - 导航到相应分析模块
   - 交互式探索结果

### 命令行参数

```bash
# 启动完整平台
python main.py --dashboard --port 8050

# 仅运行分析
python main.py --analyze --input data.csv --output results/

# 批量处理
python main.py --batch --config batch_config.json

# 生成报告
python main.py --report --format pdf --output report.pdf
```

---

## 🎨 UI特性

### Apple风格磨砂玻璃设计

- **磨砂玻璃效果**: 真实的backdrop-filter模糊
- **渐变配色**: 柔和的紫蓝渐变主题
- **动画效果**: 流畅的过渡和交互动画
- **响应式设计**: 自适应各种屏幕尺寸

### 界面预览

```
┌─────────────────────────────────────┐
│  🧬 LIHC Analysis Platform          │
├─────────────────────────────────────┤
│  ┌──────┐  ┌─────────────────────┐  │
│  │ 导航 │  │    主要内容区域     │  │
│  │      │  │                     │  │
│  │ • 分析│  │   📊 交互式图表    │  │
│  │ • 数据│  │   📈 动态可视化    │  │
│  │ • 结果│  │   📋 数据表格      │  │
│  └──────┘  └─────────────────────┘  │
└─────────────────────────────────────┘
```

---

## 📊 数据格式

### 表达数据格式

```csv
Gene,Sample1,Sample2,Sample3
TP53,10.5,8.3,12.1
EGFR,5.2,6.8,4.9
...
```

### 临床数据格式

```csv
Sample,OS_time,OS_status,Age,Stage
Sample1,365,1,65,III
Sample2,730,0,58,II
...
```

### 输出结果格式

结果保存在 `results/` 目录：
- `analysis_results.csv` - 分析结果表格
- `figures/` - 可视化图片
- `report.html` - 交互式报告

---

## 🔧 配置说明

### 系统配置

创建 `config/config.yaml` 文件：

```yaml
# 服务器配置
server:
  host: 0.0.0.0
  port: 8050
  debug: false

# 数据库配置
database:
  type: sqlite
  path: data/lihc.db

# 分析参数
analysis:
  n_jobs: 4
  cache: true
  timeout: 3600

# UI配置
ui:
  theme: glassmorphism
  language: zh
```

### 环境变量

```bash
# 设置环境变量
export LIHC_DATA_PATH=/path/to/data
export LIHC_RESULTS_PATH=/path/to/results
export LIHC_CACHE_ENABLED=true
```

---

## 🐳 Docker部署详解

### Dockerfile配置

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8050
CMD ["python", "main.py", "--dashboard"]
```

### Docker Compose配置

```yaml
version: '3.8'
services:
  lihc-platform:
    build: .
    ports:
      - "8050:8050"
    volumes:
      - ./data:/app/data
      - ./results:/app/results
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

### 生产环境部署

1. **使用Nginx反向代理**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. **使用Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:8050 main:server
```

---

## 📈 性能优化

### 推荐配置

- **开发环境**: 4核CPU, 8GB RAM
- **生产环境**: 8核CPU, 16GB RAM
- **大数据处理**: 16核CPU, 32GB RAM

### 优化建议

1. **启用缓存**
   ```python
   app.config['CACHE_TYPE'] = 'redis'
   ```

2. **并行处理**
   ```python
   from multiprocessing import Pool
   with Pool(processes=4) as pool:
       results = pool.map(analyze, datasets)
   ```

3. **数据库索引**
   ```sql
   CREATE INDEX idx_gene ON expression(gene_id);
   CREATE INDEX idx_sample ON clinical(sample_id);
   ```

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- 使用 Black 格式化 Python 代码
- 遵循 PEP 8 编码规范
- 添加适当的注释和文档
- 编写单元测试

---

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- 中国科学院大学杭州高等研究院
- TCGA数据库提供数据支持
- 所有贡献者和用户

---

## 📧 联系方式

- **项目主页**: https://github.com/ai-guoke/lihc-analysis-platform
- **问题反馈**: [GitHub Issues](https://github.com/ai-guoke/lihc-analysis-platform/issues)
- **邮箱**: support@lihc-platform.com

---

<a name="english"></a>
## 🌟 Project Overview (English)

LIHC Analysis Platform is a comprehensive bioinformatics analysis platform focused on Hepatocellular Carcinoma (LIHC). It integrates multi-omics data and provides comprehensive data analysis and visualization solutions for liver cancer research through innovative five-dimensional analysis framework and AI algorithms.

### Quick Start

```bash
# Clone repository
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform

# Install dependencies
pip install -r requirements.txt

# Start platform
python main.py --dashboard

# Access UI at http://localhost:8050
```

### Docker Deployment

```bash
# Build image
docker build -t lihc-platform:latest .

# Run container
docker run -d -p 8050:8050 lihc-platform:latest
```

For detailed documentation, please refer to the Chinese section above.

---

<div align="center">
  <b>LIHC Analysis Platform v2.6</b><br>
  Made with ❤️ by UCAS Hangzhou Institute for Advanced Study
</div>