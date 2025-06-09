#!/bin/bash
# RK3588监控器安装脚本

set -e

echo "🚀 RK3588 系统监控器安装脚本"
echo "=================================="

# 检查是否为RK3588系统
check_rk3588() {
    if [ ! -d "/sys/class/thermal" ]; then
        echo "⚠️  警告: 未找到温度传感器目录，可能不是RK3588系统"
    fi
    
    if [ ! -f "/sys/kernel/debug/rknpu/load" ]; then
        echo "⚠️  警告: 未找到NPU调试文件，NPU监控可能不可用"
        echo "   请确保以sudo权限运行监控器"
    fi
}

# 检查Python版本
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "❌ 错误: 未找到Python3"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "✅ Python版本: $python_version"
}

# 检查uv包管理器
check_uv() {
    if ! command -v uv &> /dev/null; then
        echo "📦 安装uv包管理器..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source ~/.bashrc
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    echo "✅ uv包管理器已安装"
}

# 安装依赖
install_dependencies() {
    echo "📦 安装项目依赖..."
    uv sync
    echo "✅ 依赖安装完成"
}

# 构建可执行文件
build_executable() {
    echo "🔨 构建可执行文件..."
    uv sync --group dev
    uv run pyinstaller --onefile --name rk3588-monitor --console --clean main.py
    echo "✅ 可执行文件构建完成"
}

# 设置权限
setup_permissions() {
    echo "🔐 设置文件权限..."
    chmod +x start.sh
    chmod +x dist/rk3588-monitor 2>/dev/null || true
    echo "✅ 权限设置完成"
}

# 创建桌面快捷方式 (可选)
create_desktop_entry() {
    if command -v desktop-file-install &> /dev/null; then
        echo "🖥️  创建桌面快捷方式..."
        cat > rk3588-monitor.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=RK3588 Monitor
Comment=RK3588 System Monitor
Exec=$(pwd)/dist/rk3588-monitor
Icon=utilities-system-monitor
Terminal=true
Categories=System;Monitor;
EOF
        desktop-file-install --dir=$HOME/.local/share/applications rk3588-monitor.desktop
        rm rk3588-monitor.desktop
        echo "✅ 桌面快捷方式已创建"
    fi
}

# 显示使用说明
show_usage() {
    echo ""
    echo "🎉 安装完成!"
    echo ""
    echo "使用方法:"
    echo "  直接运行:     uv run python main.py"
    echo "  使用脚本:     ./start.sh"
    echo "  可执行文件:   ./dist/rk3588-monitor"
    echo ""
    echo "获取完整功能 (包括NPU监控):"
    echo "  sudo uv run python main.py"
    echo "  sudo ./dist/rk3588-monitor"
    echo ""
    echo "配置文件: config.toml"
    echo "可以编辑此文件来自定义监控参数"
    echo ""
    echo "快捷键:"
    echo "  q - 退出"
    echo "  r - 刷新"
    echo "  c - 配置信息"
}

# 主安装流程
main() {
    check_rk3588
    check_python
    check_uv
    install_dependencies
    build_executable
    setup_permissions
    create_desktop_entry
    show_usage
}

# 运行安装
main "$@"
