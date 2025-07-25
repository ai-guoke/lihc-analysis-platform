#!/bin/bash

# LIHC Platform Docker启动管理脚本
# 支持多种运行模式和环境检查

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
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

# 显示标题
show_banner() {
    echo "============================================================"
    echo "🧬 LIHC Multi-dimensional Analysis Platform"
    echo "🐳 Docker 启动管理脚本 v2.0"
    echo "============================================================"
    echo ""
}

# 检查系统要求
check_requirements() {
    print_info "检查系统环境..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装"
        echo "请访问 https://docs.docker.com/get-docker/ 安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装"
        echo "请访问 https://docs.docker.com/compose/install/ 安装Docker Compose"
        exit 1
    fi
    
    # 检查Docker服务是否运行
    if ! docker info &> /dev/null; then
        print_error "Docker 服务未运行"
        echo "请启动Docker Desktop或Docker服务"
        exit 1
    fi
    
    print_success "环境检查通过"
}

# 检查端口占用
check_ports() {
    local ports=("8050" "8051" "5432" "6379" "3000" "9090")
    local occupied=0
    
    print_info "检查端口占用情况..."
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "端口 $port 已被占用"
            occupied=1
        fi
    done
    
    if [ $occupied -eq 0 ]; then
        print_success "所有端口都可用"
    else
        print_warning "某些端口被占用，可能需要修改配置或停止占用的服务"
        read -p "是否继续？(y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 创建必要的目录
create_directories() {
    print_info "创建必要的目录..."
    
    directories=(
        "data/raw"
        "data/processed"
        "data/templates"
        "data/user_uploads"
        "results/tables"
        "results/networks"
        "results/linchpins"
        "results/figures"
        "results/user_analyses"
        "logs"
        "uploads"
        "config"
        "ssl/certs"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
    done
    
    print_success "目录创建完成"
}

# 生成环境配置文件
generate_env_file() {
    if [ ! -f .env ]; then
        print_info "生成环境配置文件..."
        cat > .env <<EOF
# LIHC Platform Environment Variables
# 自动生成于 $(date)

# 数据库配置
POSTGRES_DB=lihc_platform
POSTGRES_USER=lihc_user
POSTGRES_PASSWORD=lihc_secure_password_$(openssl rand -hex 8)

# Redis配置
REDIS_URL=redis://redis:6379/0

# 安全配置
SECRET_KEY=$(openssl rand -hex 32)

# 环境设置
ENVIRONMENT=production

# API配置
API_BASE_URL=http://lihc-api:8050

# 监控配置
GF_SECURITY_ADMIN_PASSWORD=admin_$(openssl rand -hex 4)
EOF
        print_success "环境配置文件已生成 (.env)"
        print_warning "请检查 .env 文件并根据需要修改配置"
    else
        print_info "使用现有的 .env 文件"
    fi
}

# 选择运行模式
select_mode() {
    echo ""
    echo "请选择运行模式："
    echo ""
    echo "  1) 🚀 快速体验模式 (minimal)"
    echo "     - 最小依赖，快速启动"
    echo "     - 仅包含核心功能"
    echo "     - 适合快速测试和演示"
    echo ""
    echo "  2) 🛠️  开发模式 (dev)"
    echo "     - 包含开发工具"
    echo "     - 支持代码热重载"
    echo "     - 包含Jupyter环境"
    echo ""
    echo "  3) 🏭 生产模式 (production)"
    echo "     - 完整服务栈"
    echo "     - 包含数据库、缓存、监控"
    echo "     - 适合正式部署"
    echo ""
    echo "  4) 🔧 自定义模式"
    echo "     - 选择特定的docker-compose文件"
    echo ""
    
    read -p "请选择 (1-4) [默认: 1]: " mode
    mode=${mode:-1}
    
    case $mode in
        1)
            COMPOSE_FILE="docker-compose.minimal.yml"
            MODE_NAME="快速体验模式"
            ;;
        2)
            COMPOSE_FILE="docker-compose.dev.yml"
            MODE_NAME="开发模式"
            ;;
        3)
            COMPOSE_FILE="docker-compose.yml"
            MODE_NAME="生产模式"
            generate_env_file
            ;;
        4)
            echo ""
            echo "可用的配置文件："
            ls docker-compose*.yml | nl
            read -p "请选择配置文件编号: " file_num
            COMPOSE_FILE=$(ls docker-compose*.yml | sed -n "${file_num}p")
            MODE_NAME="自定义模式 ($COMPOSE_FILE)"
            ;;
        *)
            COMPOSE_FILE="docker-compose.minimal.yml"
            MODE_NAME="快速体验模式"
            ;;
    esac
    
    print_info "已选择: $MODE_NAME"
}

# 构建和启动服务
start_services() {
    print_info "开始构建和启动服务..."
    
    # 检查是否有旧的容器运行
    if docker-compose -f "$COMPOSE_FILE" ps -q | grep -q .; then
        print_warning "检测到正在运行的容器"
        read -p "是否停止并重新启动？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose -f "$COMPOSE_FILE" down
        fi
    fi
    
    # 构建镜像
    print_info "构建Docker镜像..."
    docker-compose -f "$COMPOSE_FILE" build
    
    # 启动服务
    print_info "启动服务..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # 等待服务启动
    print_info "等待服务启动..."
    sleep 5
    
    # 检查服务状态
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_success "服务启动成功！"
    else
        print_error "服务启动失败，请检查日志"
        docker-compose -f "$COMPOSE_FILE" logs --tail=50
        exit 1
    fi
}

# 显示访问信息
show_access_info() {
    echo ""
    echo "============================================================"
    print_success "LIHC平台已成功启动！"
    echo "============================================================"
    echo ""
    echo "📊 主应用地址: http://localhost:8050"
    
    if [ "$COMPOSE_FILE" = "docker-compose.yml" ]; then
        echo "📈 Grafana监控: http://localhost:3000 (admin/admin)"
        echo "🔍 Prometheus: http://localhost:9090"
    fi
    
    echo ""
    echo "🛠️  常用命令："
    echo "  查看日志: docker-compose -f $COMPOSE_FILE logs -f"
    echo "  停止服务: docker-compose -f $COMPOSE_FILE down"
    echo "  重启服务: docker-compose -f $COMPOSE_FILE restart"
    echo "  查看状态: docker-compose -f $COMPOSE_FILE ps"
    echo ""
    echo "📖 使用说明："
    echo "  1. 打开浏览器访问 http://localhost:8050"
    echo "  2. 使用演示数据或上传自己的数据"
    echo "  3. 运行分析并查看结果"
    echo ""
    print_info "按 Ctrl+C 可以停止查看日志（服务会继续运行）"
}

# 查看日志
follow_logs() {
    read -p "是否查看实时日志？(y/n) [默认: y]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        docker-compose -f "$COMPOSE_FILE" logs -f
    fi
}

# 主函数
main() {
    show_banner
    check_requirements
    check_ports
    create_directories
    select_mode
    start_services
    show_access_info
    follow_logs
}

# 执行主函数
main