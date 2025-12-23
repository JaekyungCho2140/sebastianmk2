# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'pandas',
        'openpyxl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 테스트/개발 도구
        'pytest', '_pytest', 'py',
        'unittest', 'doctest',
        'pdb', 'bdb',

        # 과학/분석 라이브러리 (Sebastian에서 미사용)
        'scipy',
        'sklearn', 'scikit-learn',
        'matplotlib', 'mpl_toolkits',
        'PIL', 'Pillow',
        'numpy',  # pandas 의존성이지만 직접 사용 안 함

        # PyQt6 불필요 모듈
        'PyQt6.QtWebEngine', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtMultimedia', 'PyQt6.QtMultimediaWidgets',
        'PyQt6.Qt3DCore', 'PyQt6.Qt3DRender', 'PyQt6.Qt3DInput', 'PyQt6.Qt3DExtras',
        'PyQt6.QtBluetooth', 'PyQt6.QtNfc',
        'PyQt6.QtSerialPort',
        'PyQt6.QtPositioning', 'PyQt6.QtSensors',
        'PyQt6.QtQuick', 'PyQt6.QtQml',

        # 기타
        'tkinter',
        'IPython', 'jupyter', 'notebook',
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
    name='Sebastian',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 모드 (콘솔 숨김)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../Sebastian.ico' if __import__('pathlib').Path('../Sebastian.ico').exists() else None,
)
