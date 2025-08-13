#!/bin/bash

# LIHC Analysis Platform Docker Deployment Script
# 肝癌多维度预后分析平台部署脚本

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project Configuration
PROJECT_NAME="LIHC Analysis Platform"
VERSION="v2.5.0"
COMPOSE_PROJECT_NAME="lihc-platform"

echo -e "${BLUE}🧬 ===============================================${NC}"
echo -e "${BLUE}   ${PROJECT_NAME} ${VERSION}${NC}"
echo -e "${BLUE}   肝癌多维度预后分析平台${NC}"
echo -e "${BLUE}🧬 ===============================================${NC}"
echo ""

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}📋 $1${NC}"
}

# Check Docker and Docker Compose
check_dependencies() {
    print_info "检查依赖项..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    print_status "Docker和Docker Compose已安装"
}

# Stop existing containers
stop_existing_containers() {
    print_info "停止现有容器..."
    
    # Stop LIHC containers
    docker-compose -p $COMPOSE_PROJECT_NAME down 2>/dev/null || true
    
    # Stop any remaining ultrathink containers (cleanup)
    docker stop ultrathink-dashboard ultrathink-api ultrathink-redis ultrathink-nginx 2>/dev/null || true
    docker rm ultrathink-dashboard ultrathink-api ultrathink-redis ultrathink-nginx 2>/dev/null || true
    
    print_status "现有容器已停止"
}

# Build and start services
deploy_services() {
    print_info "构建和启动LIHC服务..."
    
    # Set environment variables
    export COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME
    
    # Build and start core services
    docker-compose up -d --build lihc-dashboard lihc-api redis
    
    print_status "核心服务已启动"
    
    # Wait for services to be ready
    print_info "等待服务启动..."
    sleep 10
    
    # Check service health
    check_service_health
}

# Check service health
check_service_health() {
    print_info "检查服务健康状态..."
    
    # Check dashboard
    if curl -f http://localhost:8050 >/dev/null 2>&1; then
        print_status "Dashboard (8050端口) 运行正常"
    else
        print_warning "Dashboard可能仍在启动中"
    fi
    
    # Check API
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_status "API (8000端口) 运行正常"
    else
        print_warning "API可能仍在启动中"
    fi
    
    # Check Redis
    if docker exec lihc-redis redis-cli ping >/dev/null 2>&1; then
        print_status "Redis运行正常"
    else
        print_warning "Redis可能仍在启动中"
    fi
}

# Show deployment summary
show_summary() {
    echo ""
    echo -e "${GREEN}🎉 ===============================================${NC}"
    echo -e "${GREEN}   LIHC平台部署完成！${NC}"
    echo -e "${GREEN}🎉 ===============================================${NC}"
    echo ""
    
    print_info "访问地址："
    echo "  🌐 LIHC主面板: http://localhost:8050"
    echo "  📡 API服务:   http://localhost:8000"
    echo "  📚 API文档:   http://localhost:8000/docs"
    echo ""
    
    print_info "核心功能："
    echo "  🔬 五维度肿瘤微环境分析"
    echo "  🕸️  分子网络分析"
    echo "  📈 生存分析系统"
    echo "  🎯 精准医学预测"
    echo ""
    
    print_info "管理命令："
    echo "  查看状态: docker-compose -p $COMPOSE_PROJECT_NAME ps"
    echo "  查看日志: docker logs lihc-dashboard"
    echo "  重启服务: docker restart lihc-dashboard"
    echo "  停止服务: docker-compose -p $COMPOSE_PROJECT_NAME down"
    echo ""
    
    print_warning "重要提示："
    echo "  如果遇到访问问题，请检查防火墙设置"
    echo "  首次启动可能需要几分钟时间完成初始化"
}

# Main deployment process
main() {
    check_dependencies
    stop_existing_containers
    deploy_services
    show_summary
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        print_info "停止LIHC平台..."
        docker-compose -p $COMPOSE_PROJECT_NAME down
        print_status "LIHC平台已停止"
        ;;
    "restart")
        print_info "重启LIHC平台..."
        docker-compose -p $COMPOSE_PROJECT_NAME restart
        print_status "LIHC平台已重启"
        ;;
    "status")
        print_info "LIHC平台状态："
        docker-compose -p $COMPOSE_PROJECT_NAME ps
        ;;
    "logs")
        print_info "显示服务日志："
        docker-compose -p $COMPOSE_PROJECT_NAME logs -f
        ;;
    *)
        echo "用法: $0 [deploy|stop|restart|status|logs]"
        echo ""
        echo "命令说明："
        echo "  deploy  - 部署LIHC平台（默认）"
        echo "  stop    - 停止所有服务"
        echo "  restart - 重启所有服务"
        echo "  status  - 查看服务状态"
        echo "  logs    - 查看服务日志"
        exit 1
        ;;
esac