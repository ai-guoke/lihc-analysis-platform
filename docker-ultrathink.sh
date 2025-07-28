#!/bin/bash

# ultrathink v2.7 Docker 管理脚本
# 肝细胞癌精准医疗分析平台

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="ultrathink"
VERSION="v2.7.0"
COMPOSE_FILE="docker-compose.yml"

# 打印标题
print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 ultrathink ${VERSION} Platform                 ║"
    echo "║           Liver Hepatocellular Carcinoma Analysis           ║"
    echo "║                  Docker Management Script                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 打印使用说明
show_help() {
    echo -e "${WHITE}使用方法:${NC}"
    echo "  $0 [command] [options]"
    echo ""
    echo -e "${WHITE}可用命令:${NC}"
    echo -e "  ${GREEN}start${NC}     - 启动ultrathink平台"
    echo -e "  ${GREEN}stop${NC}      - 停止ultrathink平台"
    echo -e "  ${GREEN}restart${NC}   - 重启ultrathink平台"
    echo -e "  ${GREEN}status${NC}    - 查看服务状态"
    echo -e "  ${GREEN}logs${NC}      - 查看服务日志"
    echo -e "  ${GREEN}build${NC}     - 构建Docker镜像"
    echo -e "  ${GREEN}clean${NC}     - 清理Docker资源"
    echo -e "  ${GREEN}update${NC}    - 更新并重启服务"
    echo -e "  ${GREEN}shell${NC}     - 进入容器Shell"
    echo -e "  ${GREEN}test${NC}      - 运行系统测试"
    echo -e "  ${GREEN}backup${NC}    - 备份数据"
    echo -e "  ${GREEN}restore${NC}   - 恢复数据"
    echo ""
    echo -e "${WHITE}服务选项:${NC}"
    echo -e "  ${YELLOW}--minimal${NC}     - 仅启动核心服务 (dashboard + api)"
    echo -e "  ${YELLOW}--full${NC}        - 启动全部服务 (包括数据库、监控)"
    echo -e "  ${YELLOW}--api-only${NC}    - 仅启动API服务"
    echo -e "  ${YELLOW}--dashboard-only${NC} - 仅启动Dashboard服务"
    echo ""
    echo -e "${WHITE}示例:${NC}"
    echo "  $0 start --minimal      # 启动核心服务"
    echo "  $0 logs ultrathink-api  # 查看API日志"
    echo "  $0 shell dashboard      # 进入Dashboard容器"
}

# 检查Docker环境
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker未安装${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}错误: Docker Compose未安装${NC}"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}错误: Docker服务未启动${NC}"
        exit 1
    fi
}

# 检查必要文件
check_files() {
    local missing_files=()
    
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        missing_files+=("$COMPOSE_FILE")
    fi
    
    if [[ ! -f "Dockerfile" ]]; then
        missing_files+=("Dockerfile")
    fi
    
    if [[ ! -f "Dockerfile.api" ]]; then
        missing_files+=("Dockerfile.api")
    fi
    
    if [[ ! -f "requirements.txt" ]]; then
        missing_files+=("requirements.txt")
    fi
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        echo -e "${RED}错误: 缺少必要文件:${NC}"
        printf '%s\n' "${missing_files[@]}"
        exit 1
    fi
}

# 创建必要目录
create_directories() {
    echo -e "${BLUE}创建必要目录...${NC}"
    
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
        "temp"
        "cache"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
    done
    
    echo -e "${GREEN}✓ 目录创建完成${NC}"
}

# 构建镜像
build_images() {
    echo -e "${BLUE}构建Docker镜像...${NC}"
    
    echo -e "${YELLOW}构建Dashboard镜像...${NC}"
    docker-compose build ultrathink-dashboard
    
    echo -e "${YELLOW}构建API镜像...${NC}"
    docker-compose build ultrathink-api
    
    echo -e "${GREEN}✓ 镜像构建完成${NC}"
}

# 启动服务
start_services() {
    local mode="$1"
    
    echo -e "${BLUE}启动ultrathink ${VERSION} 平台...${NC}"
    
    case "$mode" in
        "--minimal")
            echo -e "${YELLOW}启动模式: 最小化 (Dashboard + API + Redis)${NC}"
            docker-compose up -d ultrathink-dashboard ultrathink-api redis
            ;;
        "--full")
            echo -e "${YELLOW}启动模式: 完整 (所有服务)${NC}"
            docker-compose up -d
            ;;
        "--api-only")
            echo -e "${YELLOW}启动模式: 仅API服务${NC}"
            docker-compose up -d ultrathink-api redis
            ;;
        "--dashboard-only")
            echo -e "${YELLOW}启动模式: 仅Dashboard服务${NC}"
            docker-compose up -d ultrathink-dashboard
            ;;
        *)
            echo -e "${YELLOW}启动模式: 默认 (Dashboard + API + Redis)${NC}"
            docker-compose up -d ultrathink-dashboard ultrathink-api redis
            ;;
    esac
    
    echo -e "${GREEN}✓ 服务启动完成${NC}"
    
    # 等待服务就绪
    echo -e "${BLUE}等待服务就绪...${NC}"
    sleep 10
    
    # 显示访问信息
    show_access_info
}

# 停止服务
stop_services() {
    echo -e "${BLUE}停止ultrathink平台...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ 服务已停止${NC}"
}

# 重启服务
restart_services() {
    local mode="$1"
    echo -e "${BLUE}重启ultrathink平台...${NC}"
    stop_services
    sleep 3
    start_services "$mode"
}

# 查看服务状态
show_status() {
    echo -e "${BLUE}ultrathink平台服务状态:${NC}"
    docker-compose ps
    
    echo -e "\n${BLUE}容器资源使用情况:${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
        $(docker-compose ps -q 2>/dev/null) 2>/dev/null || echo "无运行中的容器"
}

# 查看日志
show_logs() {
    local service="$1"
    
    if [[ -z "$service" ]]; then
        echo -e "${BLUE}显示所有服务日志:${NC}"
        docker-compose logs -f --tail=100
    else
        echo -e "${BLUE}显示 $service 服务日志:${NC}"
        docker-compose logs -f --tail=100 "$service"
    fi
}

# 清理资源
clean_resources() {
    echo -e "${YELLOW}清理Docker资源...${NC}"
    
    # 停止所有容器
    docker-compose down
    
    # 删除未使用的镜像
    docker image prune -f
    
    # 删除未使用的卷（可选）
    read -p "是否删除数据卷? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        docker volume prune -f
    fi
    
    echo -e "${GREEN}✓ 清理完成${NC}"
}

# 进入容器Shell
enter_shell() {
    local service="$1"
    
    case "$service" in
        "dashboard"|"dash")
            service="ultrathink-dashboard"
            ;;
        "api")
            service="ultrathink-api"
            ;;
        "redis")
            service="ultrathink-redis"
            ;;
        "postgres"|"db")
            service="ultrathink-postgres"
            ;;
        "grafana")
            service="ultrathink-grafana"
            ;;
        "")
            service="ultrathink-dashboard"
            ;;
    esac
    
    echo -e "${BLUE}进入 $service 容器...${NC}"
    docker-compose exec "$service" /bin/bash || docker-compose exec "$service" /bin/sh
}

# 运行测试
run_tests() {
    echo -e "${BLUE}运行ultrathink系统测试...${NC}"
    
    # 确保服务运行
    if ! docker-compose ps | grep -q "Up"; then
        echo -e "${YELLOW}启动测试环境...${NC}"
        start_services "--minimal"
        sleep 15
    fi
    
    # 运行API测试
    echo -e "${YELLOW}运行API测试...${NC}"
    docker-compose exec ultrathink-api python test_unified_api.py
    
    # 运行Dashboard健康检查
    echo -e "${YELLOW}检查Dashboard健康状态...${NC}"
    curl -f http://localhost:8050/ > /dev/null && echo -e "${GREEN}✓ Dashboard正常${NC}" || echo -e "${RED}✗ Dashboard异常${NC}"
    
    # 运行API健康检查
    echo -e "${YELLOW}检查API健康状态...${NC}"
    curl -f http://localhost:8000/health > /dev/null && echo -e "${GREEN}✓ API正常${NC}" || echo -e "${RED}✗ API异常${NC}"
    
    echo -e "${GREEN}✓ 测试完成${NC}"
}

# 备份数据
backup_data() {
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    
    echo -e "${BLUE}备份数据到 $backup_dir...${NC}"
    
    mkdir -p "$backup_dir"
    
    # 备份数据目录
    if [[ -d "data" ]]; then
        cp -r data "$backup_dir/"
    fi
    
    # 备份结果目录
    if [[ -d "results" ]]; then
        cp -r results "$backup_dir/"
    fi
    
    # 备份配置文件
    if [[ -d "config" ]]; then
        cp -r config "$backup_dir/"
    fi
    
    # 创建备份信息文件
    cat > "$backup_dir/backup_info.txt" << EOF
Backup Date: $(date)
ultrathink Version: $VERSION
Docker Images:
$(docker images | grep ultrathink)

Running Containers:
$(docker-compose ps)
EOF
    
    echo -e "${GREEN}✓ 备份完成: $backup_dir${NC}"
}

# 恢复数据
restore_data() {
    local backup_dir="$1"
    
    if [[ -z "$backup_dir" ]]; then
        echo -e "${RED}错误: 请指定备份目录${NC}"
        echo "使用方法: $0 restore <backup_directory>"
        return 1
    fi
    
    if [[ ! -d "$backup_dir" ]]; then
        echo -e "${RED}错误: 备份目录 $backup_dir 不存在${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}从 $backup_dir 恢复数据...${NC}"
    
    # 停止服务
    stop_services
    
    # 恢复数据
    if [[ -d "$backup_dir/data" ]]; then
        rm -rf data
        cp -r "$backup_dir/data" .
    fi
    
    if [[ -d "$backup_dir/results" ]]; then
        rm -rf results  
        cp -r "$backup_dir/results" .
    fi
    
    if [[ -d "$backup_dir/config" ]]; then
        rm -rf config
        cp -r "$backup_dir/config" .
    fi
    
    echo -e "${GREEN}✓ 数据恢复完成${NC}"
    echo -e "${BLUE}重启服务...${NC}"
    start_services
}

# 显示访问信息
show_access_info() {
    echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}                   ultrathink ${VERSION} 访问信息${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    
    echo -e "\n${WHITE}🖥️  主要服务:${NC}"
    echo -e "  ${CYAN}Dashboard:${NC}     http://localhost:8050"
    echo -e "  ${CYAN}API Server:${NC}    http://localhost:8000"
    echo -e "  ${CYAN}API 文档:${NC}      http://localhost:8000/docs"
    echo -e "  ${CYAN}API ReDoc:${NC}     http://localhost:8000/redoc"
    
    if docker-compose ps nginx 2>/dev/null | grep -q "Up"; then
        echo -e "\n${WHITE}🌐 反向代理:${NC}"
        echo -e "  ${CYAN}Nginx:${NC}        http://localhost"
    fi
    
    if docker-compose ps postgres 2>/dev/null | grep -q "Up"; then
        echo -e "\n${WHITE}🗄️  数据库:${NC}"
        echo -e "  ${CYAN}PostgreSQL:${NC}   localhost:5432"
        echo -e "  ${CYAN}数据库名:${NC}     ultrathink_db"
        echo -e "  ${CYAN}用户名:${NC}       ultrathink_user"
    fi
    
    if docker-compose ps redis 2>/dev/null | grep -q "Up"; then
        echo -e "\n${WHITE}📦 缓存:${NC}"
        echo -e "  ${CYAN}Redis:${NC}        localhost:6379"
    fi
    
    if docker-compose ps grafana 2>/dev/null | grep -q "Up"; then
        echo -e "\n${WHITE}📊 监控:${NC}"
        echo -e "  ${CYAN}Grafana:${NC}      http://localhost:3000"
        echo -e "  ${CYAN}用户名:${NC}       admin"
        echo -e "  ${CYAN}密码:${NC}         ultrathink2025"
    fi
    
    echo -e "\n${WHITE}🔑 API认证令牌:${NC}"
    echo -e "  ${CYAN}管理员:${NC}       ultrathink_api_token_2025"
    echo -e "  ${CYAN}研究员:${NC}       research_token_2025"
    
    echo -e "\n${WHITE}🛠️  管理命令:${NC}"
    echo -e "  ${YELLOW}查看状态:${NC}     $0 status"
    echo -e "  ${YELLOW}查看日志:${NC}     $0 logs [service]"
    echo -e "  ${YELLOW}进入容器:${NC}     $0 shell [service]"
    echo -e "  ${YELLOW}运行测试:${NC}     $0 test"
    
    echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════${NC}"
}

# 更新服务
update_services() {
    echo -e "${BLUE}更新ultrathink平台...${NC}"
    
    # 拉取最新代码（如果是git仓库）
    if [[ -d ".git" ]]; then
        echo -e "${YELLOW}拉取最新代码...${NC}"
        git pull || echo -e "${YELLOW}警告: Git pull失败${NC}"
    fi
    
    # 重新构建镜像
    build_images
    
    # 重启服务
    restart_services
    
    echo -e "${GREEN}✓ 更新完成${NC}"
}

# 主函数
main() {
    print_header
    
    # 检查环境
    check_docker
    check_files
    create_directories
    
    local command="$1"
    local option="$2"
    
    case "$command" in
        "start")
            start_services "$option"
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services "$option"
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$option"
            ;;
        "build")
            build_images
            ;;
        "clean")
            clean_resources
            ;;
        "update")
            update_services
            ;;
        "shell")
            enter_shell "$option"
            ;;
        "test")
            run_tests
            ;;
        "backup")
            backup_data
            ;;
        "restore")
            restore_data "$option"
            ;;
        "help"|"--help"|"-h"|"")
            show_help
            ;;
        *)
            echo -e "${RED}错误: 未知命令 '$command'${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"