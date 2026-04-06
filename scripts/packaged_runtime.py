from __future__ import annotations

import json
import os
import stat
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def handle_remove_error(function, target_path: str, _exc_info) -> None:
    os.chmod(target_path, stat.S_IWRITE)
    function(target_path)


def remove_tree(path: Path) -> None:
    if not path.exists():
        return

    last_error: OSError | None = None
    for attempt in range(6):
        try:
            shutil.rmtree(path, onexc=handle_remove_error)
            return
        except OSError as exc:
            last_error = exc
            time.sleep(0.4 * (attempt + 1))

    if last_error is not None and path.exists():
        raise last_error


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_tree(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, dirs_exist_ok=True)


def load_collection_index() -> dict:
    index_path = ROOT / "collections" / "index.json"
    return json.loads(index_path.read_text(encoding="utf-8"))


def filter_collection_index(collection_index: dict, *, grade: int | None = None) -> dict:
    if grade is None:
        return collection_index

    filtered_collections = [
        collection for collection in collection_index.get("collections", []) if collection.get("grade") == grade
    ]
    if not filtered_collections:
        raise ValueError(f"No bundled collections found for grade {grade}.")

    filtered_index = dict(collection_index)
    filtered_index["collections"] = filtered_collections

    default_collection_id = filtered_index.get("default_collection_id")
    valid_ids = {collection["id"] for collection in filtered_collections}
    if default_collection_id not in valid_ids:
        filtered_index["default_collection_id"] = filtered_collections[0]["id"]

    return filtered_index


def stage_core_app_files(destination_root: Path) -> None:
    copy_file(ROOT / "index.html", destination_root / "index.html")
    copy_tree(ROOT / "app", destination_root / "app")


def stage_collections(destination_root: Path, *, collection_index: dict | None = None) -> None:
    staged_index = collection_index or load_collection_index()
    index_destination = destination_root / "collections" / "index.json"
    index_destination.parent.mkdir(parents=True, exist_ok=True)
    index_destination.write_text(f"{json.dumps(staged_index, indent=2)}\n", encoding="utf-8")

    collection_index = staged_index
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


def stage_runtime_tree(destination_root: Path, *, clean: bool = True, grade: int | None = None) -> dict:
    if clean:
        remove_tree(destination_root)
    destination_root.mkdir(parents=True, exist_ok=True)
    collection_index = filter_collection_index(load_collection_index(), grade=grade)
    stage_core_app_files(destination_root)
    stage_collections(destination_root, collection_index=collection_index)
    return collection_index


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
