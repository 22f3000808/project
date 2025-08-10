# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Paths
import os
client_dir = os.path.dirname(os.path.abspath(os.getcwd()))

a = Analysis(
    ['main.py'],  # Entry point
    pathex=[client_dir],
    binaries=[],
    datas=[
        # Include utility modules and configs
        ('utils.py', '.'),
        ('checks.py', '.'),
        ('daemon.py', '.'),
        ('*.json', '.'),
        ('*.sh', '.'),
        ('*.ps1', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='sysutil',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True  # Change to False for no console window
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='sysutil'
)
