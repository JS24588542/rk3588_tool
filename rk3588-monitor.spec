# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('config.toml', '.')],  # 包含配置文件
    hiddenimports=[
        'textual',
        'textual.app',
        'textual.widgets',
        'psutil',
        'configparser',
        'threading',
        'time',
        'collections'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas'
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='rk3588-monitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # 启用strip减小文件大小
    upx=False,   # 关闭UPX，避免ARM64兼容性问题
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='aarch64',  # 明确指定ARM64架构
    codesign_identity=None,
    entitlements_file=None,
)