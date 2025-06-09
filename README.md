# RK3588 系统监控器

一个基于Textual框架的RK3588 SoC系统监控工具，提供实时的温度、CPU、内存和NPU使用情况监控，包含历史数据图表显示。

## 功能特性

- 🌡️ **温度监控**: 监控RK3588的7个温度传感器
  - SoC中心温度
  - A76_0/1 (CPU4/5) 大核温度
  - A76_2/3 (CPU6/7) 大核温度
  - A55_0/1/2/3 (CPU0-3) 小核温度
  - PD_CENTER温度
  - GPU温度
  - NPU温度

- 💻 **CPU监控**: 实时CPU使用率
- 🧠 **内存监控**: 内存使用情况和统计
- 🚀 **NPU监控**: RK3588 NPU三个核心的使用率
- 📊 **历史数据**: 显示最近1分钟的历史趋势图表
- 🎨 **现代界面**: 基于Textual的终端UI

## 系统要求

- RK3588/RK3588S 开发板
- Python 3.13+
- Linux 系统
- 对于NPU监控需要sudo权限

## 安装和使用

### 方法1: 使用UV包管理器 (推荐)

```bash
# 确保已安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆或下载项目
cd rk3588_tool

# 安装依赖
uv sync

# 运行监控器
uv run python main.py

# 或者使用启动脚本
./start.sh

# 如需NPU监控，请使用sudo
sudo uv run python main.py
```

### 方法2: 构建独立可执行文件

```bash
# 构建可执行文件
python build_executable.py

# 运行可执行文件
./dist/rk3588-monitor

# 或者以sudo运行以获取完整功能
sudo ./dist/rk3588-monitor
```

### 方法3: 传统Python环境

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install psutil textual

# 运行
python main.py
```

## 监控数据说明

### 温度传感器位置对应
- `thermal_zone0`: SoC中心位置
- `thermal_zone1`: CPU大核A76_0/1 (CPU4和CPU5)
- `thermal_zone2`: CPU大核A76_2/3 (CPU6和CPU7) 
- `thermal_zone3`: CPU小核A55_0/1/2/3 (CPU0、CPU1、CPU2、CPU3)
- `thermal_zone4`: PD_CENTER
- `thermal_zone5`: GPU
- `thermal_zone6`: NPU

### NPU监控
NPU监控需要读取 `/sys/kernel/debug/rknpu/load`，该文件需要sudo权限访问。
输出格式: `NPU load: Core0: 0%, Core1: 0%, Core2: 0%`

## 界面操作

- `q` - 退出程序
- `r` - 手动刷新数据
- 程序每秒自动更新一次数据

## 项目结构

```
rk3588_tool/
├── main.py              # 主程序文件
├── pyproject.toml       # 项目配置
├── start.sh            # 启动脚本
├── build_executable.py # 构建可执行文件脚本
├── README.md           # 说明文档
└── dist/               # 构建输出目录
    └── rk3588-monitor  # 可执行文件
```

## 技术实现

- **Textual**: 现代终端用户界面框架
- **psutil**: 系统和进程信息获取
- **异步更新**: 实时数据刷新
- **历史数据**: 使用deque存储最近60个数据点
- **图形显示**: ASCII字符图表显示趋势

## 注意事项

1. NPU监控功能需要sudo权限
2. 确保系统中存在对应的thermal_zone文件
3. 某些传感器在不同RK3588变体上可能不可用
4. 建议在RK3588开发板上运行，其他平台可能缺少相应的传感器文件

## 故障排除

### NPU数据无法读取
```bash
# 检查NPU调试文件是否存在
ls -la /sys/kernel/debug/rknpu/

# 使用sudo运行程序
sudo ./rk3588-monitor
```

### 温度数据无法读取
```bash
# 检查温度传感器文件
ls -la /sys/class/thermal/thermal_zone*/temp
```

## 许可证

本项目使用MIT许可证。