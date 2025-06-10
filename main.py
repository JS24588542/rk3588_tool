#!/usr/bin/env python3
"""
RK3588 System Monitor - A Textual-based monitoring tool for RK3588 SoC
Monitors temperature, CPU, memory, and NPU usage with real-time graphs
"""

import os
import subprocess
import configparser
from collections import deque
from typing import Dict, List, Optional

import psutil
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Header, Footer, Static


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = "config.toml"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        # 设置默认值
        self.config.read_dict({
            'monitor': {
                'update_interval': '1.0',
                'history_length': '60',
                'temp_warning_threshold': '60.0',
                'temp_critical_threshold': '70.0',
                'cpu_warning_threshold': '70.0',
                'cpu_critical_threshold': '90.0',
                'memory_warning_threshold': '80.0',
                'memory_critical_threshold': '95.0',
                'npu_warning_threshold': '70.0',
                'npu_critical_threshold': '90.0'
            },
            'display': {
                'graph_width': '20',
                'use_colors': 'true',
                'show_history_graphs': 'true'
            },
            'sensors': {
                'enable_temperature': 'true',
                'enable_npu': 'true'
            }
        })
        
        # 如果配置文件存在，则读取
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file)
            except Exception as e:
                print(f"警告: 无法读取配置文件 {self.config_file}: {e}")
    
    def get_float(self, section: str, key: str) -> float:
        """获取浮点数配置值"""
        return self.config.getfloat(section, key)
    
    def get_int(self, section: str, key: str) -> int:
        """获取整数配置值"""
        return self.config.getint(section, key)
    
    def get_bool(self, section: str, key: str) -> bool:
        """获取布尔配置值"""
        return self.config.getboolean(section, key)
    
    def get_str(self, section: str, key: str) -> str:
        """获取字符串配置值"""
        return self.config.get(section, key)


class ThermalZoneReader:
    """读取RK3588温度传感器数据"""
    
    def __init__(self, config: Config):
        self.config = config
        self.THERMAL_ZONES = {
            0: "SoC中心",
            1: "A76_0/1(CPU4/5)",
            2: "A76_2/3(CPU6/7)",
            3: "A55_0/1/2/3(CPU0-3)",
            4: "PD_CENTER",
            5: "GPU",
            6: "NPU"
        }
    
    def read_temperature(self, zone: int) -> Optional[float]:
        """读取指定温度区域的温度（摄氏度）"""
        if not self.config.get_bool('sensors', 'enable_temperature'):
            return None
            
        try:
            thermal_path = f"/sys/class/thermal/thermal_zone{zone}/temp"
            if os.path.exists(thermal_path):
                with open(thermal_path, 'r') as f:
                    temp_millidegree = int(f.read().strip())
                    return temp_millidegree / 1000.0
        except (FileNotFoundError, ValueError, PermissionError):
            pass
        return None
    
    def read_all_temperatures(self) -> Dict[str, float]:
        """读取所有温度传感器数据"""
        temps = {}
        for zone, name in self.THERMAL_ZONES.items():
            temp = self.read_temperature(zone)
            if temp is not None:
                temps[name] = temp
        return temps
    
    def get_temp_color(self, temp: float) -> str:
        """根据温度返回颜色"""
        warning_threshold = self.config.get_float('monitor', 'temp_warning_threshold')
        critical_threshold = self.config.get_float('monitor', 'temp_critical_threshold')
        
        if temp > critical_threshold:
            return "red"
        elif temp > warning_threshold:
            return "yellow"
        else:
            return "green"


class NPUReader:
    """读取RK3588 NPU使用率数据"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def read_npu_load(self) -> Dict[str, float]:
        """读取NPU负载，需要sudo权限"""
        if not self.config.get_bool('sensors', 'enable_npu'):
            return {"Core0": 0.0, "Core1": 0.0, "Core2": 0.0}
            
        try:
            result = subprocess.run(
                ['sudo', 'cat', '/sys/kernel/debug/rknpu/load'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                # 解析输出格式: "NPU load: Core0: 0%, Core1: 0%, Core2: 0%,"
                output = result.stdout.strip()
                npu_loads = {}
                
                if "NPU load:" in output:
                    parts = output.split("NPU load:")[1].strip()
                    for part in parts.split(','):
                        if ':' in part:
                            core_info = part.strip()
                            if core_info:
                                core_name, load_str = core_info.split(':')
                                load_val = float(load_str.strip().rstrip('%'))
                                npu_loads[core_name.strip()] = load_val
                
                return npu_loads
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
            pass
        
        return {"Core0": 0.0, "Core1": 0.0, "Core2": 0.0}
    
    def get_npu_color(self, load: float) -> str:
        """根据NPU负载返回颜色"""
        warning_threshold = self.config.get_float('monitor', 'npu_warning_threshold')
        critical_threshold = self.config.get_float('monitor', 'npu_critical_threshold')
        
        if load > critical_threshold:
            return "red"
        elif load > warning_threshold:
            return "yellow"
        else:
            return "green"


class GraphWidget(Widget):
    """图形显示组件，显示历史数据曲线"""
    
    def __init__(self, title: str, max_points: int = 60, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.data_points = deque(maxlen=max_points)
        self.max_value = 100.0
        self.min_value = 0.0
    
    def add_data_point(self, value: float):
        """添加数据点"""
        self.data_points.append(value)
        if value > self.max_value:
            self.max_value = value * 1.1
        self.refresh()
    
    def render(self) -> str:
        """渲染图形"""
        if not self.data_points:
            return f"[bold]{self.title}[/bold]\n无数据"
        
        width = max(50, len(self.data_points))
        height = 8
        
        # 创建图形网格
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # 绘制数据点
        if len(self.data_points) > 1:
            for i, value in enumerate(self.data_points):
                if i < width:
                    # 将值映射到网格高度
                    normalized = (value - self.min_value) / (self.max_value - self.min_value) if self.max_value > self.min_value else 0
                    y = int((1 - normalized) * (height - 1))
                    y = max(0, min(height - 1, y))
                    grid[y][i] = '█'
        
        # 转换为字符串
        lines = []
        current_val = self.data_points[-1] if self.data_points else 0
        lines.append(f"[bold]{self.title}[/bold] 当前: {current_val:.1f}")
        lines.append(f"最大: {self.max_value:.1f}")
        
        for row in grid:
            lines.append(''.join(row))
        
        lines.append(f"最小: {self.min_value:.1f}")
        
        return '\n'.join(lines)


class SystemInfoWidget(Static):
    """系统信息显示组件"""
    
    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.thermal_reader = ThermalZoneReader(config)
        self.npu_reader = NPUReader(config)
        
        # 历史数据存储
        history_length = self.config.get_int('monitor', 'history_length')
        self.cpu_history = deque(maxlen=history_length)
        self.memory_history = deque(maxlen=history_length)
        self.temp_history = {name: deque(maxlen=history_length) for name in self.thermal_reader.THERMAL_ZONES.values()}
        self.npu_history = {"Core0": deque(maxlen=history_length), "Core1": deque(maxlen=history_length), "Core2": deque(maxlen=history_length)}
    
    def update_data(self):
        """更新所有监控数据"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=None)
        self.cpu_history.append(cpu_percent)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        self.memory_history.append(memory.percent)
        
        # 温度数据
        temperatures = self.thermal_reader.read_all_temperatures()
        for name, temp in temperatures.items():
            if name in self.temp_history:
                self.temp_history[name].append(temp)
        
        # NPU使用率
        npu_loads = self.npu_reader.read_npu_load()
        for core, load in npu_loads.items():
            if core in self.npu_history:
                self.npu_history[core].append(load)
        
        # 更新显示
        self.render_info()
    
    def get_cpu_color(self, cpu_percent: float) -> str:
        """根据CPU使用率返回颜色"""
        warning_threshold = self.config.get_float('monitor', 'cpu_warning_threshold')
        critical_threshold = self.config.get_float('monitor', 'cpu_critical_threshold')
        
        if cpu_percent > critical_threshold:
            return "red"
        elif cpu_percent > warning_threshold:
            return "yellow"
        else:
            return "green"
    
    def get_memory_color(self, memory_percent: float) -> str:
        """根据内存使用率返回颜色"""
        warning_threshold = self.config.get_float('monitor', 'memory_warning_threshold')
        critical_threshold = self.config.get_float('monitor', 'memory_critical_threshold')
        
        if memory_percent > critical_threshold:
            return "red"
        elif memory_percent > warning_threshold:
            return "yellow"
        else:
            return "green"
    
    def get_trend_indicator(self, data: List[float]) -> str:
        """获取趋势指示器"""
        if len(data) < 2:
            return ""
        
        current = data[-1]
        previous = data[-2]
        
        if current > previous + 1:
            return "↗"
        elif current < previous - 1:    
            return "↘"
        else:
            return "→"
    
    def get_avg_and_trend(self, data: List[float]) -> tuple:
        """获取平均值和趋势"""
        if len(data) < 2:
            return 0.0, ""
        
        # 最近5个数据点的平均值
        recent_data = data[-5:]
        avg = sum(recent_data) / len(recent_data)
        trend = self.get_trend_indicator(data)
        
        return avg, trend

    def render_info(self):
        """渲染系统信息"""
        lines = []
        display_mode = self.config.get_str('display', 'display_mode') if self.config.config.has_option('display', 'display_mode') else 'trend'
        show_trends = display_mode == 'trend' and self.config.get_bool('display', 'show_history_graphs')
        
        # CPU信息
        cpu_current = self.cpu_history[-1] if self.cpu_history else 0
        cpu_color = self.get_cpu_color(cpu_current)
        cpu_line = f"[bold {cpu_color}]💻 CPU使用率: {cpu_current:.1f}%[/bold {cpu_color}]"
        
        if show_trends and len(self.cpu_history) >= 2:
            cpu_avg, cpu_trend = self.get_avg_and_trend(list(self.cpu_history))
            cpu_line += f"  [dim](平均: {cpu_avg:.1f}% {cpu_trend})[/dim]"
        
        lines.append(cpu_line)
        
        # 内存信息  
        memory = psutil.virtual_memory()
        memory_color = self.get_memory_color(memory.percent)
        mem_line = f"[bold {memory_color}]🧠 内存使用: {memory.percent:.1f}% ({memory.used//1024//1024}MB/{memory.total//1024//1024}MB)[/bold {memory_color}]"
        
        if show_trends and len(self.memory_history) >= 2:
            mem_avg, mem_trend = self.get_avg_and_trend(list(self.memory_history))
            mem_line += f"  [dim](平均: {mem_avg:.1f}% {mem_trend})[/dim]"
            
        lines.append(mem_line)
        lines.append("")
        
        # 温度信息
        if self.config.get_bool('sensors', 'enable_temperature'):
            lines.append("[bold red]🌡️  芯片温度:[/bold red]")
            temperatures = self.thermal_reader.read_all_temperatures()
            
            # 按重要性排序显示
            temp_order = [
                ("SoC中心", "🔥"),
                ("A76_0/1(CPU4/5)", "🔴"), 
                ("A76_2/3(CPU6/7)", "🔴"),
                ("A55_0/1/2/3(CPU0-3)", "🟡"),
                ("GPU", "🎮"),
                ("NPU", "🧠"),
                ("PD_CENTER", "⚙️")
            ]
            
            for name, icon in temp_order:
                if name in temperatures:
                    temp = temperatures[name]
                    color = self.thermal_reader.get_temp_color(temp)
                    temp_line = f"  {icon} [{color}]{name}: {temp:.1f}°C[/{color}]"
                    
                    if show_trends and len(self.temp_history[name]) >= 2:
                        temp_avg, temp_trend = self.get_avg_and_trend(list(self.temp_history[name]))
                        temp_line += f"  [dim](平均: {temp_avg:.1f}°C {temp_trend})[/dim]"
                    
                    lines.append(temp_line)
        
        lines.append("")
        
        # NPU信息
        if self.config.get_bool('sensors', 'enable_npu'):
            lines.append("[bold magenta]🚀 NPU使用率:[/bold magenta]")
            npu_loads = self.npu_reader.read_npu_load()
            
            for core, load in npu_loads.items():
                color = self.npu_reader.get_npu_color(load)
                npu_line = f"  🔹 [{color}]{core}: {load:.1f}%[/{color}]"
                
                if show_trends and len(self.npu_history[core]) >= 2:
                    npu_avg, npu_trend = self.get_avg_and_trend(list(self.npu_history[core]))
                    npu_line += f"  [dim](平均: {npu_avg:.1f}% {npu_trend})[/dim]"
                
                lines.append(npu_line)
        
        self.update('\n'.join(lines))


class RK3588Monitor(App):
    """RK3588系统监控主应用"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    SystemInfoWidget {
        border: solid $primary;
        padding: 1;
        margin: 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "退出"),
        ("r", "refresh", "刷新"),
        ("t", "toggle_trends", "切换趋势显示"),
        ("s", "toggle_simple", "简洁模式"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = Config()
    
    def compose(self) -> ComposeResult:
        """组合界面组件"""
        yield Header()
        yield Container(
            SystemInfoWidget(self.config, id="system_info"),
            id="main_container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """应用启动时的初始化"""
        self.title = "RK3588 系统监控器"
        self.sub_title = "实时监控温度、CPU、内存、NPU"
        
        # 从配置获取更新间隔
        update_interval = self.config.get_float('monitor', 'update_interval')
        self.set_interval(update_interval, self.update_system_info)
    
    def update_system_info(self) -> None:
        """更新系统信息"""
        system_widget = self.query_one("#system_info", SystemInfoWidget)
        system_widget.update_data()
    
    def action_refresh(self) -> None:
        """手动刷新"""
        self.update_system_info()
    
    def action_toggle_trends(self) -> None:
        """切换趋势显示"""
        current = self.config.get_bool('display', 'show_history_graphs')
        # 动态更新配置（仅在当前会话中）
        self.config.config.set('display', 'show_history_graphs', str(not current))
        self.update_system_info()
        mode = "开启" if not current else "关闭"
        self.notify(f"趋势显示已{mode}")
    
    def action_toggle_simple(self) -> None:
        """切换简洁模式"""
        current_mode = self.config.get_str('display', 'display_mode') if self.config.config.has_option('display', 'display_mode') else 'trend'
        new_mode = 'simple' if current_mode == 'trend' else 'trend'
        self.config.config.set('display', 'display_mode', new_mode)
        self.update_system_info()
        self.notify(f"切换到{'简洁' if new_mode == 'simple' else '详细'}模式")


def main():
    """主函数"""
    app = RK3588Monitor()
    app.run()


if __name__ == "__main__":
    main()
