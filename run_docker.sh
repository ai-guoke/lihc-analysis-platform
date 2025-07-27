#!/bin/bash

# 🐳 LIHC Platform Quick Docker Runner
# 快速启动LIHC平台的简化脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 启动LIHC肿瘤微环境分析平台...${NC}"

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}❌ Docker未安装，请先安装Docker${NC}"
    exit 1
fi

# 检查docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}❌ Docker Compose未安装${NC}"
    exit 1
fi

# 进入项目目录
cd "$(dirname "$0")"

# 创建必要目录
mkdir -p data/{raw,processed,external,user_uploads} results/{tables,networks,linchpins,figures} logs config

echo -e "${BLUE}🔧 构建并启动服务...${NC}"

# 构建并启动
docker-compose up --build -d

echo -e "${BLUE}⏱️  等待服务启动...${NC}"

# 等待服务就绪
sleep 30

# 检查状态
if curl -s http://localhost:8050 > /dev/null; then
    echo -e "${GREEN}✅ 平台启动成功！${NC}"
    echo -e "${GREEN}🌐 访问地址: http://localhost:8050${NC}"
else
    echo -e "${YELLOW}⚠️  服务可能还在启动中，请稍候访问 http://localhost:8050${NC}"
fi

echo -e "${BLUE}📊 查看服务状态:${NC}"
docker-compose ps