# Docker Deployment Guide

## 🐳 Docker部署指南

本文档说明如何使用Docker部署LIHC分析平台（包含最新的科学原理提示功能）。

### 📋 前置要求

- Docker Desktop (推荐版本 20.10+)
- Docker Compose (通常随Docker Desktop一起安装)
- 至少4GB可用内存
- 端口8050未被占用

### 🚀 快速部署

#### 方法1：使用部署脚本（推荐）

```bash
# 运行自动部署脚本
./deploy_with_tips.sh
```

脚本会自动：
- 检查Docker状态
- 停止旧容器
- 构建新镜像
- 启动服务
- 验证部署

#### 方法2：手动部署

```bash
# 1. 构建镜像
docker-compose -f docker-compose.scientific.yml build

# 2. 启动服务
docker-compose -f docker-compose.scientific.yml up -d

# 3. 查看日志
docker-compose -f docker-compose.scientific.yml logs -f
```

### 📂 Docker配置文件说明

1. **Dockerfile** - 基础Docker镜像配置
2. **Dockerfile.scientific** - 包含科学提示功能的优化版本
3. **docker-compose.professional.yml** - 专业版部署配置
4. **docker-compose.scientific.yml** - 科学版部署配置（推荐）

### 🔧 配置选项

#### 环境变量

- `DASHBOARD_MODE`: 仪表板模式 (professional/unified)
- `ENABLE_SCIENTIFIC_TIPS`: 启用科学原理提示 (true/false)
- `PYTHONUNBUFFERED`: Python输出缓冲 (建议设为1)

#### 端口映射

默认端口：8050（可在docker-compose文件中修改）

#### 数据卷

- `./src:/app/src` - 源代码（只读）
- `./data:/app/data` - 数据目录
- `./results:/app/results` - 结果输出
- `./logs:/app/logs` - 日志文件

### 🛠️ 常用命令

```bash
# 启动服务
docker-compose -f docker-compose.scientific.yml up -d

# 停止服务
docker-compose -f docker-compose.scientific.yml down

# 查看日志
docker-compose -f docker-compose.scientific.yml logs -f

# 重新构建镜像
docker-compose -f docker-compose.scientific.yml build --no-cache

# 进入容器
docker exec -it lihc-scientific-platform bash

# 查看容器状态
docker ps

# 清理未使用的镜像
docker system prune -a
```

### 🆕 新功能特性

#### 科学原理提示功能

- 每个分析页面都有"科学原理"按钮
- 点击可查看：
  - 🔬 科学基础
  - 💡 设计理念
  - 📊 数学原理
  - 📚 参考文献

#### 支持的分析模块

1. **多维度分析** - 五维肿瘤微环境分析
2. **网络分析** - 分子相互作用网络
3. **Linchpin靶点** - 关键治疗靶点识别
4. **生存分析** - 预后评估与风险分层
5. **多组学整合** - 多层次数据融合
6. **ClosedLoop分析** - 因果推理验证
7. **免疫微环境** - 免疫浸润评估
8. **药物响应预测** - 个体化用药指导
9. **分子分型** - 肿瘤亚型识别

### 🐛 故障排除

#### Docker未运行
```bash
# macOS/Windows: 启动Docker Desktop
# Linux: 
sudo systemctl start docker
```

#### 端口被占用
```bash
# 查找占用8050端口的进程
lsof -i:8050
# 终止进程
kill -9 <PID>
```

#### 构建失败
```bash
# 清理Docker缓存
docker system prune -a
# 重新构建
docker-compose -f docker-compose.scientific.yml build --no-cache
```

#### 内存不足
```bash
# 增加Docker内存限制（Docker Desktop设置中）
# 推荐至少4GB
```

### 📊 性能优化

1. **使用生产模式**
   - 设置 `ENV=production`
   - 启用Python优化：`PYTHONOPTIMIZE=1`

2. **资源限制**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 4G
   ```

3. **缓存优化**
   - 挂载缓存目录：`./cache:/app/cache`
   - 使用Redis缓存（可选）

### 🔒 安全建议

1. **使用非root用户**（已默认配置）
2. **限制网络访问**（使用专用网络）
3. **定期更新基础镜像**
4. **使用环境变量管理敏感信息**

### 📝 更新日志

- **v2.1.0** - 添加科学原理提示功能
- **v2.0.0** - 专业仪表板界面
- **v1.0.0** - 初始版本

### 💡 提示

- 首次启动可能需要几分钟下载依赖
- 建议使用Chrome或Firefox浏览器访问
- 支持移动端响应式布局
- 可通过环境变量自定义配置

### 📞 支持

如遇到问题，请：
1. 查看日志：`docker-compose logs`
2. 检查Docker状态：`docker ps`
3. 确认端口可用：`netstat -an | grep 8050`

---

🎉 祝您使用愉快！