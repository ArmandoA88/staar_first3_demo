from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GITIGNORE_PATH = ROOT / ".gitignore"
GITIGNORE_BEGIN = "# >>> split large files >>>"
GITIGNORE_END = "# <<< split large files <<<"
DEFAULT_THRESHOLD_MB = 90
DEFAULT_CHUNK_MB = 48


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split large files into GitHub-safe chunks and restore them locally."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    split_parser = subparsers.add_parser("split", help="Split large files into chunk directories.")
    split_parser.add_argument("paths", nargs="*", help="Optional file paths to split.")
    split_parser.add_argument("--threshold-mb", type=int, default=DEFAULT_THRESHOLD_MB)
    split_parser.add_argument("--chunk-mb", type=int, default=DEFAULT_CHUNK_MB)
    split_parser.add_argument("--delete-original", action="store_true", default=True)
    split_parser.add_argument("--keep-original", action="store_true")

    restore_parser = subparsers.add_parser("restore", help="Restore original files from chunk directories.")
    restore_parser.add_argument("paths", nargs="*", help="Optional original file paths or .parts directories.")
    restore_parser.add_argument("--force", action="store_true")

    status_parser = subparsers.add_parser("status", help="Show tracked split-file status.")
    status_parser.add_argument("paths", nargs="*", help="Optional original file paths or .parts directories.")

    return parser.parse_args()


def relative_repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def sha256_for_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_candidate_files(threshold_bytes: int) -> list[Path]:
    candidates: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        if path.name == "manifest.json" and path.parent.name.endswith(".parts"):
            continue
        if path.suffix.lower().startswith(".part"):
            continue
        if path.parent.name.endswith(".parts"):
            continue
        if path.stat().st_size >= threshold_bytes:
            candidates.append(path)
    return sorted(candidates)


def managed_gitignore_entries() -> set[str]:
    if not GITIGNORE_PATH.exists():
        return set()

    lines = GITIGNORE_PATH.read_text(encoding="utf-8").splitlines()
    inside = False
    entries: set[str] = set()
    for line in lines:
        if line == GITIGNORE_BEGIN:
            inside = True
            continue
        if line == GITIGNORE_END:
            break
        if inside and line and not line.startswith("#"):
            entries.add(line)
    return entries


def update_gitignore(entries: set[str]) -> None:
    existing_lines = GITIGNORE_PATH.read_text(encoding="utf-8").splitlines() if GITIGNORE_PATH.exists() else []
    prefix: list[str] = []
    suffix: list[str] = []
    inside = False
    seen_begin = False
    seen_end = False

    for line in existing_lines:
        if line == GITIGNORE_BEGIN:
            inside = True
            seen_begin = True
            continue
        if line == GITIGNORE_END:
            inside = False
            seen_end = True
            continue
        if inside:
            continue
        if not seen_begin:
            prefix.append(line)
        elif seen_end:
            suffix.append(line)

    managed_block = [
        GITIGNORE_BEGIN,
        "# Paths in this block are restored locally from chunked parts and should not be committed.",
        *sorted(entries),
        GITIGNORE_END,
    ]
    payload_lines = prefix + managed_block + suffix
    GITIGNORE_PATH.write_text("\n".join(payload_lines).rstrip() + "\n", encoding="utf-8")


def parts_dir_for_file(path: Path) -> Path:
    return path.with_name(f"{path.name}.parts")


def manifest_path_for_parts_dir(parts_dir: Path) -> Path:
    return parts_dir / "manifest.json"


def write_split_parts(path: Path, chunk_bytes: int) -> dict[str, object]:
    parts_dir = parts_dir_for_file(path)
    parts_dir.mkdir(parents=True, exist_ok=True)

    part_files: list[str] = []
    file_hash = hashlib.sha256()
    part_index = 0

    with path.open("rb") as source_handle:
        while True:
            buffer = source_handle.read(chunk_bytes)
            if not buffer:
                break
            part_index += 1
            part_name = f"{path.name}.part{part_index:03d}"
            part_path = parts_dir / part_name
            part_path.write_bytes(buffer)
            file_hash.update(buffer)
            part_files.append(part_name)

    manifest = {
        "schema_version": "split_file_manifest_v1",
        "original_path": relative_repo_path(path),
        "original_size_bytes": path.stat().st_size,
        "original_sha256": file_hash.hexdigest(),
        "chunk_size_bytes": chunk_bytes,
        "part_files": part_files,
        "generated_at_utc": utc_now(),
    }
    manifest_path_for_parts_dir(parts_dir).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def resolve_parts_dirs(paths: list[str]) -> list[Path]:
    if not paths:
        return sorted(ROOT.rglob("*.parts"))

    parts_dirs: list[Path] = []
    for raw in paths:
        candidate = (ROOT / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
        if candidate.is_dir() and candidate.name.endswith(".parts"):
            parts_dirs.append(candidate)
            continue
        if candidate.is_file():
            parts_dirs.append(parts_dir_for_file(candidate))
            continue
        raise FileNotFoundError(f"Unsupported path for restore/status: {raw}")
    return sorted(set(parts_dirs))


def read_manifest(parts_dir: Path) -> dict[str, object]:
    manifest_path = manifest_path_for_parts_dir(parts_dir)
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing manifest: {relative_repo_path(manifest_path)}")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def restore_file(parts_dir: Path, force: bool) -> Path:
    manifest = read_manifest(parts_dir)
    original_path = ROOT / str(manifest["original_path"])
    if original_path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {relative_repo_path(original_path)}")

    original_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()

    with original_path.open("wb") as output_handle:
        for part_name in manifest["part_files"]:
            part_path = parts_dir / str(part_name)
            buffer = part_path.read_bytes()
            output_handle.write(buffer)
            digest.update(buffer)

    actual_hash = digest.hexdigest()
    expected_hash = str(manifest["original_sha256"])
    if actual_hash != expected_hash:
        original_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"Checksum mismatch for {relative_repo_path(original_path)}: {actual_hash} != {expected_hash}"
        )
    return original_path


def split_command(args: argparse.Namespace) -> int:
    threshold_bytes = args.threshold_mb * 1024 * 1024
    chunk_bytes = args.chunk_mb * 1024 * 1024
    delete_original = args.delete_original and not args.keep_original

    if args.paths:
        files = []
        for raw in args.paths:
            candidate = (ROOT / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
            if not candidate.exists() or not candidate.is_file():
                raise FileNotFoundError(f"File not found: {raw}")
            files.append(candidate)
    else:
        files = find_candidate_files(threshold_bytes)

    if not files:
        print("No files matched the split criteria.")
        return 0

    gitignore_entries = managed_gitignore_entries()

    for path in files:
        manifest = write_split_parts(path, chunk_bytes)
        print(
            f"Split {relative_repo_path(path)} into {len(manifest['part_files'])} parts "
            f"at {relative_repo_path(parts_dir_for_file(path))}"
        )
        gitignore_entries.add(f"/{relative_repo_path(path)}")
        if delete_original:
            path.unlink()
            print(f"Removed original {relative_repo_path(path)}")

    update_gitignore(gitignore_entries)
    return 0


def restore_command(args: argparse.Namespace) -> int:
    parts_dirs = resolve_parts_dirs(args.paths)
    if not parts_dirs:
        print("No split parts directories found.")
        return 0

    for parts_dir in parts_dirs:
        restored_path = restore_file(parts_dir, force=args.force)
        print(f"Restored {relative_repo_path(restored_path)}")
    return 0


def status_command(args: argparse.Namespace) -> int:
    parts_dirs = resolve_parts_dirs(args.paths)
    if not parts_dirs:
        print("No split parts directories found.")
        return 0

    for parts_dir in parts_dirs:
        manifest = read_manifest(parts_dir)
        original_path = ROOT / str(manifest["original_path"])
        state = "present" if original_path.exists() else "split-only"
        print(
            json.dumps(
                {
                    "original_path": manifest["original_path"],
                    "parts_dir": relative_repo_path(parts_dir),
                    "part_count": len(manifest["part_files"]),
                    "original_exists": original_path.exists(),
                    "state": state,
                }
            )
        )
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "split":
        return split_command(args)
    if args.command == "restore":
        return restore_command(args)
    if args.command == "status":
        return status_command(args)
    raise RuntimeError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
