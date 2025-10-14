# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for tsp_auto single executable
Includes all necessary dependencies for Selenium and webdriver-manager
"""

block_cipher = None

a = Analysis(
    ['browser_module.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        # Core modules
        'config',
        'logger',
        'error_codes',
        'tcp_server',
        'command_processor',
        'browser_manager',
        'automation_workflow',
        'response_handler',

        # Selenium dependencies
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.common',
        'selenium.webdriver.common.by',
        'selenium.webdriver.common.keys',
        'selenium.webdriver.support',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.options',
        'selenium.common',
        'selenium.common.exceptions',

        # webdriver-manager dependencies
        'webdriver_manager',
        'webdriver_manager.chrome',
        'webdriver_manager.core',

        # Standard library modules that might be missed
        'json',
        'socket',
        'threading',
        'queue',
        'argparse',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude test modules
        'tests',
        'test_unit_basic',
        'test_tcp_connection',
        'tcp_client_example',
        'mock_tcp_server',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='tsp_auto',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disabled for better Selenium compatibility and fewer AV false positives
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    # Additional Windows-specific options for better compatibility
    version=None,
    uac_admin=False,
    uac_uiaccess=False,
)
