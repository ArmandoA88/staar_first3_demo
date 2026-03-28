from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from packaged_runtime import ROOT, directory_size, format_size, stage_runtime_tree

APP_NAME = "STAARProblemBrowser"
BUILD_ROOT = ROOT / "build" / "desktop"
STAGED_RUNTIME_ROOT = BUILD_ROOT / "runtime"
PYINSTALLER_WORKPATH = BUILD_ROOT / "pyinstaller-work"
PYINSTALLER_SPECPATH = BUILD_ROOT / "pyinstaller-spec"
DIST_PATH = ROOT


def stage_runtime() -> None:
    stage_runtime_tree(STAGED_RUNTIME_ROOT)


def build_executable() -> None:
    DIST_PATH.mkdir(parents=True, exist_ok=True)
    PYINSTALLER_WORKPATH.mkdir(parents=True, exist_ok=True)
    PYINSTALLER_SPECPATH.mkdir(parents=True, exist_ok=True)

    add_data_value = f"{STAGED_RUNTIME_ROOT}{os.pathsep}runtime"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        APP_NAME,
        "--distpath",
        str(DIST_PATH),
        "--workpath",
        str(PYINSTALLER_WORKPATH),
        "--specpath",
        str(PYINSTALLER_SPECPATH),
        "--add-data",
        add_data_value,
        str(ROOT / "desktop_launcher.py"),
    ]
    subprocess.run(command, check=True)


def main() -> int:
    stage_runtime()
    build_executable()

    exe_path = DIST_PATH / f"{APP_NAME}.exe"
    runtime_size = directory_size(STAGED_RUNTIME_ROOT)
    print(f"Staged runtime: {STAGED_RUNTIME_ROOT}")
    print(f"Staged runtime size: {format_size(runtime_size)}")
    print(f"Built executable: {exe_path}")
    if exe_path.exists():
        print(f"Executable size: {format_size(exe_path.stat().st_size)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
