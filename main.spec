# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Required Engine Binaries (libmpv, FFmpeg, D3DCompiler)
required_binaries = ['engine/libmpv-2.dll', 'engine/ffmpeg.exe', 'engine/D3DCompiler_47_cor3.dll']
engine_binaries = []
for binary in required_binaries:
    if not os.path.exists(binary):
        raise FileNotFoundError(f"Required engine binary not found: {binary}")
    engine_binaries.append((binary, 'engine'))

# Application Data Bundles
app_datas = [
    ('bingebox_icon.ico', '.'),
    ('THIRD_PARTY_LICENSES.txt', '.'),
    ('LICENSE', '.')
]

# Hidden Imports Specification
app_hiddenimports = [
    'mpv',
    'PySide6',
    'PySide6.QtNetwork',
    'shiboken6'
]

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=engine_binaries,
    datas=app_datas,
    hiddenimports=app_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'numpy', 'IPython'],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BingeBox',
    icon='bingebox_icon.ico',
    version='file_version_info.txt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='BingeBox',
)
