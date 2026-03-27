from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS_ROOT = ROOT / "collections"
STANDARD_DIRS = [
    "source",
    "data",
    "reports",
    "images/extracted",
    "images/stimuli",
    "images/demo",
    "cache/vision",
    "docs",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--default-collection-id", default=None)
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def normalize_subject(value: str) -> str:
    normalized = value.replace("_", "-").strip().lower()
    if normalized == "elar":
        return "ELAR"
    return normalized.replace("-", " ").title()


def extract_grade_number(value: str) -> int | None:
    match = re.fullmatch(r"grade-(\d+)", value.strip().lower())
    return int(match.group(1)) if match else None


def build_collection_id(grade: int | None, subject: str) -> str:
    subject_slug = subject.lower().replace(" ", "-")
    return f"grade-{grade or 'x'}-{subject_slug}"


def build_collection_label(grade: int | None, subject: str) -> str:
    if grade is None:
        return subject
    return f"Grade {grade} {subject}"


def ensure_standard_dirs(collection_dir: Path) -> None:
    for relative_dir in STANDARD_DIRS:
        (collection_dir / relative_dir).mkdir(parents=True, exist_ok=True)


def relative_repo_path(path: Path | None) -> str | None:
    if path is None:
        return None
    return path.relative_to(ROOT).as_posix()


def first_pdf_in_source(collection_dir: Path) -> Path | None:
    source_pdfs = sorted((collection_dir / "source").glob("*.pdf"))
    return source_pdfs[0] if source_pdfs else None


def existing_reports(collection_dir: Path) -> dict[str, str]:
    report_map = {
        "coverage_csv": collection_dir / "reports" / "pdf_coverage_report.csv",
        "coverage_md": collection_dir / "reports" / "pdf_coverage_report.md",
        "coverage_summary_json": collection_dir / "reports" / "pdf_coverage_summary.json",
    }
    return {
        key: relative_repo_path(path)
        for key, path in report_map.items()
        if path.exists()
    }


def infer_status(source_pdf: Path | None, catalog_path: Path | None) -> str:
    if catalog_path and catalog_path.exists():
        return "ready"
    if source_pdf and source_pdf.exists():
        return "source_only"
    return "scaffolded"


def collection_sort_key(manifest: dict[str, Any]) -> tuple[int, str, str]:
    grade = manifest.get("grade")
    grade_value = grade if isinstance(grade, int) else 999
    subject = str(manifest.get("subject") or "")
    label = str(manifest.get("label") or "")
    return (grade_value, subject.lower(), label.lower())


def normalize_manifest(collection_dir: Path, existing_manifest: dict[str, Any]) -> dict[str, Any]:
    grade = existing_manifest.get("grade")
    if not isinstance(grade, int):
        grade = extract_grade_number(collection_dir.parent.name)

    subject = str(existing_manifest.get("subject") or normalize_subject(collection_dir.name))
    collection_id = str(existing_manifest.get("id") or build_collection_id(grade, subject))
    label = str(existing_manifest.get("label") or build_collection_label(grade, subject))
    root = relative_repo_path(collection_dir)
    source_pdf = first_pdf_in_source(collection_dir)
    catalog_path = collection_dir / "data" / "staar_catalog.json"
    catalog = relative_repo_path(catalog_path) if catalog_path.exists() else None

    return {
        "schema_version": "collection_manifest_v1",
        "id": collection_id,
        "label": label,
        "grade": grade,
        "subject": subject,
        "status": infer_status(source_pdf, catalog_path if catalog else None),
        "root": root,
        "source_pdf": relative_repo_path(source_pdf),
        "catalog": catalog,
        "reports": existing_reports(collection_dir),
        "images_dir": relative_repo_path(collection_dir / "images" / "extracted"),
        "stimulus_images_dir": relative_repo_path(collection_dir / "images" / "stimuli"),
        "vision_cache_dir": relative_repo_path(collection_dir / "cache" / "vision"),
    }


def iter_collection_dirs() -> list[Path]:
    collection_dirs: list[Path] = []
    for grade_dir in sorted(COLLECTIONS_ROOT.glob("grade-*")):
        if not grade_dir.is_dir():
            continue
        for subject_dir in sorted(grade_dir.iterdir()):
            if subject_dir.is_dir():
                collection_dirs.append(subject_dir)
    return collection_dirs


def choose_default_collection(
    manifests: list[dict[str, Any]],
    preferred_id: str | None,
    existing_index: dict[str, Any] | None,
) -> str | None:
    valid_ids = {manifest["id"] for manifest in manifests}
    if preferred_id in valid_ids:
        return preferred_id

    existing_default = existing_index.get("default_collection_id") if existing_index else None
    if existing_default in valid_ids:
        return existing_default

    ready_manifest = next((manifest for manifest in manifests if manifest["status"] == "ready"), None)
    if ready_manifest:
        return ready_manifest["id"]

    return manifests[0]["id"] if manifests else None


def main() -> int:
    args = parse_args()
    existing_index = read_json(COLLECTIONS_ROOT / "index.json") if (COLLECTIONS_ROOT / "index.json").exists() else None

    manifests: list[dict[str, Any]] = []
    for collection_dir in iter_collection_dirs():
        ensure_standard_dirs(collection_dir)
        manifest_path = collection_dir / "collection.json"
        existing_manifest = read_json(manifest_path) if manifest_path.exists() else {}
        manifest = normalize_manifest(collection_dir, existing_manifest)
        write_json(manifest_path, manifest)
        manifests.append(manifest)

    manifests.sort(key=collection_sort_key)
    default_collection_id = choose_default_collection(manifests, args.default_collection_id, existing_index)

    index_payload = {
        "schema_version": "collection_index_v1",
        "default_collection_id": default_collection_id,
        "collections": manifests,
    }
    write_json(COLLECTIONS_ROOT / "index.json", index_payload)

    print(f"Indexed {len(manifests)} collections.")
    print(f"Default collection: {default_collection_id}")
    print(f"Wrote {(COLLECTIONS_ROOT / 'index.json').relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
