# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources')  # Add this line to include the resources folder
    ],
    hiddenimports=['PyQt6.sip'],  # Add common hidden imports for PyQt
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,        # Include binaries in the EXE
    a.zipfiles,        # Include zipfiles in the EXE
    a.datas,           # Include data in the EXE
    [],
    name='Poker Timer Monitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,  # Ensure everything runs from the exe
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources/icons/poker_timer_icon.png'],
)