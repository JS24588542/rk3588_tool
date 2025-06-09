# RK3588 Monitor Makefile
.PHONY: help install build clean test run run-sudo dev

help:  ## 显示帮助信息
	@echo "RK3588 系统监控器 - 可用命令:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install:  ## 安装项目依赖
	uv sync

dev-install:  ## 安装开发依赖
	uv sync --group dev

build:  ## 构建wheel包
	uv build

build-exe:  ## 构建独立可执行文件
	uv run pyinstaller --onefile --name rk3588-monitor --console --clean main.py

run:  ## 运行监控器 (普通模式)
	uv run python main.py

run-sudo:  ## 以sudo运行监控器 (获取完整NPU功能)
	sudo uv run python main.py

run-exe:  ## 运行可执行文件
	./dist/rk3588-monitor

run-exe-sudo:  ## 以sudo运行可执行文件
	sudo ./dist/rk3588-monitor

test:  ## 测试程序 (5秒后自动退出)
	timeout 5s uv run python main.py || echo "测试完成"

clean:  ## 清理构建文件
	rm -rf build/ dist/ *.spec __pycache__/ .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

package:  ## 创建发布包 (包含源码、wheel和可执行文件)
	make clean
	make build
	make build-exe
	tar -czf rk3588-monitor-release.tar.gz dist/ README.md start.sh

info:  ## 显示项目信息
	@echo "项目名称: RK3588 系统监控器"
	@echo "版本: 0.1.0"
	@echo "Python版本: $$(python --version)"
	@echo "依赖状态:"
	@uv tree --quiet || echo "  未安装依赖，请运行 'make install'"
	@echo ""
	@if [ -f "dist/rk3588-monitor" ]; then \
		echo "可执行文件: dist/rk3588-monitor ($$(ls -lh dist/rk3588-monitor | awk '{print $$5}'))"; \
	else \
		echo "可执行文件: 未构建，请运行 'make build-exe'"; \
	fi
