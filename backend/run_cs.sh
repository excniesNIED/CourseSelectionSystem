#!/bin/bash

# 切换到 cs conda 环境并运行后端服务的脚本
echo "正在激活 cs conda 环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate cs

echo "环境信息:"
echo "Python: $(which python)"
echo "Python 版本: $(python --version)"
echo ""

# 清理缓存文件
echo "清理缓存文件..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# 检查数据库是否存在，如果不存在则创建
if [ ! -f "course_selection.db" ]; then
    echo "数据库不存在，正在创建数据库和初始化数据..."
    python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('数据库表创建完成')"
    
    echo "正在初始化数据..."
    curl -X POST http://localhost:5000/api/admin/init-data > /dev/null 2>&1 &
    sleep 2
fi

# 设置端口号，默认5000
PORT=${PORT:-5000}

echo "启动后端服务 (Flask Debug Mode)..."
echo "访问地址: http://localhost:$PORT"
echo "API文档: http://localhost:$PORT/apidocs/"
echo "按 Ctrl+C 停止服务"
echo ""
FLASK_ENV=development FLASK_DEBUG=1 python -c "
from app import create_app
import os
app = create_app()
app.run(host='0.0.0.0', port=$PORT, debug=True)
"
