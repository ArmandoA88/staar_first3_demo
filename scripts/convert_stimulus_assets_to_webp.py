from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image

from stimulus_image_optimization import (
    STIMULUS_WEBP_METHOD,
    STIMULUS_WEBP_QUALITY,
    save_grayscale_webp,
)

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS_ROOT = ROOT / "collections"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def iter_collection_manifests() -> list[Path]:
    return sorted(COLLECTIONS_ROOT.rglob("collection.json"))


def convert_stimulus_png(png_path: Path) -> Path:
    webp_path = png_path.with_suffix(".webp")
    with Image.open(png_path) as image:
        save_grayscale_webp(image, webp_path)
    return webp_path


def rewrite_catalog_stimulus_paths(catalog: dict[str, Any]) -> int:
    updated_refs = 0
    for stimulus_group in catalog.get("stimulus_groups", []):
        page_images = stimulus_group.get("page_images")
        if not isinstance(page_images, list):
            continue
        next_page_images: list[str] = []
        for image_path in page_images:
            normalized = str(image_path).replace("\\", "/")
            if normalized.lower().endswith(".png"):
                normalized = f"{normalized[:-4]}.webp"
                updated_refs += 1
            next_page_images.append(normalized)
        stimulus_group["page_images"] = next_page_images
    return updated_refs


def main() -> int:
    total_collections = 0
    total_converted = 0
    total_deleted = 0
    total_saved_bytes = 0

    for manifest_path in iter_collection_manifests():
        manifest = read_json(manifest_path)
        catalog_rel = manifest.get("catalog")
        stimulus_rel = manifest.get("stimulus_images_dir")
        if not catalog_rel or not stimulus_rel:
            continue

        catalog_path = ROOT / Path(str(catalog_rel))
        stimulus_dir = ROOT / Path(str(stimulus_rel))
        if not catalog_path.exists() or not stimulus_dir.exists():
            continue

        png_paths = sorted(stimulus_dir.rglob("*.png"))
        if not png_paths:
            continue

        bytes_before = sum(path.stat().st_size for path in png_paths)
        converted = 0
        bytes_after = 0
        for png_path in png_paths:
            webp_path = convert_stimulus_png(png_path)
            converted += 1
            bytes_after += webp_path.stat().st_size

        catalog = read_json(catalog_path)
        updated_refs = rewrite_catalog_stimulus_paths(catalog)
        write_json(catalog_path, catalog)

        deleted = 0
        for png_path in png_paths:
            webp_path = png_path.with_suffix(".webp")
            if webp_path.exists():
                png_path.unlink()
                deleted += 1

        saved_bytes = bytes_before - bytes_after
        total_collections += 1
        total_converted += converted
        total_deleted += deleted
        total_saved_bytes += saved_bytes

        print(
            f"{manifest.get('id', manifest_path.parent.name)}: "
            f"converted={converted} deleted_png={deleted} refs_updated={updated_refs} "
            f"saved_mb={saved_bytes / (1024 * 1024):.2f}"
        )

    print(
        f"Converted {total_converted} stimulus PNG files across {total_collections} collections "
        f"to grayscale WebP q{STIMULUS_WEBP_QUALITY} (method {STIMULUS_WEBP_METHOD})."
    )
    print(f"Deleted {total_deleted} original stimulus PNG files.")
    print(f"Net storage saved: {total_saved_bytes / (1024 * 1024):.2f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
