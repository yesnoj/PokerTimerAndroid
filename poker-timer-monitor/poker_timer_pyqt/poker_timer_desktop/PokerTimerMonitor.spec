# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []

# Raccolta di tutte le dipendenze per Flask
flask_col = collect_all('flask')
datas.extend(flask_col[0])
binaries.extend(flask_col[1])
hiddenimports.extend(flask_col[2])

# Raccolta di tutte le dipendenze per PyQt6
pyqt_col = collect_all('PyQt6')
datas.extend(pyqt_col[0])
binaries.extend(pyqt_col[1])
hiddenimports.extend(pyqt_col[2])

# Raccolta per pyngrok (opzionale, se installato)
try:
    pyngrok_col = collect_all('pyngrok')
    datas.extend(pyngrok_col[0])
    binaries.extend(pyngrok_col[1])
    hiddenimports.extend(pyngrok_col[2])
except Exception:
    pass

# Raccolta per qrcode e dipendenze
try:
    qrcode_col = collect_all('qrcode')
    datas.extend(qrcode_col[0])
    binaries.extend(qrcode_col[1])
    hiddenimports.extend(qrcode_col[2])
    
    # PIL/Pillow è necessario per qrcode
    pil_col = collect_all('PIL')
    datas.extend(pil_col[0])
    binaries.extend(pil_col[1])
    hiddenimports.extend(pil_col[2])
except Exception:
    pass

# Aggiungi le risorse dell'applicazione
datas.append(('resources', 'resources'))

# Definisci altri import nascosti necessari
additional_hiddenimports = [
    'PyQt6.sip',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'socket',
    'threading',
    'datetime',
    'json',
    'flask',
    'logging',
    'io',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont'
]
hiddenimports.extend(additional_hiddenimports)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Poker Timer Monitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources/icons/poker_timer_icon.png'],
)
