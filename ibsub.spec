# -*- mode: python -*-

# A specification file for PyInstaller which creates a single executable.
#
# Run with:
#
#    python /path/to/pyinstaller.py ibsub.spec
#
# This will produce a `dist' directory which contains the executable.

a = Analysis(
    ['lsf_ibutils/ibsub/main.py'],
    pathex=['.'],
    hiddenimports=[],
    hookspath=None,
    runtime_hooks=None,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='ibsub',
    debug=False,
    strip=None,
    upx=True,
    console=True,
)
