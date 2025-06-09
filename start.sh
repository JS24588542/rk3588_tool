#!/bin/bash
# RK3588 Monitor 启动脚本

echo "🚀 启动 RK3588 系统监控器..."
echo "提示: 为了完整功能，建议使用 sudo 运行以获取NPU监控数据"
echo ""

# 检查是否有sudo权限来读取NPU数据
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  当前以普通用户身份运行"
    echo "   NPU监控可能无法正常工作"
    echo "   建议使用: sudo ./start.sh"
    echo ""
fi

# 检查是否在虚拟环境中
if [ -f ".venv/bin/activate" ]; then
    echo "📦 激活虚拟环境..."
    source .venv/bin/activate
fi

# 启动监控器
python main.py
