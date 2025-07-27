#!/bin/bash

# LIHC Platform Docker Deployment Script
# 一键部署LIHC肿瘤微环境五维度分析平台
# 
# Usage: ./deploy_with_tips.sh [options]
# Options:
#   --build-only    只构建镜像，不启动服务
#   --start-only    只启动已存在的服务
#   --force-rebuild 强制重新构建镜像
#   --help          显示帮助信息

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 图标定义
ROCKET="🚀"
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
DOCKER="🐳"
HEART="💖"
TIMER="⏱️"
SPARKLE="✨"

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}${1}${NC}"
}

print_success() {
    echo -e "${GREEN}${CHECK} ${1}${NC}"
}

print_error() {
    echo -e "${RED}${CROSS} ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}${WARNING} ${1}${NC}"
}

print_header() {
    echo -e "${PURPLE}${1}${NC}"
}

# 显示帮助信息
show_help() {
    cat << EOF
${ROCKET} LIHC平台Docker部署脚本

使用方法:
  ./deploy_with_tips.sh [选项]

选项:
  --build-only     只构建镜像，不启动服务
  --start-only     只启动已存在的服务  
  --force-rebuild  强制重新构建镜像
  --help          显示此帮助信息

示例:
  ./deploy_with_tips.sh                # 完整部署
  ./deploy_with_tips.sh --build-only   # 只构建镜像
  ./deploy_with_tips.sh --start-only   # 只启动服务

EOF
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装或不在PATH中"
        return 1
    fi
}

# 检查系统要求
check_requirements() {
    print_header "${DOCKER} 检查系统要求..."
    
    # 检查Docker
    if ! check_command docker; then
        print_error "请先安装 Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # 检查Docker版本
    DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
    REQUIRED_VERSION="20.10"
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$DOCKER_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        print_warning "Docker版本可能过低 (当前: $DOCKER_VERSION, 推荐: $REQUIRED_VERSION+)"
    else
        print_success "Docker版本检查通过: $DOCKER_VERSION"
    fi
    
    # 检查Docker Compose
    if ! check_command docker-compose; then
        print_error "请先安装 Docker Compose"
        exit 1
    fi
    
    # 检查Docker服务状态
    if ! docker info &> /dev/null; then
        print_error "Docker服务未运行，请启动Docker"
        exit 1
    fi
    
    # 检查端口占用
    if lsof -Pi :8050 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口8050已被占用，可能需要停止其他服务"
        echo "占用端口的进程:"
        lsof -Pi :8050 -sTCP:LISTEN
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # 检查磁盘空间 (至少需要5GB)
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    REQUIRED_SPACE=$((5 * 1024 * 1024))  # 5GB in KB
    if [ $AVAILABLE_SPACE -lt $REQUIRED_SPACE ]; then
        print_warning "可用磁盘空间可能不足 (可用: $(($AVAILABLE_SPACE/1024/1024))GB, 推荐: 5GB+)"
    fi
    
    print_success "系统要求检查完成"
}

# 创建必要的目录
create_directories() {
    print_info "创建必要的目录..."
    
    directories=(
        "data/raw"
        "data/processed" 
        "data/external"
        "data/user_uploads"
        "results/tables"
        "results/networks"
        "results/linchpins"
        "results/figures"
        "results/user_analyses"
        "logs"
        "config"
        "uploads"
        "temp"
        "cache"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        print_success "创建目录: $dir"
    done
}

# 检查重要文件
check_files() {
    print_info "检查重要文件..."
    
    required_files=(
        "Dockerfile"
        "docker-compose.yml"
        "requirements.txt"
        "main.py"
        "src/visualization/professional_dashboard.py"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "缺少重要文件: $file"
            exit 1
        else
            print_success "文件检查通过: $file"
        fi
    done
}

# 清理旧容器和镜像
cleanup_old_containers() {
    print_info "清理旧容器和镜像..."
    
    # 停止并删除相关容器
    if docker-compose ps -q 2>/dev/null | grep -q .; then
        print_info "停止现有服务..."
        docker-compose down --volumes --remove-orphans 2>/dev/null || true
    fi
    
    # 清理悬空镜像
    if docker images -f "dangling=true" -q | grep -q .; then
        print_info "清理悬空镜像..."
        docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null || true
    fi
    
    print_success "清理完成"
}

# 构建Docker镜像
build_image() {
    print_header "${DOCKER} 构建Docker镜像..."
    
    # 显示构建开始信息
    print_info "开始构建LIHC平台镜像，这可能需要几分钟..."
    print_info "正在安装Python依赖包..."
    
    # 构建镜像
    if docker-compose build --no-cache; then
        print_success "Docker镜像构建成功"
    else
        print_error "Docker镜像构建失败"
        print_info "常见解决方案:"
        print_info "1. 检查网络连接"
        print_info "2. 清理Docker缓存: docker system prune -f"
        print_info "3. 增加Docker内存限制"
        exit 1
    fi
}

# 启动服务
start_services() {
    print_header "${ROCKET} 启动LIHC平台服务..."
    
    # 启动服务
    if docker-compose up -d; then
        print_success "服务启动成功"
    else
        print_error "服务启动失败"
        print_info "检查日志: docker-compose logs lihc-platform"
        exit 1
    fi
}

# 等待服务就绪
wait_for_service() {
    print_info "${TIMER} 等待服务完全启动..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8050/health > /dev/null 2>&1; then
            print_success "服务已就绪！"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_warning "服务可能还在启动中，请稍候片刻"
    print_info "您可以通过以下方式检查状态:"
    print_info "  docker-compose logs -f lihc-platform"
    print_info "  curl http://localhost:8050/health"
}

# 显示服务状态
show_status() {
    print_header "${SPARKLE} 服务状态信息"
    
    echo
    print_info "容器状态:"
    docker-compose ps
    
    echo
    print_info "服务访问地址:"
    echo -e "  ${GREEN}🌐 主平台: ${CYAN}http://localhost:8050${NC}"
    echo -e "  ${GREEN}🏥 健康检查: ${CYAN}http://localhost:8050/health${NC}"
    
    echo
    print_info "容器管理命令:"
    echo -e "  ${YELLOW}查看日志:${NC} docker-compose logs -f lihc-platform"
    echo -e "  ${YELLOW}停止服务:${NC} docker-compose down"
    echo -e "  ${YELLOW}重启服务:${NC} docker-compose restart"
    echo -e "  ${YELLOW}进入容器:${NC} docker-compose exec lihc-platform bash"
    
    echo
    print_info "平台功能特色:"
    echo -e "  ${PURPLE}🧬 五维度预后分析${NC} - 240+基因多维度评估"
    echo -e "  ${PURPLE}🛡️  TAMs极化分析${NC} - M1/M2巨噬细胞分析"
    echo -e "  ${PURPLE}📊 生存分析集成${NC} - 风险分层与Kaplan-Meier曲线"
    echo -e "  ${PURPLE}📈 交互式可视化${NC} - 专业级图表和仪表板"
}

# 显示问题排查提示
show_troubleshooting() {
    print_header "${WARNING} 常见问题排查"
    
    echo
    print_info "如果遇到问题，请尝试:"
    echo -e "  ${YELLOW}1. 检查日志:${NC} docker-compose logs lihc-platform"
    echo -e "  ${YELLOW}2. 重启服务:${NC} docker-compose restart"
    echo -e "  ${YELLOW}3. 完全重建:${NC} ./deploy_with_tips.sh --force-rebuild"
    echo -e "  ${YELLOW}4. 检查端口:${NC} lsof -i :8050"
    echo -e "  ${YELLOW}5. 查看文档:${NC} cat DOCKER_DEPLOYMENT.md"
    
    echo
    print_info "获取帮助:"
    echo -e "  ${CYAN}📖 部署文档: DOCKER_DEPLOYMENT.md${NC}"
    echo -e "  ${CYAN}📋 项目文档: README.md${NC}"
}

# 主函数
main() {
    local build_only=false
    local start_only=false
    local force_rebuild=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --build-only)
                build_only=true
                shift
                ;;
            --start-only)
                start_only=true
                shift
                ;;
            --force-rebuild)
                force_rebuild=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 显示欢迎信息
    echo
    print_header "========================================================"
    print_header "${ROCKET} LIHC肿瘤微环境五维度分析平台 Docker部署"
    print_header "========================================================"
    echo
    
    # 检查系统要求
    check_requirements
    echo
    
    # 检查文件
    check_files
    echo
    
    # 创建目录
    create_directories
    echo
    
    if [ "$start_only" = false ]; then
        # 清理旧容器 (如果需要强制重建)
        if [ "$force_rebuild" = true ]; then
            cleanup_old_containers
            echo
        fi
        
        # 构建镜像
        build_image
        echo
    fi
    
    if [ "$build_only" = false ]; then
        # 启动服务
        start_services
        echo
        
        # 等待服务就绪
        wait_for_service
        echo
        
        # 显示状态信息
        show_status
        echo
        
        # 显示问题排查提示
        show_troubleshooting
        echo
        
        # 成功消息
        print_header "========================================================"
        print_success "${HEART} LIHC平台部署完成！请在浏览器中访问: http://localhost:8050"
        print_header "========================================================"
    else
        print_success "镜像构建完成！使用 --start-only 启动服务"
    fi
}

# 运行主函数
main "$@"