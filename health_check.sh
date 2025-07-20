#!/bin/bash

# LIHC Dashboard 健康检查脚本

echo "🚀 LIHC Dashboard 健康检查"
echo "=========================="

# 检查容器状态
echo "📦 检查容器状态..."
docker-compose ps

echo ""
echo "🌐 测试服务访问性..."

# 测试Apple Dashboard
echo "🍎 Apple Dashboard (8052):"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8052)
if [ "$response" = "200" ]; then
    echo "   ✅ 正常运行"
else
    echo "   ❌ 访问失败 (HTTP $response)"
fi

# 测试Enhanced Dashboard
echo "📤 Enhanced Dashboard (8051):"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8051)
if [ "$response" = "200" ]; then
    echo "   ✅ 正常运行"
else
    echo "   ❌ 访问失败 (HTTP $response)"
fi

# 测试Original Dashboard
echo "📊 Original Dashboard (8050):"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8050)
if [ "$response" = "200" ]; then
    echo "   ✅ 正常运行"
else
    echo "   ❌ 访问失败 (HTTP $response)"
fi

# 测试Jupyter Lab
echo "🔬 Jupyter Lab (8888):"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8888)
if [ "$response" = "200" ] || [ "$response" = "302" ]; then
    echo "   ✅ 正常运行"
else
    echo "   ❌ 访问失败 (HTTP $response)"
fi

echo ""
echo "📝 访问地址汇总:"
echo "🍎 Apple Dashboard: http://localhost:8052 (推荐)"
echo "📤 Enhanced Dashboard: http://localhost:8051"
echo "📊 Original Dashboard: http://localhost:8050"
echo "🔬 Jupyter Lab: http://localhost:8888"

echo ""
echo "🎉 健康检查完成！"
echo "推荐访问: http://localhost:8052"