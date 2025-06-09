# 项目概览

## RK3588 系统监控器

这是一个专为RK3588 SoC设计的现代化系统监控工具，提供实时的硬件监控和可视化界面。

### 🎯 项目目标

- 实时监控RK3588芯片的温度、CPU、内存和NPU使用情况
- 提供类似bottom的历史数据图表显示
- 支持配置化的监控参数
- 提供独立的可执行文件便于部署

### 📁 项目结构

```
rk3588_tool/
├── main.py              # 主程序 - 包含所有监控逻辑和UI
├── config.toml          # 配置文件 - 可自定义监控参数
├── pyproject.toml       # 项目配置 - 依赖和构建设置
├── README.md            # 详细说明文档
├── Makefile             # 构建和管理命令
├── install.sh           # 自动安装脚本
├── start.sh             # 快速启动脚本
├── build_executable.py  # 可执行文件构建脚本
└── dist/
    ├── rk3588-monitor   # 独立可执行文件 (20MB)
    └── *.whl           # Python wheel包
```

### 🚀 快速开始

1. **自动安装** (推荐):
   ```bash
   ./install.sh
   ```

2. **手动安装**:
   ```bash
   # 安装依赖
   uv sync
   
   # 运行监控器
   uv run python main.py
   # 或
   ./start.sh
   ```

3. **使用可执行文件**:
   ```bash
   # 直接运行
   ./dist/rk3588-monitor
   
   # 获取完整功能 (包括NPU监控)
   sudo ./dist/rk3588-monitor
   ```

### 🛠️ 技术栈

- **UI框架**: [Textual](https://textual.textualize.io/) - 现代化终端用户界面
- **系统监控**: [psutil](https://psutil.readthedocs.io/) - 跨平台系统信息库
- **包管理**: [uv](https://astral.sh/uv/) - 现代Python包管理器
- **打包工具**: [PyInstaller](https://pyinstaller.org/) - Python可执行文件打包

### 🎛️ 监控功能

#### 温度监控
- 7个温度传感器实时监控
- 包括SoC中心、CPU大核、小核、GPU、NPU等
- 可配置的温度警告阈值
- 彩色显示温度状态

#### 系统监控
- CPU使用率监控
- 内存使用情况监控
- 历史数据图表 (最近1分钟)
- 可配置的警告阈值

#### NPU监控
- RK3588 NPU三核心使用率
- 需要sudo权限访问调试接口
- 实时负载显示

### ⚙️ 配置选项

编辑 `config.toml` 文件可以自定义:

- 数据更新间隔
- 历史数据长度
- 各种警告阈值
- 图表显示设置
- 传感器开关

### 🎨 界面特性

- **现代化UI**: 基于Textual的终端界面
- **实时更新**: 可配置的刷新间隔
- **历史图表**: ASCII字符绘制的趋势图
- **颜色编码**: 根据使用率/温度显示不同颜色
- **快捷键操作**: q退出、r刷新、c配置

### 📦 部署选项

1. **开发模式**: 使用uv运行Python脚本
2. **独立模式**: 20MB的单文件可执行程序
3. **包安装**: 通过pip安装wheel包
4. **系统集成**: 桌面快捷方式支持

### 🔒 权限要求

- **基本功能**: 普通用户权限
- **完整功能**: sudo权限 (NPU监控需要访问/sys/kernel/debug/rknpu/load)

### 🎯 适用场景

- RK3588开发板性能监控
- 系统温度管理
- NPU负载分析
- 系统性能调优
- 服务器监控

### 🔄 构建流程

项目支持多种构建方式:

```bash
# 使用Makefile
make install    # 安装依赖
make build     # 构建wheel包
make build-exe # 构建可执行文件
make clean     # 清理构建文件

# 手动构建
uv build                           # 构建wheel
uv run pyinstaller main.py        # 构建可执行文件
```

### 📊 性能特点

- **轻量级**: 最小化系统资源占用
- **高效**: 1秒更新间隔，响应迅速
- **稳定**: 异常处理完善，运行稳定
- **兼容**: 支持RK3588/RK3588S各种变体

这个项目展示了如何使用现代Python工具栈创建专业的系统监控应用，特别适合嵌入式Linux系统的监控需求。
