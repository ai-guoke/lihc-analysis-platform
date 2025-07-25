#!/bin/bash

# LIHC Platform Docker停止脚本

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

echo "============================================================"
echo "🛑 LIHC Platform Docker 停止脚本"
echo "============================================================"
echo ""

# 查找所有运行的docker-compose配置
print_info "查找运行中的服务..."

compose_files=(
    "docker-compose.yml"
    "docker-compose.minimal.yml"
    "docker-compose.dev.yml"
    "docker-compose.stable.yml"
    "docker-compose.complete.yml"
)

stopped=0

for compose_file in "${compose_files[@]}"; do
    if [ -f "$compose_file" ]; then
        # 检查该配置文件是否有运行的容器
        if docker-compose -f "$compose_file" ps -q 2>/dev/null | grep -q .; then
            print_warning "发现使用 $compose_file 运行的服务"
            read -p "是否停止？(y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_info "停止 $compose_file 中的服务..."
                docker-compose -f "$compose_file" down
                stopped=$((stopped + 1))
            fi
        fi
    fi
done

if [ $stopped -eq 0 ]; then
    print_info "没有发现运行中的LIHC服务"
else
    print_success "已停止 $stopped 个服务配置"
fi

# 可选：清理
echo ""
read -p "是否清理未使用的Docker资源（镜像、卷等）？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "清理Docker资源..."
    docker system prune -f
    print_success "清理完成"
fi

echo ""
print_success "操作完成！"