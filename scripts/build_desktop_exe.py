from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "STAARProblemBrowser"
ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = ROOT / "build" / "desktop"
STAGED_RUNTIME_ROOT = BUILD_ROOT / "runtime"
PYINSTALLER_WORKPATH = BUILD_ROOT / "pyinstaller-work"
PYINSTALLER_SPECPATH = BUILD_ROOT / "pyinstaller-spec"
DIST_PATH = ROOT


def remove_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_tree(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, dirs_exist_ok=True)


def stage_core_app_files() -> None:
    copy_file(ROOT / "index.html", STAGED_RUNTIME_ROOT / "index.html")
    copy_tree(ROOT / "app", STAGED_RUNTIME_ROOT / "app")


def stage_collections() -> None:
    index_path = ROOT / "collections" / "index.json"
    copy_file(index_path, STAGED_RUNTIME_ROOT / "collections" / "index.json")

    collection_index = json.loads(index_path.read_text(encoding="utf-8"))
    for collection in collection_index.get("collections", []):
        collection_root = ROOT / Path(collection["root"])
        staged_collection_root = STAGED_RUNTIME_ROOT / Path(collection["root"])

        collection_manifest = collection_root / "collection.json"
        if collection_manifest.exists():
            copy_file(collection_manifest, staged_collection_root / "collection.json")

        catalog_path = collection.get("catalog")
        if catalog_path:
            copy_file(ROOT / Path(catalog_path), STAGED_RUNTIME_ROOT / Path(catalog_path))

        images_dir = collection_root / "images"
        if images_dir.exists():
            copy_tree(images_dir, staged_collection_root / "images")


def stage_runtime() -> None:
    remove_tree(STAGED_RUNTIME_ROOT)
    STAGED_RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    stage_core_app_files()
    stage_collections()


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


def format_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{num_bytes} B"


def main() -> int:
    stage_runtime()
    build_executable()

    exe_path = DIST_PATH / f"{APP_NAME}.exe"
    runtime_size = sum(path.stat().st_size for path in STAGED_RUNTIME_ROOT.rglob("*") if path.is_file())
    print(f"Staged runtime: {STAGED_RUNTIME_ROOT}")
    print(f"Staged runtime size: {format_size(runtime_size)}")
    print(f"Built executable: {exe_path}")
    if exe_path.exists():
        print(f"Executable size: {format_size(exe_path.stat().st_size)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
