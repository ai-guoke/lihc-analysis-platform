#!/bin/bash

# ultrathink v2.7 完整版Docker运行脚本
# 肝细胞癌精准医疗分析平台

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║             ultrathink v2.7.0 完整版平台                     ║"
echo "║           肝细胞癌精准医疗分析 - Docker部署                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 1. 检查Docker环境
echo -e "${BLUE}[1/6] 检查Docker环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装。请先安装Docker Desktop${NC}"
    echo "访问: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    # 尝试使用docker compose命令
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}错误: Docker Compose未安装${NC}"
        exit 1
    fi
    # 创建别名
    alias docker-compose='docker compose'
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}错误: Docker服务未启动。请启动Docker Desktop${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker环境检查通过${NC}"

# 2. 创建必要的目录结构
echo -e "\n${BLUE}[2/6] 创建项目目录结构...${NC}"
directories=(
    "data/raw"
    "data/processed"
    "data/external"
    "data/user_uploads"
    "data/templates"
    "results/tables"
    "results/networks"
    "results/linchpins"
    "results/figures"
    "results/user_analyses"
    "logs"
    "temp"
    "cache"
    "config"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    echo -e "  ${GREEN}✓${NC} 创建目录: $dir"
done

# 3. 检查必要文件
echo -e "\n${BLUE}[3/6] 检查必要文件...${NC}"
required_files=(
    "requirements.txt"
    "docker-compose.yml"
    "Dockerfile"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "  ${GREEN}✓${NC} 找到文件: $file"
    else
        missing_files+=("$file")
        echo -e "  ${RED}✗${NC} 缺少文件: $file"
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo -e "${RED}错误: 缺少必要文件，请确保在项目根目录运行此脚本${NC}"
    exit 1
fi

# 4. 停止并清理旧容器（如果存在）
echo -e "\n${BLUE}[4/6] 清理旧容器...${NC}"
if docker ps -a | grep -q "ultrathink"; then
    echo -e "${YELLOW}发现旧容器，正在清理...${NC}"
    docker-compose down 2>/dev/null || true
    docker system prune -f
fi
echo -e "${GREEN}✓ 清理完成${NC}"

# 5. 构建并启动服务
echo -e "\n${BLUE}[5/6] 构建并启动ultrathink服务...${NC}"
echo -e "${YELLOW}这可能需要几分钟时间，请耐心等待...${NC}"

# 使用标准docker-compose.yml启动所有服务
docker-compose up -d --build

# 等待服务启动
echo -e "\n${YELLOW}等待服务完全启动...${NC}"
sleep 20

# 6. 验证服务状态
echo -e "\n${BLUE}[6/6] 验证服务状态...${NC}"

# 检查容器状态
echo -e "\n${CYAN}容器运行状态:${NC}"
docker-compose ps

# 检查服务健康状态
services=("ultrathink-dashboard" "ultrathink-api" "ultrathink-redis")
all_healthy=true

for service in "${services[@]}"; do
    if docker ps | grep -q "$service"; then
        echo -e "  ${GREEN}✓${NC} $service 运行中"
    else
        echo -e "  ${RED}✗${NC} $service 未运行"
        all_healthy=false
    fi
done

# 显示访问信息
echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}              ultrathink v2.7.0 完整版启动成功！              ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"

echo -e "\n${PURPLE}📊 核心功能模块:${NC}"
echo -e "  • 单细胞RNA-seq分析"
echo -e "  • AI生物标志物发现"
echo -e "  • 药物组合预测"
echo -e "  • 多组学数据整合"
echo -e "  • 患者分层系统"
echo -e "  • 智能报告生成"
echo -e "  • 实时任务队列"

echo -e "\n${CYAN}🌐 访问地址:${NC}"
echo -e "  ${YELLOW}主控制面板:${NC}    http://localhost:8050"
echo -e "  ${YELLOW}API服务:${NC}       http://localhost:8000"
echo -e "  ${YELLOW}API文档:${NC}       http://localhost:8000/docs"
echo -e "  ${YELLOW}API ReDoc:${NC}     http://localhost:8000/redoc"

if docker ps | grep -q "ultrathink-postgres"; then
    echo -e "\n${CYAN}🗄️ 数据库服务:${NC}"
    echo -e "  ${YELLOW}PostgreSQL:${NC}    localhost:5432"
    echo -e "  ${YELLOW}数据库:${NC}        ultrathink_db"
    echo -e "  ${YELLOW}用户:${NC}          ultrathink_user"
fi

if docker ps | grep -q "ultrathink-grafana"; then
    echo -e "\n${CYAN}📈 监控服务:${NC}"
    echo -e "  ${YELLOW}Grafana:${NC}       http://localhost:3000"
    echo -e "  ${YELLOW}用户/密码:${NC}     admin/ultrathink2025"
fi

echo -e "\n${CYAN}🔑 API认证信息:${NC}"
echo -e "  ${YELLOW}管理员令牌:${NC}    ultrathink_api_token_2025"
echo -e "  ${YELLOW}研究员令牌:${NC}    research_token_2025"

echo -e "\n${CYAN}📝 常用管理命令:${NC}"
echo -e "  ${YELLOW}查看日志:${NC}      docker-compose logs -f [service_name]"
echo -e "  ${YELLOW}停止服务:${NC}      docker-compose down"
echo -e "  ${YELLOW}重启服务:${NC}      docker-compose restart"
echo -e "  ${YELLOW}查看状态:${NC}      docker-compose ps"
echo -e "  ${YELLOW}进入容器:${NC}      docker-compose exec ultrathink-dashboard bash"

echo -e "\n${CYAN}🧪 测试平台功能:${NC}"
echo -e "  ${YELLOW}健康检查:${NC}"
echo -e "    curl http://localhost:8050/"
echo -e "    curl http://localhost:8000/health"
echo -e "  ${YELLOW}API测试:${NC}"
echo -e "    curl -H \"Authorization: Bearer ultrathink_api_token_2025\" http://localhost:8000/"

if [[ "$all_healthy" == true ]]; then
    echo -e "\n${GREEN}🎉 所有服务启动成功！ultrathink平台已准备就绪。${NC}"
    echo -e "${GREEN}🚀 现在可以访问 http://localhost:8050 开始使用平台${NC}"
else
    echo -e "\n${YELLOW}⚠️  部分服务可能需要更多时间启动，请稍等片刻后再试${NC}"
    echo -e "${YELLOW}💡 提示: 使用 'docker-compose logs -f' 查看详细日志${NC}"
fi

echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}        ultrathink v2.7 - 肝细胞癌精准医疗分析平台           ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"