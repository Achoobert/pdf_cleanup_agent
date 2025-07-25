# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Get the base directory
base_dir = os.path.abspath('.')

# Collect all data files from the data directory
data_files = []
data_dir = os.path.join(base_dir, 'data')
if os.path.exists(data_dir):
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if not file.startswith('.'):  # Skip hidden files
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, base_dir)
                data_files.append((src_path, os.path.dirname(rel_path)))

# Collect prompts directory
prompts_dir = os.path.join(base_dir, 'prompts')
if os.path.exists(prompts_dir):
    for root, dirs, files in os.walk(prompts_dir):
        for file in files:
            if not file.startswith('.'):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, base_dir)
                data_files.append((src_path, os.path.dirname(rel_path)))

# Add configuration files
config_files = ['pipeline_config.yml', 'config.yml']
for config_file in config_files:
    if os.path.exists(config_file):
        data_files.append((config_file, '.'))

# Hidden imports for PyQt5 and other dependencies
hidden_imports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'PyQt5.sip',
    'requests',
    'psutil',
    'yaml',
    'logging',
    'argparse',
    'traceback',
    'dataclasses',
    'typing',
]

# Collect all submodules from our scripts
hidden_imports.extend(collect_submodules('scripts.ui'))

a = Analysis(
    ['scripts/ui/main.py'],
    pathex=[base_dir],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PDFCleanupAgent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PDFCleanupAgent',
)

# macOS App Bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='PDF Cleanup Agent.app',
        icon='assets/icon.icns' if os.path.exists('assets/icon.icns') else None,
        bundle_identifier='com.pdfcleanupagent.app',
        version='1.0.0',
        info_plist={
            'CFBundleName': 'PDF Cleanup Agent',
            'CFBundleDisplayName': 'PDF Cleanup Agent',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleIdentifier': 'com.pdfcleanupagent.app',
            'CFBundleExecutable': 'PDFCleanupAgent',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': 'PDFC',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'LSMinimumSystemVersion': '10.13.0',
            'NSHumanReadableCopyright': 'Copyright © 2025 PDF Cleanup Agent',
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeExtensions': ['pdf'],
                    'CFBundleTypeName': 'PDF Document',
                    'CFBundleTypeRole': 'Editor',
                    'LSHandlerRank': 'Alternate',
                }
            ],
        },
    )