from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from png_optimization import file_sha256, optimize_png_file

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="collections")
    parser.add_argument("--workers", type=int, default=max(1, min(6, os.cpu_count() or 1)))
    parser.add_argument("--progress-every", type=int, default=250)
    return parser.parse_args()


def iter_target_pngs(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.png") if "images" in path.parts)


def optimize_worker(path_str: str) -> tuple[str, dict[str, int | bool | str]]:
    path = Path(path_str)
    result = optimize_png_file(path)
    return path_str, {
        "original_bytes": result.original_bytes,
        "optimized_bytes": result.optimized_bytes,
        "bytes_saved": result.bytes_saved,
        "grayscale_converted": result.grayscale_converted,
        "rewritten": result.rewritten,
        "mode_before": result.mode_before,
        "mode_after": result.mode_after,
    }


def update_catalog_hashes(root: Path) -> tuple[int, int]:
    changed_files = 0
    changed_items = 0
    for catalog_path in sorted(root.rglob("staar_catalog.json")):
        payload = json.loads(catalog_path.read_text(encoding="utf-8"))
        items = payload.get("items", [])
        file_changed = False
        for item in items:
            source = item.get("source")
            if not isinstance(source, dict):
                continue
            question_image = source.get("question_image")
            if not isinstance(question_image, str) or not question_image:
                continue
            image_path = ROOT / Path(question_image)
            if not image_path.exists():
                continue
            digest = file_sha256(image_path)
            if source.get("sha256") != digest:
                source["sha256"] = digest
                changed_items += 1
                file_changed = True
        if file_changed:
            catalog_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            changed_files += 1
    return changed_files, changed_items


def main() -> int:
    args = parse_args()
    root = ROOT / Path(args.root)
    png_paths = iter_target_pngs(root)
    total_files = len(png_paths)
    if total_files == 0:
        print(f"No PNG files found under {root}")
        return 0

    processed = 0
    rewritten = 0
    grayscale_converted = 0
    original_total = 0
    optimized_total = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(optimize_worker, str(path)): path
            for path in png_paths
        }
        for future in as_completed(futures):
            _, result = future.result()
            processed += 1
            original_total += int(result["original_bytes"])
            optimized_total += int(result["optimized_bytes"])
            rewritten += int(bool(result["rewritten"]))
            grayscale_converted += int(bool(result["grayscale_converted"]))
            if processed % args.progress_every == 0 or processed == total_files:
                saved_mb = (original_total - optimized_total) / (1024 * 1024)
                print(
                    f"[{processed}/{total_files}] rewritten={rewritten} "
                    f"grayscale={grayscale_converted} saved={saved_mb:.2f} MB"
                )

    changed_catalog_files, changed_catalog_items = update_catalog_hashes(root)
    saved_bytes = original_total - optimized_total
    print(f"Processed PNG files: {total_files}")
    print(f"Rewritten files: {rewritten}")
    print(f"Grayscale conversions: {grayscale_converted}")
    print(f"Saved bytes: {saved_bytes}")
    print(f"Saved MB: {saved_bytes / (1024 * 1024):.2f}")
    print(f"Saved GB: {saved_bytes / (1024 * 1024 * 1024):.3f}")
    print(f"Catalog files updated: {changed_catalog_files}")
    print(f"Catalog items updated: {changed_catalog_items}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
