#!/bin/bash

# Fix proxy settings for local development
export NO_PROXY="localhost,127.0.0.1,0.0.0.0"

echo "=== 🔧 ultrathink v2.7 代理修复 ==="
echo "已设置 NO_PROXY 环境变量以绕过本地服务代理"
echo ""
echo "🌐 可访问的服务："
echo "  • ultrathink 主面板: http://localhost:8050"
echo "  • ultrathink API:    http://localhost:8000"
echo "  • superbro 前端:     http://localhost:3000"
echo ""
echo "💡 如需永久生效，请在 ~/.zshrc 中添加："
echo "export NO_PROXY=\"localhost,127.0.0.1,0.0.0.0\""