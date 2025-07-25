#!/bin/bash

echo "🐳 LIHC Multi-dimensional Analysis Platform Docker 启动脚本"
echo "================================================================"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  端口 $port 已被占用"
        return 1
    else
        echo "✅ 端口 $port 可用"
        return 0
    fi
}

echo "🔍 检查环境..."

# 检查必要的端口
if ! check_port 8050; then
    echo "💡 您可以使用其他端口，比如 8051"
fi

echo "🏗️  开始构建和启动..."

# 选择运行模式
echo "请选择运行模式："
echo "1) 简化模式 (最小依赖，快速启动) - 推荐"
echo "2) 开发模式 (完整功能，启动较慢)"
echo "3) 生产模式 (完整服务栈，包含数据库等)"

read -p "请输入选择 (1-3): " choice

case $choice in
    1)
        echo "🚀 启动简化模式..."
        docker-compose -f docker-compose.minimal.yml up --build
        ;;
    2)
        echo "🛠️  启动开发模式..."
        docker-compose -f docker-compose.dev.yml up --build
        ;;
    3)
        echo "🏭 启动生产模式..."
        docker-compose up --build
        ;;
    *)
        echo "❌ 无效选择，启动简化模式..."
        docker-compose -f docker-compose.minimal.yml up --build
        ;;
esac

echo "🎉 启动完成!"
echo "📖 打开浏览器访问: http://localhost:8050"
echo "🛑 按 Ctrl+C 停止服务"