from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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


def stage_core_app_files(destination_root: Path) -> None:
    copy_file(ROOT / "index.html", destination_root / "index.html")
    copy_tree(ROOT / "app", destination_root / "app")


def stage_collections(destination_root: Path) -> None:
    index_path = ROOT / "collections" / "index.json"
    copy_file(index_path, destination_root / "collections" / "index.json")

    collection_index = json.loads(index_path.read_text(encoding="utf-8"))
    for collection in collection_index.get("collections", []):
        collection_root = ROOT / Path(collection["root"])
        staged_collection_root = destination_root / Path(collection["root"])

        collection_manifest = collection_root / "collection.json"
        if collection_manifest.exists():
            copy_file(collection_manifest, staged_collection_root / "collection.json")

        catalog_path = collection.get("catalog")
        if catalog_path:
            copy_file(ROOT / Path(catalog_path), destination_root / Path(catalog_path))

        images_dir = collection_root / "images"
        if images_dir.exists():
            copy_tree(images_dir, staged_collection_root / "images")


def stage_runtime_tree(destination_root: Path, *, clean: bool = True) -> None:
    if clean:
        remove_tree(destination_root)
    destination_root.mkdir(parents=True, exist_ok=True)
    stage_core_app_files(destination_root)
    stage_collections(destination_root)


def format_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{num_bytes} B"


def directory_size(path: Path) -> int:
    return sum(candidate.stat().st_size for candidate in path.rglob("*") if candidate.is_file())
