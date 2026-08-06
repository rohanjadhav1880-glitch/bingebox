# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Lean Engine Binaries (Only active components: libmpv, FFmpeg, FFprobe, MediaInfo, D3DCompiler)
engine_binaries = [
    ('engine/libmpv-2.dll', 'engine'),
    ('engine/ffmpeg.exe', 'engine'),
    ('engine/ffprobe.exe', 'engine'),
    ('engine/MediaInfo.dll', 'engine'),
    ('engine/D3DCompiler_47_cor3.dll', 'engine')
]

# Application Data Bundles
app_datas = [
    ('bingebox_icon.ico', '.'),
    ('src/assets', 'src/assets'),
    ('public', 'public')
]

# Hidden Imports Specification
app_hiddenimports = [
    'mpv',
    'PySide6',
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
    excludes=[],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BingeBox',
    icon='bingebox_icon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
