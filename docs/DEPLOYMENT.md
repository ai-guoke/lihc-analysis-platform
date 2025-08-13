# 📦 LIHC Platform 部署指南

本文档提供 LIHC Analysis Platform 的详细部署说明，包括多种部署方式和配置选项。

## 📋 目录

- [系统要求](#系统要求)
- [部署方式](#部署方式)
  - [Docker部署（推荐）](#docker部署推荐)
  - [Docker Compose部署](#docker-compose部署)
  - [Kubernetes部署](#kubernetes部署)
  - [本地部署](#本地部署)
  - [云平台部署](#云平台部署)
- [配置管理](#配置管理)
- [性能优化](#性能优化)
- [安全配置](#安全配置)
- [监控与日志](#监控与日志)
- [故障排除](#故障排除)

---

## 系统要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 10GB 可用空间
- **系统**: Linux/macOS/Windows
- **Python**: 3.8+
- **浏览器**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

### 推荐配置
- **CPU**: 4核心或更多
- **内存**: 16GB RAM
- **存储**: 50GB SSD
- **GPU**: NVIDIA GPU（可选，用于加速深度学习）
- **网络**: 稳定的互联网连接

---

## 部署方式

### Docker部署（推荐）

#### 1. 安装Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# macOS
brew install docker

# Windows
# 下载并安装 Docker Desktop: https://www.docker.com/products/docker-desktop
```

#### 2. 构建镜像

```bash
# 克隆项目
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform

# 构建Docker镜像
docker build -t lihc-platform:latest .

# 或使用多阶段构建（生产环境）
docker build -f Dockerfile.prod -t lihc-platform:prod .
```

#### 3. 运行容器

```bash
# 基础运行
docker run -d \
  --name lihc-platform \
  -p 8050:8050 \
  lihc-platform:latest

# 高级配置运行
docker run -d \
  --name lihc-platform \
  -p 8050:8050 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/config:/app/config \
  -e APP_ENV=production \
  -e SECRET_KEY=your-secret-key \
  --restart unless-stopped \
  lihc-platform:latest
```

### Docker Compose部署

#### 1. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  lihc-platform:
    build: .
    image: lihc-platform:latest
    container_name: lihc-platform
    ports:
      - "8050:8050"
    volumes:
      - ./data:/app/data
      - ./results:/app/results
      - ./config:/app/config
    environment:
      - APP_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
    restart: unless-stopped
    networks:
      - lihc-network

  redis:
    image: redis:alpine
    container_name: lihc-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - lihc-network

  postgres:
    image: postgres:13
    container_name: lihc-db
    environment:
      - POSTGRES_DB=lihc_db
      - POSTGRES_USER=lihc_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - lihc-network

networks:
  lihc-network:
    driver: bridge

volumes:
  redis-data:
  postgres-data:
```

#### 2. 启动服务

```bash
# 创建环境变量文件
cat > .env << EOF
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://lihc_user:password@postgres:5432/lihc_db
DB_PASSWORD=your-db-password
EOF

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f lihc-platform
```

### Kubernetes部署

#### 1. 创建部署文件

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lihc-platform
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lihc-platform
  template:
    metadata:
      labels:
        app: lihc-platform
    spec:
      containers:
      - name: lihc-platform
        image: lihc-platform:latest
        ports:
        - containerPort: 8050
        env:
        - name: APP_ENV
          value: "production"
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: lihc-data-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: lihc-platform-service
spec:
  selector:
    app: lihc-platform
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8050
  type: LoadBalancer
```

#### 2. 部署到Kubernetes

```bash
# 创建命名空间
kubectl create namespace lihc-platform

# 应用配置
kubectl apply -f deployment.yaml -n lihc-platform

# 查看部署状态
kubectl get pods -n lihc-platform

# 获取服务地址
kubectl get service lihc-platform-service -n lihc-platform
```

### 本地部署

#### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/ai-guoke/lihc-analysis-platform.git
cd lihc-analysis-platform

# 创建Python虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 升级pip
pip install --upgrade pip
```

#### 2. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装系统依赖（Ubuntu/Debian）
sudo apt-get update
sudo apt-get install -y \
  build-essential \
  python3-dev \
  libpq-dev \
  redis-server

# macOS
brew install postgresql redis
```

#### 3. 配置环境

```bash
# 创建配置文件
cp .env.example .env

# 编辑配置
nano .env
```

#### 4. 初始化数据库（如果使用）

```bash
# 创建数据库
python scripts/init_db.py

# 运行迁移
python scripts/migrate.py
```

#### 5. 启动应用

```bash
# 开发模式
python main.py --dashboard --debug --port 8050

# 生产模式
gunicorn -w 4 -b 0.0.0.0:8050 "main:server"

# 或使用PM2（Node.js进程管理器）
pm2 start ecosystem.config.js
```

### 云平台部署

#### AWS EC2

```bash
# 1. 创建EC2实例（推荐t3.medium或更高）

# 2. SSH连接到实例
ssh -i your-key.pem ec2-user@your-instance-ip

# 3. 安装Docker
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# 4. 部署应用
docker run -d \
  --name lihc-platform \
  -p 80:8050 \
  -v /data:/app/data \
  --restart always \
  lihc-platform:latest

# 5. 配置安全组
# 开放端口 80 (HTTP) 和 443 (HTTPS)
```

#### Google Cloud Platform

```bash
# 1. 创建GCE实例
gcloud compute instances create lihc-platform \
  --machine-type=n1-standard-2 \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB

# 2. SSH连接
gcloud compute ssh lihc-platform

# 3. 安装并运行
# 参考Docker部署步骤

# 4. 配置防火墙
gcloud compute firewall-rules create allow-lihc \
  --allow tcp:8050 \
  --source-ranges 0.0.0.0/0
```

#### Azure

```bash
# 1. 创建资源组
az group create --name lihc-rg --location eastus

# 2. 创建容器实例
az container create \
  --resource-group lihc-rg \
  --name lihc-platform \
  --image lihc-platform:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8050 \
  --ip-address public
```

---

## 配置管理

### 环境变量配置

```bash
# .env 文件示例
# ==================== 应用配置 ====================
APP_ENV=production           # development/staging/production
APP_DEBUG=false              # true/false
SECRET_KEY=your-secret-key   # 用于加密会话

# ==================== 服务器配置 ====================
HOST=0.0.0.0                # 监听地址
PORT=8050                    # 监听端口
WORKERS=4                    # 工作进程数

# ==================== 数据库配置 ====================
DATABASE_URL=postgresql://user:password@localhost:5432/lihc_db
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# ==================== Redis配置 ====================
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600              # 缓存过期时间（秒）

# ==================== 数据配置 ====================
DATA_DIR=/app/data
RESULTS_DIR=/app/results
UPLOAD_MAX_SIZE=100MB
ALLOWED_EXTENSIONS=csv,tsv,txt,xlsx,xls

# ==================== 分析配置 ====================
PARALLEL_WORKERS=4          # 并行分析进程数
ANALYSIS_TIMEOUT=3600       # 分析超时时间（秒）
GPU_ENABLED=false           # 是否启用GPU加速

# ==================== 日志配置 ====================
LOG_LEVEL=INFO             # DEBUG/INFO/WARNING/ERROR
LOG_FILE=/app/logs/app.log
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5

# ==================== 安全配置 ====================
CORS_ORIGINS=*             # 允许的跨域来源
RATE_LIMIT=100/hour        # 请求限制
SESSION_TIMEOUT=3600       # 会话超时（秒）
```

### 配置文件管理

```yaml
# config/config.yaml
app:
  name: LIHC Analysis Platform
  version: 2.6
  description: Multi-dimensional analysis platform for HCC

server:
  host: 0.0.0.0
  port: 8050
  debug: false
  reload: false

analysis:
  survival:
    min_samples: 20
    p_value_threshold: 0.05
    confidence_interval: 0.95
    
  network:
    correlation_method: pearson
    correlation_threshold: 0.6
    min_node_degree: 3
    max_nodes: 500
    
  dimension_weights:
    tumor: 0.3
    immune: 0.25
    stromal: 0.2
    ecm: 0.15
    cytokine: 0.1

visualization:
  theme: light
  colors:
    primary: '#667eea'
    secondary: '#764ba2'
  plotly_config:
    displayModeBar: true
    responsive: true
```

---

## 性能优化

### 1. 缓存配置

```python
# config/cache.py
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 3600,
    'CACHE_KEY_PREFIX': 'lihc_',
}
```

### 2. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_samples_patient_id ON samples(patient_id);
CREATE INDEX idx_genes_symbol ON genes(symbol);
CREATE INDEX idx_expression_composite ON expression(sample_id, gene_id);

-- 分区表（用于大数据集）
CREATE TABLE expression_2024 PARTITION OF expression
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 3. Nginx反向代理

```nginx
# /etc/nginx/sites-available/lihc-platform
server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 静态文件缓存
    location /assets/ {
        alias /app/assets/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 4. CDN配置

```javascript
// config/cdn.js
const CDN_CONFIG = {
  plotly: 'https://cdn.plot.ly/plotly-latest.min.js',
  bootstrap: 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
  fontawesome: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
};
```

---

## 安全配置

### 1. HTTPS配置

```bash
# 使用Let's Encrypt获取SSL证书
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. 防火墙配置

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 8050 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

### 3. 安全头配置

```python
# config/security.py
SECURITY_HEADERS = {
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'"
}
```

---

## 监控与日志

### 1. 日志配置

```python
# config/logging.py
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console']
    }
}
```

### 2. Prometheus监控

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
      
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 3. 健康检查

```python
# healthcheck.py
@app.route('/health')
def health_check():
    checks = {
        'status': 'healthy',
        'database': check_database(),
        'redis': check_redis(),
        'disk_space': check_disk_space(),
        'memory': check_memory()
    }
    return jsonify(checks)
```

---

## 故障排除

### 常见问题

#### 1. 端口已被占用

```bash
# 查找占用端口的进程
sudo lsof -i :8050
# 或
sudo netstat -tulpn | grep :8050

# 终止进程
sudo kill -9 <PID>
```

#### 2. 内存不足

```bash
# 增加swap空间
sudo dd if=/dev/zero of=/swapfile bs=1G count=4
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 3. Docker容器无法启动

```bash
# 查看容器日志
docker logs lihc-platform

# 进入容器调试
docker run -it --entrypoint /bin/bash lihc-platform:latest

# 清理Docker资源
docker system prune -a
```

#### 4. 数据库连接失败

```bash
# 检查数据库服务
sudo systemctl status postgresql

# 检查连接
psql -h localhost -U lihc_user -d lihc_db

# 重置数据库密码
sudo -u postgres psql
ALTER USER lihc_user PASSWORD 'new_password';
```

### 日志位置

- **应用日志**: `/app/logs/app.log`
- **Docker日志**: `docker logs lihc-platform`
- **系统日志**: `/var/log/syslog`
- **Nginx日志**: `/var/log/nginx/`

### 获取支持

- 📧 Email: support@lihc-platform.com
- 🐛 Issues: [GitHub Issues](https://github.com/ai-guoke/lihc-analysis-platform/issues)
- 📚 文档: [在线文档](https://docs.lihc-platform.com)

---

<div align="center">

[返回主页](../README.md) | [开发指南](DEVELOPMENT.md) | [API文档](API.md)

</div>