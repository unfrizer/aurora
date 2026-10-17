"""PyInstaller one-folder specification for the existing AURORA launcher."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

root = Path.cwd()
analysis = Analysis(
    [str(root / "scripts" / "launcher_entry.py")],
    pathex=[str(root)],
    binaries=[],
    datas=[(str(root / "frontend" / "dist"), "frontend/dist")],
    hiddenimports=collect_submodules("uvicorn"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "pyright", "ruff"],
    noarchive=False,
)
pyz = PYZ(analysis.pure)
executable = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="AURORA",
    console=True,
    upx=False,
)
bundle = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name="AURORA",
)
