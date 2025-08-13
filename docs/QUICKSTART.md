# 🚀 LIHC Platform 快速开始指南

本指南将帮助您在5分钟内快速启动和使用 LIHC Analysis Platform。

## 📋 快速导航

- [1分钟快速体验](#1分钟快速体验)
- [3分钟本地部署](#3分钟本地部署)
- [5分钟完整安装](#5分钟完整安装)
- [第一次使用](#第一次使用)
- [示例分析流程](#示例分析流程)
- [常用功能速查](#常用功能速查)

---

## 1分钟快速体验

### 使用Docker一键启动

```bash
# 拉取并运行预构建镜像
docker run -d -p 8050:8050 --name lihc-quick ghcr.io/ai-guoke/lihc-platform:latest

# 打开浏览器访问
open http://localhost:8050

# 使用演示数据体验
# 用户名: demo
# 密码: demo123
```

🎉 **恭喜！平台已经运行，您可以立即开始探索。**

---

## 3分钟本地部署

### 步骤1：下载项目

```bash
# 克隆项目
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform
```

### 步骤2：安装依赖

```bash
# 使用pip安装（推荐使用虚拟环境）
pip install -r requirements.txt
```

### 步骤3：启动平台

```bash
# 启动仪表板
python main.py --dashboard

# 访问地址: http://localhost:8050
```

---

## 5分钟完整安装

### 前置准备

```bash
# 1. 检查Python版本（需要3.8+）
python --version

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# 3. 升级pip
pip install --upgrade pip
```

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化配置
cp .env.example .env
# 编辑 .env 文件设置必要的环境变量

# 4. 下载演示数据（可选）
python scripts/download_demo_data.py

# 5. 启动平台
python main.py --dashboard --port 8050
```

### 验证安装

```bash
# 运行测试
python -m pytest tests/

# 检查服务状态
curl http://localhost:8050/health
```

---

## 第一次使用

### 1. 访问平台

打开浏览器访问: http://localhost:8050

### 2. 界面介绍

```
┌─────────────────────────────────────────────┐
│  LIHC Analysis Platform                    │
├─────────────────────────────────────────────┤
│  ┌─────────┐  ┌──────────────────────────┐ │
│  │ 侧边栏  │  │      主要功能区域        │ │
│  │         │  │                          │ │
│  │ • 数据  │  │   [上传数据区域]         │ │
│  │ • 分析  │  │   [参数设置]             │ │
│  │ • 结果  │  │   [运行按钮]             │ │
│  └─────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### 3. 功能导航

- **📊 平台概览**: 查看系统状态和统计信息
- **📁 数据管理**: 上传和管理数据文件
- **🔬 分析模块**: 
  - 多维度分析
  - 网络分析
  - 生存分析
  - Linchpin靶点
- **📈 结果查看**: 查看分析结果和下载报告

---

## 示例分析流程

### 快速示例：运行五维度分析

#### 1. 准备数据

使用提供的演示数据或准备您自己的数据：

```bash
# 表达数据格式 (expression.csv)
Gene,Sample1,Sample2,Sample3
TP53,10.5,8.3,12.1
EGFR,5.2,6.8,4.9

# 临床数据格式 (clinical.csv)
Sample,OS.time,OS,Age,Stage
Sample1,365,1,65,III
Sample2,730,0,58,II
```

#### 2. 上传数据

1. 点击左侧菜单 **"数据管理"**
2. 点击 **"上传数据"** 按钮
3. 选择表达数据文件
4. 选择临床数据文件
5. 点击 **"确认上传"**

#### 3. 运行分析

1. 点击左侧菜单 **"五维度预后分析"**
2. 选择已上传的数据集
3. 设置分析参数（可保持默认）
4. 点击 **"开始分析"** 按钮

#### 4. 查看结果

分析完成后，您将看到：
- 五个维度的得分雷达图
- 综合预后评分
- 生存曲线
- 关键基因列表

#### 5. 下载报告

点击 **"下载报告"** 按钮获取：
- PDF分析报告
- Excel数据表格
- 高清图片

---

## 常用功能速查

### 数据操作

```python
# 命令行上传数据
python main.py --upload --expression expr.csv --clinical clin.csv

# 批量上传
python main.py --batch-upload --dir ./data/batch/

# 数据验证
python main.py --validate --input data.csv
```

### 分析任务

```python
# 运行特定分析
python main.py --analyze survival --data dataset1

# 运行所有分析
python main.py --analyze all --data dataset1

# 使用自定义参数
python main.py --analyze network --config custom_params.yaml
```

### 结果管理

```python
# 导出结果
python main.py --export --format pdf --output results.pdf

# 生成报告
python main.py --report --data dataset1 --output report.html

# 清理旧结果
python main.py --clean --older-than 30
```

---

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+U` | 上传数据 |
| `Ctrl+R` | 运行分析 |
| `Ctrl+S` | 保存结果 |
| `Ctrl+E` | 导出报告 |
| `Ctrl+H` | 显示帮助 |

---

## 常见问题

### Q1: 如何使用自己的数据？

**A:** 确保您的数据符合以下格式：
- 表达矩阵：行为基因，列为样本
- 临床数据：必须包含 `OS.time` 和 `OS` 列
- 支持格式：CSV, TSV, Excel

### Q2: 分析需要多长时间？

**A:** 
- 小数据集（<100样本）：1-2分钟
- 中等数据集（100-500样本）：5-10分钟
- 大数据集（>500样本）：15-30分钟

### Q3: 如何提高分析速度？

**A:** 
1. 增加并行工作进程：`--workers 8`
2. 启用GPU加速：`--gpu`
3. 使用缓存：`--cache`

### Q4: 出现错误怎么办？

**A:** 
1. 查看日志：`logs/app.log`
2. 运行诊断：`python main.py --diagnose`
3. 提交Issue：[GitHub Issues](https://github.com/ai-guoke/lihc-analysis-platform/issues)

---

## 进阶使用

### 使用API进行编程访问

```python
from lihc_platform import Client

# 连接到平台
client = Client("http://localhost:8050")

# 上传数据
dataset_id = client.upload_data(
    expression="expr.csv",
    clinical="clin.csv"
)

# 运行分析
job_id = client.run_analysis(
    dataset_id=dataset_id,
    analysis_type="five_dimension"
)

# 获取结果
results = client.get_results(job_id)
print(results.summary)
```

### 自定义分析流程

```python
from src.analysis import Pipeline

# 创建分析管道
pipeline = Pipeline()
pipeline.add_step("normalize", method="quantile")
pipeline.add_step("feature_selection", n_features=100)
pipeline.add_step("survival_analysis", method="cox")

# 运行管道
results = pipeline.run(data)
```

---

## 获取帮助

### 资源链接

- 📚 [完整文档](https://docs.lihc-platform.com)
- 🎥 [视频教程](https://www.youtube.com/lihc-platform)
- 💬 [社区论坛](https://forum.lihc-platform.com)
- 📧 [技术支持](mailto:support@lihc-platform.com)

### 命令帮助

```bash
# 查看所有命令
python main.py --help

# 查看特定命令帮助
python main.py --analyze --help

# 查看版本信息
python main.py --version
```

---

<div align="center">

**🎉 现在您已经准备好开始使用 LIHC Analysis Platform 了！**

[返回主页](../README.md) | [部署指南](DEPLOYMENT.md) | [开发文档](DEVELOPMENT.md)

</div>