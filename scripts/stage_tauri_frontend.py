from __future__ import annotations

from packaged_runtime import ROOT, directory_size, format_size, stage_runtime_tree

TAURI_FRONTEND_ROOT = ROOT / "build" / "tauri" / "frontend"


def main() -> int:
    stage_runtime_tree(TAURI_FRONTEND_ROOT)
    print(f"Staged Tauri frontend: {TAURI_FRONTEND_ROOT}")
    print(f"Frontend size: {format_size(directory_size(TAURI_FRONTEND_ROOT))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
