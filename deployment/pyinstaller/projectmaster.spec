# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for ProjectMaster Enterprise
Builds a standalone Windows EXE with embedded Streamlit server

Usage:
    pyinstaller deployment/pyinstaller/projectmaster.spec

Output:
    dist/ProjectMaster/ProjectMaster.exe (~600MB)
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all Streamlit data files
streamlit_datas = collect_data_files('streamlit', include_py_files=True)

# Collect all plotly data files
plotly_datas = collect_data_files('plotly')

# All hidden imports needed
hiddenimports = [
    'streamlit',
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.magic',
    'plotly',
    'plotly.express',
    'plotly.graph_objs',
    'pandas',
    'numpy',
    'PIL',
    'fpdf',
    'reportlab',
    'bcrypt',
    'cryptography',
    'openpyxl',
    'icalendar',
    'requests',
    'python-dateutil',
    'pytz',
] + collect_submodules('streamlit') + collect_submodules('plotly')

# Analysis
a = Analysis(
    ['../../project_app.py'],  # Main entry point
    pathex=[],
    binaries=[],
    datas=[
        ('../../*.py', '.'),  # All Python files
        ('../../data', 'data'),  # Data directory
        ('../../uploads', 'uploads'),  # Uploads directory
        ('../../project_images', 'project_images'),  # Images
        ('../../project_docs', 'project_docs'),  # Documents
        ('.streamlit/config.toml', '.streamlit'),  # Streamlit config
    ] + streamlit_datas + plotly_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ProjectMaster',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if sys.platform == 'win32' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ProjectMaster',
)
