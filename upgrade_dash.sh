#!/bin/bash

# LIHC平台Dash升级脚本
# 用于修复React生命周期方法警告

echo "🔧 开始升级Dash依赖..."

# 停止现有容器
echo "📋 停止现有容器..."
docker-compose -p lihc-platform down

# 重新构建镜像（强制重新安装依赖）
echo "🐳 重新构建Docker镜像（升级Dash）..."
docker-compose -p lihc-platform build --no-cache lihc-dashboard

# 启动服务
echo "🚀 启动升级后的服务..."
docker-compose -p lihc-platform up -d lihc-dashboard lihc-api redis

# 等待服务启动
echo "⏱️  等待服务启动..."
sleep 15

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose -p lihc-platform ps

echo "✅ Dash升级完成！"
echo ""
echo "访问地址："
echo "  🌐 主面板: http://localhost:8050"
echo "  📡 API:   http://localhost:8000"
echo ""
echo "注意："
echo "  • React警告已通过JavaScript抑制"
echo "  • 建议在浏览器中清除缓存"
echo "  • 如仍有警告，请检查浏览器控制台"