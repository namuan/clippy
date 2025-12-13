# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_clippy.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('clippy/data', 'clippy/data'),
        ('clippy/media', 'clippy/media'),
        ('assets', 'assets'),
    ],
    hiddenimports=[],
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
    name='Clippy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Clippy',
)
app = BUNDLE(
    coll,
    name='Clippy.app',
    icon='assets/icon.icns',
    bundle_identifier='com.namuan.clippy',
)
