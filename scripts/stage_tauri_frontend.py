from __future__ import annotations

import argparse
import os

from generate_tauri_icons import main as generate_tauri_icons
from packaged_runtime import ROOT, directory_size, format_size, stage_runtime_tree

TAURI_FRONTEND_ROOT = ROOT / "build" / "tauri" / "frontend"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage the packaged frontend for Tauri.")
    parser.add_argument("--grade", type=int, help="Only bundle collections for a single grade.")
    return parser.parse_args()


def resolve_grade(args: argparse.Namespace) -> int | None:
    if args.grade is not None:
        return args.grade

    env_grade = os.environ.get("STAAR_BUILD_GRADE", "").strip()
    if not env_grade:
        return None

    return int(env_grade)


def main() -> int:
    args = parse_args()
    grade = resolve_grade(args)
    generate_tauri_icons()
    collection_index = stage_runtime_tree(TAURI_FRONTEND_ROOT, grade=grade)
    print(f"Staged Tauri frontend: {TAURI_FRONTEND_ROOT}")
    if grade is None:
        print(f"Included collections: {len(collection_index.get('collections', []))} (full catalog)")
    else:
        collection_labels = ", ".join(collection["label"] for collection in collection_index.get("collections", []))
        print(f"Included collections for grade {grade}: {collection_labels}")
    print(f"Frontend size: {format_size(directory_size(TAURI_FRONTEND_ROOT))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
