# LIHC Platform Unified API System v2.7
## 统一API端点系统使用指南

### 🚀 系统概述

LIHC平台统一API系统为肝细胞癌精准医疗分析提供了完整的RESTful API接口，整合了7个核心分析模块：

- 🧬 **单细胞RNA-seq分析** - 肿瘤微环境细胞分型与功能分析
- 🎯 **AI生物标志物发现** - 基于机器学习的精准诊断标志物挖掘  
- 💊 **药物组合预测** - 个性化联合用药方案优化
- 🔬 **多组学数据整合** - 基因组、转录组、蛋白组等多维度数据融合
- 👥 **患者分层系统** - 分子亚型识别与风险评估
- 📊 **智能报告生成** - 自动化分析报告与临床决策支持
- ⚡ **实时任务队列** - 高并发异步任务处理

### 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI REST API                        │
├─────────────────────────────────────────────────────────────┤
│  Authentication │  Task Manager │  Error Handling │  CORS  │
├─────────────────────────────────────────────────────────────┤
│              Analysis Module Integration                    │
├─────────────────────────────────────────────────────────────┤
│ Single Cell │ Biomarker │ Drug Combo │ Multi-omics │ ...   │
└─────────────────────────────────────────────────────────────┘
```

### 🔧 快速开始

#### 1. 启动API服务器

```bash
# 方法1: 直接运行
python src/api/unified_api_system.py

# 方法2: 使用uvicorn
uvicorn src.api.unified_api_system:app --host 0.0.0.0 --port 8000 --reload

# 方法3: 生产环境
uvicorn src.api.unified_api_system:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 2. 访问API文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

#### 3. 使用API客户端SDK

```python
from src.api.api_client_sdk import LIHCAPIClient

# 创建客户端
client = LIHCAPIClient(
    base_url="http://localhost:8000",
    api_token="ultrathink_api_token_2025"
)

# 健康检查
health = client.health_check()
print(f"API状态: {health.message}")
```

### 🔐 认证系统

API使用Bearer Token认证方式：

```http
Authorization: Bearer ultrathink_api_token_2025
```

**可用令牌**:
- `ultrathink_api_token_2025` - 管理员权限（所有功能）
- `research_token_2025` - 研究员权限（分析和报告）

### 📋 API端点详解

#### 🏥 健康与信息端点

```http
GET /                    # API基本信息
GET /health              # 健康检查  
GET /stats               # 使用统计
```

#### 🧬 分析端点

##### 1. 单细胞RNA-seq分析

```http
POST /analysis/single-cell
```

**请求示例**:
```python
response = client.analyze_single_cell(
    sample_data={
        "expression_matrix": [[gene1_counts], [gene2_counts], ...],
        "gene_names": ["Gene1", "Gene2", ...],
        "cell_barcodes": ["Cell1", "Cell2", ...]
    },
    clustering_method="leiden",
    quality_control=True
)
```

**返回数据**:
- 细胞类型注释
- 聚类结果
- 差异表达基因
- UMAP/t-SNE可视化

##### 2. AI生物标志物发现

```http
POST /analysis/biomarker
```

**请求示例**:
```python
response = client.discover_biomarkers(
    omics_data={
        "transcriptomics": {"expression_data": [...], "gene_names": [...]},
        "genomics": {"mutation_data": [...], "gene_names": [...]}
    },
    algorithms=["random_forest", "lasso", "xgboost"],
    validation_split=0.2
)
```

**返回数据**:
- 顶级生物标志物列表
- 算法一致性评分
- 验证性能指标
- 临床实用性评估

##### 3. 药物组合预测

```http
POST /analysis/drug-combination
```

**请求示例**:
```python
response = client.predict_drug_combinations(
    patient_profile={
        "molecular_profile": {...},
        "clinical_features": {...},
        "biomarkers": {...}
    },
    available_drugs=["Sorafenib", "Lenvatinib", "Atezolizumab", "Bevacizumab"],
    combination_size=2
)
```

**返回数据**:
- 推荐药物组合
- 协同效应评分
- 预期疗效评估
- 副作用风险评估

##### 4. 多组学数据整合

```http
POST /analysis/multiomics
```

**请求示例**:
```python
response = client.integrate_multiomics(
    omics_data={
        "genomics": {...},
        "transcriptomics": {...},
        "proteomics": {...},
        "metabolomics": {...}
    },
    integration_method="SNF",
    feature_selection=True
)
```

**返回数据**:
- 整合分析结果
- 多组学特征重要性
- 跨组学关联网络
- 整合质量评估

##### 5. 患者分层分析

```http
POST /analysis/stratification
```

**请求示例**:
```python
response = client.stratify_patients(
    patient_data={
        "molecular_data": {...},
        "clinical_data": {...}
    },
    stratification_method="consensus_clustering",
    n_clusters=3
)
```

**返回数据**:
- 患者分层结果
- 分子亚型特征
- 风险评分
- 治疗推荐

#### 📊 报告生成端点

```http
POST /reports/generate
```

**请求示例**:
```python
response = client.generate_report(
    report_type="Comprehensive Analysis Report",
    analysis_results={...},
    output_format="HTML",
    template_customization={
        "custom_branding": {"platform_name": "My LIHC Platform"}
    }
)
```

**支持的报告类型**:
- Clinical Summary Report (临床摘要报告)
- Comprehensive Analysis Report (综合分析报告)
- Biomarker Discovery Report (生物标志物发现报告)
- Treatment Recommendation Report (治疗推荐报告)
- Multi-omics Integration Report (多组学整合报告)
- Patient Stratification Report (患者分层报告)
- Research Publication Draft (研究发表草稿)
- Regulatory Submission Report (监管申报报告)

**输出格式**: PDF, HTML, Word, PowerPoint, JSON, Markdown

#### ⏱️ 任务管理端点

```http
GET /tasks/{task_id}     # 查询任务状态
```

**任务状态**:
- `pending` - 等待处理
- `running` - 正在运行
- `completed` - 已完成
- `failed` - 失败

#### 📁 数据管理端点

```http
POST /data/upload        # 上传数据文件
POST /analysis/batch     # 批量分析
```

### 💻 使用示例

#### 完整分析流程示例

```python
from src.api.api_client_sdk import LIHCAPIClient, create_sample_data, create_patient_profile

# 1. 初始化客户端
client = LIHCAPIClient(base_url="http://localhost:8000")

# 2. 检查API状态
health = client.health_check()
if not health.success:
    print("API服务不可用")
    exit(1)

# 3. 准备数据
sample_data = create_sample_data(n_genes=2000, n_cells=500)
patient_profile = create_patient_profile("P001")

# 4. 执行单细胞分析
print("开始单细胞分析...")
sc_response = client.analyze_single_cell(sample_data)

if sc_response.success:
    # 等待分析完成
    result = client.wait_for_task_completion(sc_response.task_id)
    
    if result.success:
        print(f"单细胞分析完成: {result.data['metadata']}")
        
        # 5. 基于单细胞结果进行药物预测
        drug_response = client.predict_drug_combinations(
            patient_profile=patient_profile,
            available_drugs=["Sorafenib", "Atezolizumab", "Bevacizumab"]
        )
        
        # 等待药物预测完成
        drug_result = client.wait_for_task_completion(drug_response.task_id)
        
        if drug_result.success:
            # 6. 生成综合报告
            report_response = client.generate_report(
                report_type="Comprehensive Analysis Report",
                analysis_results={
                    "single_cell": result.data,
                    "drug_combination": drug_result.data,
                    "n_patients": 1
                }
            )
            
            report_result = client.wait_for_task_completion(report_response.task_id)
            
            if report_result.success:
                print("✅ 完整分析流程成功完成!")
                print(f"报告质量评分: {report_result.data['metadata']['quality_score']}")
```

#### 批量分析示例

```python
# 准备多个分析任务
analyses = [
    {
        "analysis_type": "single_cell",
        "data_source": "sample_1",
        "parameters": {"sample_data": create_sample_data()}
    },
    {
        "analysis_type": "biomarker",
        "data_source": "cohort_1", 
        "parameters": {"omics_data": create_omics_data()}
    }
]

# 提交批量分析
batch_response = client.batch_analysis(analyses)

if batch_response.success:
    print(f"批量分析已提交: {batch_response.data['task_ids']}")
    
    # 监控所有任务
    for task_id in batch_response.data['task_ids']:
        result = client.wait_for_task_completion(task_id)
        print(f"任务 {task_id}: {'成功' if result.success else '失败'}")
```

### 🔧 高级配置

#### 自定义客户端配置

```python
client = LIHCAPIClient(
    base_url="https://your-api-server.com",
    api_token="your_custom_token"
)

# 自定义超时时间
client.session.timeout = 300  # 5分钟超时
```

#### 错误处理

```python
try:
    response = client.analyze_single_cell(sample_data)
    
    if not response.success:
        print(f"分析失败: {response.message}")
        if response.error_code:
            print(f"错误代码: {response.error_code}")
    
except Exception as e:
    print(f"网络错误: {e}")
```

### 📊 性能与限制

#### 性能指标
- **并发请求**: 支持多用户同时访问
- **任务队列**: 异步处理长时间运行的分析
- **批量处理**: 单次最多10个分析任务
- **文件上传**: 支持大文件上传（建议<100MB）

#### 分析时间估算
- 单细胞分析: 5-10分钟 (500-5000细胞)
- 生物标志物发现: 10-15分钟 (1000-10000特征)
- 药物组合预测: 3-7分钟
- 多组学整合: 8-12分钟
- 患者分层: 5-8分钟
- 报告生成: 2-5分钟

### 🛡️ 安全考虑

- **HTTPS**: 生产环境建议使用HTTPS
- **令牌管理**: 定期更换API令牌
- **数据隐私**: 上传的数据仅用于分析，不会永久存储
- **访问日志**: 所有API调用都会记录日志

### 🔍 故障排除

#### 常见问题

1. **连接失败**
   ```python
   # 检查服务器状态
   health = client.health_check()
   ```

2. **认证失败**
   ```python
   # 验证令牌
   client.api_token = "correct_token"
   ```

3. **任务超时**
   ```python
   # 增加超时时间
   result = client.wait_for_task_completion(task_id, max_wait_time=3600)
   ```

4. **数据格式错误**
   ```python
   # 使用提供的数据生成函数
   sample_data = create_sample_data()
   ```

### 📞 技术支持

- **API文档**: http://localhost:8000/docs
- **GitHub**: LIHC Platform Repository
- **邮箱**: support@lihc-platform.com

### 🔄 版本更新

**v2.7.0** (当前版本)
- ✅ 统一API端点系统
- ✅ 7个核心分析模块集成
- ✅ 异步任务处理
- ✅ 智能报告生成
- ✅ 完整的API客户端SDK

---

🎉 **LIHC Platform Unified API System** - 为肝癌精准医疗提供强大的计算支持！