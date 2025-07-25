#!/bin/bash

# LIHC Platform Docker状态检查脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "============================================================"
echo "📊 LIHC Platform Docker 状态检查"
echo "============================================================"
echo ""

# 检查Docker服务
print_info "检查Docker服务状态..."
if docker info &> /dev/null; then
    print_success "Docker服务正常运行"
else
    print_error "Docker服务未运行"
    exit 1
fi

# 检查运行的容器
print_info "检查LIHC平台容器..."
echo ""

# 检查各个配置文件的容器
compose_files=(
    "docker-compose.yml"
    "docker-compose.minimal.yml"
    "docker-compose.dev.yml"
    "docker-compose.stable.yml"
    "docker-compose.complete.yml"
)

total_containers=0

for compose_file in "${compose_files[@]}"; do
    if [ -f "$compose_file" ]; then
        # 获取该配置文件定义的服务
        services=$(docker-compose -f "$compose_file" ps --services 2>/dev/null || true)
        if [ -n "$services" ]; then
            echo "📄 $compose_file:"
            docker-compose -f "$compose_file" ps 2>/dev/null || true
            echo ""
            
            # 统计运行的容器
            running=$(docker-compose -f "$compose_file" ps -q 2>/dev/null | wc -l | tr -d ' ')
            total_containers=$((total_containers + running))
        fi
    fi
done

echo "------------------------------------------------------------"

if [ $total_containers -gt 0 ]; then
    print_success "共有 $total_containers 个LIHC容器在运行"
    echo ""
    
    # 显示容器详细信息
    echo "🐳 运行中的容器详情："
    docker ps --filter "name=lihc" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    echo "📊 资源使用情况："
    docker stats --no-stream --filter "name=lihc"
    
    echo ""
    echo "🌐 访问地址："
    if docker ps | grep -q "8050->8050"; then
        print_success "主应用: http://localhost:8050"
    fi
    if docker ps | grep -q "8051->8051"; then
        print_info "Dashboard: http://localhost:8051"
    fi
    if docker ps | grep -q "3000->3000"; then
        print_info "Grafana: http://localhost:3000"
    fi
    if docker ps | grep -q "9090->9090"; then
        print_info "Prometheus: http://localhost:9090"
    fi
    
else
    print_warning "没有发现运行中的LIHC容器"
    echo ""
    echo "💡 提示：使用以下命令启动服务："
    echo "   ./docker-start.sh"
    echo "   或"
    echo "   docker-compose -f docker-compose.minimal.yml up -d"
fi

echo ""
echo "🔧 常用命令："
echo "  查看日志: docker logs -f <container-name>"
echo "  进入容器: docker exec -it <container-name> bash"
echo "  重启容器: docker restart <container-name>"
echo ""