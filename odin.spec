# -*- mode: python ; coding: utf-8 -*-
"""
ODIN v6.0 - PyInstaller Specification File
For building cross-platform executables, especially Windows .exe

Usage:
    pyinstaller odin.spec
"""

import os
from pathlib import Path

# Get the current directory
current_dir = Path.cwd()
odin_dir = current_dir / 'odin'

block_cipher = None

# Analysis phase - collect all Python files and dependencies
a = Analysis(
    [str(odin_dir / '__main__.py')],  # Entry point
    pathex=[str(current_dir)],
    binaries=[],
    datas=[
        # Include package data files
        (str(odin_dir / 'schemas'), 'odin/schemas'),
        (str(odin_dir / 'templates'), 'odin/templates') if (odin_dir / 'templates').exists() else None,
        # Include other data files if they exist
        ('requirements.txt', '.'),
        ('README.md', '.') if Path('README.md').exists() else None,
    ],
    hiddenimports=[
        'odin.cli',
        'odin.core', 
        'odin.instance',
        'odin.audit',
        'odin.backup',
        'click',
        'rich',
        'psutil',
        'filelock',
        'jsonschema',
        'yaml',
        'colorama',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',      # GUI library not needed
        'matplotlib',   # Plotting library not needed
        'numpy',        # Numerical library not needed unless specifically used
        'pandas',       # Data analysis library not needed
        'PIL',          # Image processing not needed
        'scipy',        # Scientific computing not needed
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove None entries from datas
a.datas = [item for item in a.datas if item is not None]

# PYZ phase - create Python archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE phase - create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='odin',
    debug=False,
    bootloader_ignore_signals=False,  
    strip=False,
    upx=True,  # Enable UPX compression for smaller file size
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console window for CLI application
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windows-specific options
    version='version_info.txt' if Path('version_info.txt').exists() else None,
    icon='odin.ico' if Path('odin.ico').exists() else None,
    # Add metadata
    uac_admin=False,  # Don't require admin privileges
    uac_uiaccess=False,
)
