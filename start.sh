#!/bin/bash
# PicHome 图床系统启动脚本

cd /home/ubuntu/.openclaw/workspace/pichome

echo “🚀 启动 PicHome 图床系统...”
echo “📍 访问地址: http://$(hostname -I | awk '{print $1}'):5000”
echo “”

python3 app.py