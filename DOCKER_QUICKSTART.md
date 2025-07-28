# 🐳 ultrathink v2.7 Docker 快速启动指南

## 🚀 一键启动

### 最简单的启动方式

```bash
# 1. 给脚本执行权限
chmod +x docker-ultrathink.sh

# 2. 启动平台（最小化模式）
./docker-ultrathink.sh start --minimal
```

**就这么简单！** 🎉

启动后访问：
- **主面板**: http://localhost:8050
- **API文档**: http://localhost:8000/docs

---

## 📋 系统要求

- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **内存**: 最少4GB，推荐8GB+
- **CPU**: 最少2核，推荐4核+
- **磁盘**: 最少5GB可用空间

---

## 🎯 启动模式

### 1. 最小化模式（推荐新手）
```bash
./docker-ultrathink.sh start --minimal
```
**包含**: Dashboard + API + Redis  
**内存使用**: ~2GB

### 2. 完整模式
```bash
./docker-ultrathink.sh start --full
```
**包含**: 所有服务（数据库、监控等）  
**内存使用**: ~4GB

### 3. 仅API服务
```bash
./docker-ultrathink.sh start --api-only
```
**包含**: API + Redis  
**内存使用**: ~1GB

---

## 🛠️ 常用命令

```bash
# 查看服务状态
./docker-ultrathink.sh status

# 查看日志
./docker-ultrathink.sh logs

# 停止服务
./docker-ultrathink.sh stop

# 重启服务
./docker-ultrathink.sh restart

# 运行测试
./docker-ultrathink.sh test

# 进入容器
./docker-ultrathink.sh shell dashboard
./docker-ultrathink.sh shell api

# 查看帮助
./docker-ultrathink.sh help
```

---

## 🌐 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **主面板** | http://localhost:8050 | 分析界面 |
| **API服务** | http://localhost:8000 | REST API |
| **API文档** | http://localhost:8000/docs | Swagger UI |
| **API ReDoc** | http://localhost:8000/redoc | 文档 |
| **Redis** | localhost:6379 | 缓存服务 |
| **PostgreSQL** | localhost:5432 | 数据库（完整模式） |
| **Grafana** | http://localhost:3000 | 监控（完整模式） |

---

## 🔑 API认证

### 认证令牌

在请求头中添加：
```
Authorization: Bearer ultrathink_api_token_2025
```

**可用令牌**:
- `ultrathink_api_token_2025` - 管理员权限
- `research_token_2025` - 研究员权限

### Python SDK示例

```python
from src.api.api_client_sdk import LIHCAPIClient

client = LIHCAPIClient(
    base_url="http://localhost:8000",
    api_token="ultrathink_api_token_2025"
)

# 健康检查
health = client.health_check()
print(health.message)
```

---

## 🧪 快速测试

### 1. 系统健康检查
```bash
curl http://localhost:8050/        # Dashboard
curl http://localhost:8000/health  # API
```

### 2. API测试
```bash
curl -H "Authorization: Bearer ultrathink_api_token_2025" \
     http://localhost:8000/
```

### 3. 运行完整测试套件
```bash
./docker-ultrathink.sh test
```

---

## 📊 性能监控

### 查看资源使用
```bash
./docker-ultrathink.sh status
```

### 查看实时日志
```bash
./docker-ultrathink.sh logs        # 所有服务
./docker-ultrathink.sh logs api    # 仅API服务
```

---

## 🔧 故障排除

### 常见问题

#### 1. 端口冲突
```bash
# 检查端口占用
lsof -i :8050
lsof -i :8000

# 或修改 docker-compose.yml 中的端口映射
```

#### 2. 内存不足
```bash
# 使用最小化模式
./docker-ultrathink.sh start --minimal

# 或增加Docker内存限制
```

#### 3. 权限问题
```bash
# 给脚本执行权限
chmod +x docker-ultrathink.sh

# 检查Docker权限
docker info
```

#### 4. 服务无法启动
```bash
# 查看详细日志
./docker-ultrathink.sh logs

# 重新构建镜像
./docker-ultrathink.sh build
./docker-ultrathink.sh restart
```

### 日志位置
- **容器日志**: `./docker-ultrathink.sh logs [service]`
- **应用日志**: `./logs/` 目录
- **数据文件**: `./data/` 目录

---

## 💾 数据管理

### 备份数据
```bash
./docker-ultrathink.sh backup
```

### 恢复数据
```bash
./docker-ultrathink.sh restore backups/20250127_143000
```

### 清理资源
```bash
./docker-ultrathink.sh clean
```

---

## 🔄 更新平台

```bash
# 更新到最新版本
./docker-ultrathink.sh update
```

---

## 🎯 核心功能演示

### 1. 单细胞分析API调用

```python
import requests

response = requests.post(
    "http://localhost:8000/analysis/single-cell",
    headers={"Authorization": "Bearer ultrathink_api_token_2025"},
    json={
        "sample_data": {
            "expression_matrix": [[1,2,3],[4,5,6]],
            "gene_names": ["Gene1", "Gene2"],
            "cell_barcodes": ["Cell1", "Cell2", "Cell3"]
        },
        "clustering_method": "leiden"
    }
)

print(f"任务ID: {response.json()['task_id']}")
```

### 2. 生物标志物发现

```python
response = requests.post(
    "http://localhost:8000/analysis/biomarker",
    headers={"Authorization": "Bearer ultrathink_api_token_2025"},
    json={
        "omics_data": {
            "transcriptomics": {
                "expression_data": [[1,2],[3,4]],
                "gene_names": ["GENE1", "GENE2"]
            }
        },
        "algorithms": ["random_forest", "lasso"]
    }
)
```

### 3. 报告生成

```python
response = requests.post(
    "http://localhost:8000/reports/generate",
    headers={"Authorization": "Bearer ultrathink_api_token_2025"},
    json={
        "report_type": "Clinical Summary Report",
        "analysis_results": {"n_patients": 100},
        "output_format": "HTML"
    }
)
```

---

## 📞 获取帮助

### 命令行帮助
```bash
./docker-ultrathink.sh help
```

### 在线文档
- **API文档**: http://localhost:8000/docs
- **使用指南**: ./API_USAGE_GUIDE.md

### 系统信息
```bash
./docker-ultrathink.sh status    # 服务状态
docker --version                # Docker版本
docker-compose --version        # Compose版本
```

---

## 🎉 成功启动标志

看到以下信息说明启动成功：

```
✓ 服务启动完成

═══════════════════════════════════════════════════════════════
                   ultrathink v2.7.0 访问信息
═══════════════════════════════════════════════════════════════

🖥️  主要服务:
  Dashboard:     http://localhost:8050
  API Server:    http://localhost:8000
  API 文档:      http://localhost:8000/docs
```

**现在您可以开始使用ultrathink v2.7进行肝癌精准医疗分析了！** 🚀

---

*ultrathink v2.7 - 肝细胞癌精准医疗分析平台*