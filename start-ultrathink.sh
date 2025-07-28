#!/bin/bash

# ultrathink v2.7 简化启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                 ultrathink v2.7.0 Platform                 ║"
echo "║           快速启动 - 肝细胞癌精准医疗分析平台                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: Docker Compose未安装${NC}"
    exit 1
fi

# 创建必要目录
echo -e "${BLUE}创建必要目录...${NC}"
mkdir -p data/{raw,processed,external,user_uploads} \
         results/{tables,networks,linchpins,figures,user_analyses} \
         logs temp cache

# 启动服务
echo -e "${BLUE}启动ultrathink平台...${NC}"
docker-compose -f docker-compose.simple.yml up -d

echo -e "${YELLOW}等待服务启动...${NC}"
sleep 15

# 检查服务状态
echo -e "${BLUE}检查服务状态...${NC}"
docker-compose -f docker-compose.simple.yml ps

echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                ultrathink v2.7.0 启动完成！${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"

echo -e "\n${CYAN}🖥️  访问地址:${NC}"
echo -e "  ${YELLOW}主面板:${NC}      http://localhost:8050"
echo -e "  ${YELLOW}API服务:${NC}     http://localhost:8000"
echo -e "  ${YELLOW}API文档:${NC}     http://localhost:8000/docs"

echo -e "\n${CYAN}🔑 API认证令牌:${NC}"
echo -e "  ${YELLOW}管理员:${NC}      ultrathink_api_token_2025"

echo -e "\n${CYAN}🛠️  管理命令:${NC}"
echo -e "  ${YELLOW}查看日志:${NC}    docker-compose -f docker-compose.simple.yml logs -f"
echo -e "  ${YELLOW}停止服务:${NC}    docker-compose -f docker-compose.simple.yml down"
echo -e "  ${YELLOW}重启服务:${NC}    docker-compose -f docker-compose.simple.yml restart"

echo -e "\n${GREEN}🚀 ultrathink平台已成功启动，可以开始分析了！${NC}"