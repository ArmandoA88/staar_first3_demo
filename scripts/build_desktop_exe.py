from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from generate_tauri_icons import main as generate_tauri_icons
from packaged_runtime import ROOT, directory_size, format_size, stage_runtime_tree

BUILD_ROOT = ROOT / "build" / "desktop"
STAGED_RUNTIME_ROOT = BUILD_ROOT / "runtime"
PYINSTALLER_WORKPATH = BUILD_ROOT / "pyinstaller-work"
PYINSTALLER_SPECPATH = BUILD_ROOT / "pyinstaller-spec"
DIST_PATH = ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the STAAR Problem Browser desktop launcher EXE.")
    parser.add_argument("--grade", type=int, help="Only bundle collections for a single grade.")
    return parser.parse_args()


def resolve_app_name(grade: int | None) -> str:
    if grade is None:
        return "STAARProblemBrowser"
    return f"STAARProblemBrowserGrade{grade}"


def stage_runtime(*, grade: int | None) -> None:
    generate_tauri_icons()
    stage_runtime_tree(STAGED_RUNTIME_ROOT, grade=grade)


def build_executable(*, app_name: str) -> None:
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
        app_name,
        "--icon",
        str(ROOT / "src-tauri" / "icons" / "icon.ico"),
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
    args = parse_args()
    app_name = resolve_app_name(args.grade)
    stage_runtime(grade=args.grade)
    build_executable(app_name=app_name)

    exe_path = DIST_PATH / f"{app_name}.exe"
    runtime_size = directory_size(STAGED_RUNTIME_ROOT)
    print(f"Staged runtime: {STAGED_RUNTIME_ROOT}")
    if args.grade is None:
        print("Bundled scope: all grades")
    else:
        print(f"Bundled scope: grade {args.grade}")
    print(f"Staged runtime size: {format_size(runtime_size)}")
    print(f"Built executable: {exe_path}")
    if exe_path.exists():
        print(f"Executable size: {format_size(exe_path.stat().st_size)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
