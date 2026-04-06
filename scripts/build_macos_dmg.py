from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from generate_tauri_icons import main as generate_tauri_icons
from packaged_runtime import ROOT, directory_size, format_size, remove_tree, stage_runtime_tree

APP_NAME = "STAAR Problem Browser"
APP_BUNDLE_ID = "com.staarproblembrowser.desktop"
BUILD_ROOT = ROOT / "build" / "macos"
STAGED_RUNTIME_ROOT = BUILD_ROOT / "runtime"
DIST_PATH = BUILD_ROOT / "dist"
PYINSTALLER_WORKPATH = BUILD_ROOT / "pyinstaller-work"
PYINSTALLER_SPECPATH = BUILD_ROOT / "pyinstaller-spec"
DMG_STAGING_ROOT = BUILD_ROOT / "dmg-root"


def read_version() -> str:
    config_path = ROOT / "src-tauri" / "tauri.conf.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    return str(config["version"])


def build_app_bundle() -> Path:
    generate_tauri_icons()
    stage_runtime_tree(STAGED_RUNTIME_ROOT)

    remove_tree(DIST_PATH)
    remove_tree(PYINSTALLER_WORKPATH)
    remove_tree(PYINSTALLER_SPECPATH)

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
        "--windowed",
        "--onedir",
        "--name",
        APP_NAME,
        "--icon",
        str(ROOT / "src-tauri" / "icons" / "icon.icns"),
        "--osx-bundle-identifier",
        APP_BUNDLE_ID,
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

    app_path = DIST_PATH / f"{APP_NAME}.app"
    if not app_path.exists():
        raise FileNotFoundError(f"PyInstaller app bundle was not created: {app_path}")
    return app_path


def build_dmg(app_path: Path) -> Path:
    version = read_version()
    dmg_path = ROOT / f"{APP_NAME}_{version}_macOS.dmg"

    if dmg_path.exists():
        dmg_path.unlink()

    remove_tree(DMG_STAGING_ROOT)
    DMG_STAGING_ROOT.mkdir(parents=True, exist_ok=True)

    staged_app_path = DMG_STAGING_ROOT / app_path.name
    shutil.copytree(app_path, staged_app_path)

    applications_link = DMG_STAGING_ROOT / "Applications"
    if applications_link.exists() or applications_link.is_symlink():
        applications_link.unlink()
    applications_link.symlink_to("/Applications", target_is_directory=True)

    command = [
        "hdiutil",
        "create",
        "-volname",
        APP_NAME,
        "-srcfolder",
        str(DMG_STAGING_ROOT),
        "-ov",
        "-format",
        "UDZO",
        str(dmg_path),
    ]
    subprocess.run(command, check=True)
    return dmg_path


def main() -> int:
    if sys.platform != "darwin":
        print("build_macos_dmg.py must be run on macOS.", file=sys.stderr)
        return 1

    app_path = build_app_bundle()
    dmg_path = build_dmg(app_path)

    runtime_size = directory_size(STAGED_RUNTIME_ROOT)
    print(f"Staged runtime: {STAGED_RUNTIME_ROOT}")
    print(f"Staged runtime size: {format_size(runtime_size)}")
    print(f"Built app bundle: {app_path}")
    print(f"Built DMG: {dmg_path}")
    if dmg_path.exists():
        print(f"DMG size: {format_size(dmg_path.stat().st_size)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
