# 🐳 ultrathink v2.7 Docker完整部署指南

## 📋 目录
1. [系统要求](#系统要求)
2. [快速开始](#快速开始)
3. [完整部署步骤](#完整部署步骤)
4. [服务架构](#服务架构)
5. [功能验证](#功能验证)
6. [常见问题](#常见问题)
7. [高级配置](#高级配置)

---

## 🖥️ 系统要求

### 最低配置
- **操作系统**: macOS, Linux, Windows 10/11 (with WSL2)
- **CPU**: 4核心
- **内存**: 8GB RAM
- **磁盘**: 10GB可用空间
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### 推荐配置
- **CPU**: 8核心或更多
- **内存**: 16GB RAM或更多
- **磁盘**: 20GB可用空间

---

## 🚀 快速开始

### 一键启动完整版

```bash
# 1. 克隆或下载项目
cd /path/to/mrna2

# 2. 运行完整版启动脚本
chmod +x run-ultrathink-full.sh
./run-ultrathink-full.sh
```

**就这么简单！** 等待约2-3分钟后，访问：
- 主面板: http://localhost:8050
- API文档: http://localhost:8000/docs

---

## 📝 完整部署步骤

### 步骤1: 安装Docker

#### macOS
```bash
# 安装Docker Desktop
brew install --cask docker
# 或从官网下载: https://www.docker.com/products/docker-desktop
```

#### Linux (Ubuntu/Debian)
```bash
# 更新包索引
sudo apt-get update

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo apt-get install docker-compose-plugin

# 将用户添加到docker组
sudo usermod -aG docker $USER
newgrp docker
```

#### Windows
1. 安装Docker Desktop for Windows
2. 确保启用WSL2
3. 在WSL2终端中运行项目

### 步骤2: 准备项目

```bash
# 进入项目目录
cd /path/to/mrna2

# 确保脚本有执行权限
chmod +x run-ultrathink-full.sh
chmod +x docker-ultrathink.sh
```

### 步骤3: 启动服务

#### 方法1: 使用完整启动脚本（推荐）
```bash
./run-ultrathink-full.sh
```

#### 方法2: 使用docker-compose直接启动
```bash
# 创建必要目录
mkdir -p data/{raw,processed,external,user_uploads} \
         results/{tables,networks,linchpins,figures,user_analyses} \
         logs temp cache

# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 方法3: 使用管理脚本
```bash
# 启动完整服务
./docker-ultrathink.sh start --full

# 查看状态
./docker-ultrathink.sh status
```

### 步骤4: 验证部署

```bash
# 检查服务健康状态
curl http://localhost:8050/          # Dashboard
curl http://localhost:8000/health    # API

# 查看运行中的容器
docker ps

# 查看资源使用情况
docker stats
```

---

## 🏗️ 服务架构

### 核心服务

| 服务名称 | 容器名称 | 端口 | 说明 |
|---------|---------|------|------|
| **Dashboard** | ultrathink-dashboard | 8050 | Web用户界面 |
| **API Server** | ultrathink-api | 8000 | REST API服务 |
| **Redis** | ultrathink-redis | 6379 | 缓存和任务队列 |

### 可选服务

| 服务名称 | 容器名称 | 端口 | 说明 |
|---------|---------|------|------|
| **PostgreSQL** | ultrathink-postgres | 5432 | 数据持久化 |
| **Nginx** | ultrathink-nginx | 80/443 | 反向代理 |
| **Grafana** | ultrathink-grafana | 3000 | 监控面板 |

### 服务依赖关系

```
┌─────────────────┐
│     Nginx       │
│   (可选代理)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐     ┌─────────┐
│Dashboard│ │  API  │────▶│  Redis  │
└────────┘ └───────┘     └─────────┘
              │                
              │          ┌──────────┐
              └─────────▶│PostgreSQL│
                        │  (可选)   │
                        └──────────┘
```

---

## ✅ 功能验证

### 1. Dashboard功能测试

访问 http://localhost:8050，测试以下功能：

- [ ] 页面正常加载
- [ ] 左侧导航菜单可用
- [ ] 数据上传功能
- [ ] 各分析模块可访问
- [ ] 可视化图表正常显示

### 2. API功能测试

#### 使用curl测试
```bash
# API健康检查
curl http://localhost:8000/health

# 获取API信息
curl -H "Authorization: Bearer ultrathink_api_token_2025" \
     http://localhost:8000/

# 查看API文档
open http://localhost:8000/docs
```

#### 使用Python SDK测试
```python
from src.api.api_client_sdk import LIHCAPIClient

# 创建客户端
client = LIHCAPIClient(
    base_url="http://localhost:8000",
    api_token="ultrathink_api_token_2025"
)

# 健康检查
health = client.health_check()
print(f"API状态: {health.success} - {health.message}")

# 获取API统计
stats = client.get_api_stats()
print(f"API统计: {stats.data}")
```

### 3. 分析功能测试

```python
# 测试单细胞分析
from src.api.api_client_sdk import create_sample_data

sample_data = create_sample_data(n_genes=100, n_cells=50)
response = client.analyze_single_cell(sample_data)

if response.success:
    print(f"分析任务ID: {response.task_id}")
    # 等待完成
    result = client.wait_for_task_completion(response.task_id)
    print(f"分析结果: {result.data}")
```

---

## ❓ 常见问题

### Q1: 端口被占用
```bash
# 检查端口占用
lsof -i :8050
lsof -i :8000

# 解决方案1: 停止占用端口的服务
kill -9 <PID>

# 解决方案2: 修改端口映射
# 编辑 docker-compose.yml，修改端口：
# ports:
#   - "8051:8050"  # 改为其他端口
```

### Q2: 构建失败
```bash
# 清理Docker缓存
docker system prune -af

# 重新构建
docker-compose build --no-cache
```

### Q3: 内存不足
```bash
# 检查Docker内存限制
docker system info | grep Memory

# 增加Docker Desktop内存配置
# macOS/Windows: Docker Desktop > Preferences > Resources
# Linux: 修改 /etc/docker/daemon.json
```

### Q4: 服务无法启动
```bash
# 查看详细错误日志
docker-compose logs ultrathink-dashboard
docker-compose logs ultrathink-api

# 检查文件权限
ls -la src/
chmod -R 755 src/
```

### Q5: 无法访问服务
```bash
# 检查容器网络
docker network ls
docker network inspect mrna2_ultrathink-network

# 检查防火墙设置（Linux）
sudo ufw status
sudo ufw allow 8050
sudo ufw allow 8000
```

---

## ⚙️ 高级配置

### 自定义环境变量

创建 `.env` 文件：
```env
# API配置
API_PORT=8000
API_WORKERS=4
API_TOKEN=your_custom_token

# Dashboard配置
DASHBOARD_PORT=8050
DASHBOARD_MODE=professional

# 数据库配置
POSTGRES_USER=ultrathink_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=ultrathink_db

# Redis配置
REDIS_MAX_MEMORY=1gb
```

### 生产环境部署

#### 1. 使用HTTPS
```yaml
# docker-compose.override.yml
services:
  nginx:
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
    environment:
      - ENABLE_SSL=true
```

#### 2. 数据持久化
```yaml
volumes:
  postgres-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /data/ultrathink/postgres
```

#### 3. 资源限制
```yaml
services:
  ultrathink-api:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

### 监控和日志

#### 启用Grafana监控
```bash
# 编辑 docker-compose.yml，取消注释Grafana服务
# 重启服务
docker-compose up -d grafana

# 访问监控面板
open http://localhost:3000
# 用户名: admin
# 密码: ultrathink2025
```

#### 集中日志管理
```bash
# 查看所有日志
docker-compose logs -f

# 导出日志
docker-compose logs > ultrathink_logs_$(date +%Y%m%d).txt

# 实时监控特定服务
docker-compose logs -f ultrathink-api
```

---

## 🔧 维护命令

### 日常维护
```bash
# 备份数据
./docker-ultrathink.sh backup

# 清理未使用资源
docker system prune -f

# 更新镜像
docker-compose pull
docker-compose up -d
```

### 故障恢复
```bash
# 强制重启所有服务
docker-compose down
docker-compose up -d --force-recreate

# 恢复备份
./docker-ultrathink.sh restore backups/20250127_143000
```

---

## 📊 性能优化建议

1. **使用SSD存储**: 将Docker数据目录放在SSD上
2. **增加内存**: 分配至少8GB内存给Docker
3. **启用缓存**: 确保Redis服务正常运行
4. **限制日志**: 配置日志轮转避免磁盘占用过多

```yaml
# docker-compose.yml 添加日志限制
services:
  ultrathink-api:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 🎯 下一步

1. **探索功能**: 访问 http://localhost:8050 开始使用平台
2. **查看API文档**: http://localhost:8000/docs
3. **运行示例分析**: 参考 API_USAGE_GUIDE.md
4. **集成到工作流**: 使用Python SDK进行批量分析

---

## 📞 技术支持

遇到问题？
1. 查看日志: `docker-compose logs -f`
2. 查看文档: `DOCKER_QUICKSTART.md`, `API_USAGE_GUIDE.md`
3. 运行诊断: `./docker-ultrathink.sh test`

---

**🎉 恭喜！您已成功部署ultrathink v2.7平台，开始您的肝癌精准医疗分析之旅吧！**