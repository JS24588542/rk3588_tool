#!/usr/bin/env python3
"""
构建可执行文件的脚本
使用PyInstaller将Python应用打包为独立的可执行文件
"""

import subprocess
import sys
from pathlib import Path


def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)


def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # PyInstaller参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 生成单个可执行文件
        "--name", "rk3588-monitor",     # 可执行文件名
        "--console",                    # 控制台应用
        "--clean",                      # 清理临时文件
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ 构建成功!")
        print("可执行文件位于: dist/rk3588-monitor")
        print("\n使用方法:")
        print("  ./dist/rk3588-monitor")
        print("\n注意: NPU监控需要sudo权限，建议以sudo运行:")
        print("  sudo ./dist/rk3588-monitor")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    try:
        install_pyinstaller()
        build_executable()
    except KeyboardInterrupt:
        print("\n用户取消构建")
    except Exception as e:
        print(f"构建过程中出现错误: {e}")
