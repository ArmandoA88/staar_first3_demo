from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

import fitz

from scripts.extract_staar_items import (
    collect_standard_segment_entries,
    resolve_collection_metadata,
    segment_page,
    slugify_standard,
    slugify_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection-root", default="collections/grade-3/math")
    parser.add_argument("--pdf", default=None)
    parser.add_argument("--catalog", default=None)
    return parser.parse_args()


def resolve_pdf(collection_root: Path, value: str | None) -> Path:
    if value:
        candidate = Path(value)
        return candidate if candidate.is_absolute() else ROOT / candidate
    source_dir = collection_root / "source"
    pdfs = sorted(source_dir.glob("*.pdf"))
    if len(pdfs) == 1:
        return pdfs[0]
    if not pdfs:
        raise FileNotFoundError(f"No PDF found in {source_dir}")
    raise RuntimeError(f"Multiple PDFs found in {source_dir}; pass --pdf explicitly.")


def build_item_id(subject: str | None, grade: int | None, metadata: dict) -> str:
    return (
        f"g{grade or 'x'}_"
        f"{slugify_text(subject or 'unknown') or 'unknown'}_"
        f"{slugify_standard(metadata['standard'])}_"
        f"{metadata['year']}_"
        f"q{metadata['question_number']}"
    )


def main() -> int:
    args = parse_args()
    collection_root = ROOT / args.collection_root
    pdf_path = resolve_pdf(collection_root, args.pdf)
    catalog_path = ROOT / args.catalog if args.catalog else collection_root / "data" / "staar_catalog.json"
    csv_path = collection_root / "reports" / "pdf_coverage_report.csv"
    md_path = collection_root / "reports" / "pdf_coverage_report.md"
    json_path = collection_root / "reports" / "pdf_coverage_summary.json"

    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    if not catalog_path.exists():
        raise FileNotFoundError(catalog_path)

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog_items = catalog["items"]
    catalog_ids = {item["id"] for item in catalog_items}

    doc = fitz.open(pdf_path)
    subject, grade, _ = resolve_collection_metadata(doc, collection_root)

    page_rows: list[dict] = [
        {
            "page_number": page_index + 1,
            "segment_count": 0,
            "has_items": "no",
            "item_ids": "",
            "standards": "",
            "years": "",
            "question_numbers": "",
        }
        for page_index in range(doc.page_count)
    ]
    extracted_ids: list[str] = []

    if subject == "ELAR":
        segment_entries: list[tuple[int, object]] = []
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            next_page = doc.load_page(page_index + 1) if page_index + 1 < doc.page_count else None
            for segment in segment_page(page, next_page):
                segment_entries.append((page_index, segment))
    else:
        segment_entries = collect_standard_segment_entries(doc)

    for page_index, segment in segment_entries:
        item_id = build_item_id(subject, grade, segment.metadata)
        extracted_ids.append(item_id)
        row = page_rows[page_index]
        row["segment_count"] += 1
        row["has_items"] = "yes"
        row["item_ids"] = "; ".join(filter(None, [row["item_ids"], item_id])).strip("; ")
        row["standards"] = "; ".join(filter(None, [row["standards"], segment.metadata["standard"]])).strip("; ")
        row["years"] = "; ".join(filter(None, [row["years"], str(segment.metadata["year"])])).strip("; ")
        row["question_numbers"] = "; ".join(
            filter(None, [row["question_numbers"], str(segment.metadata["question_number"])])
        ).strip("; ")

    extracted_id_counts = Counter(extracted_ids)
    duplicate_extracted_ids = sorted(item_id for item_id, count in extracted_id_counts.items() if count > 1)
    missing_from_catalog = sorted(set(extracted_ids) - catalog_ids)
    missing_from_pdf = sorted(catalog_ids - set(extracted_ids))
    missing_images = sorted(
        item["id"] for item in catalog_items if not (ROOT / item["source"]["question_image"]).exists()
    )

    pages_with_items = [row for row in page_rows if row["segment_count"] > 0]
    two_item_pages = [row["page_number"] for row in page_rows if row["segment_count"] == 2]

    summary = {
        "collection_root": collection_root.relative_to(ROOT).as_posix(),
        "pdf_pages": doc.page_count,
        "pages_with_items": len(pages_with_items),
        "pages_without_items": doc.page_count - len(pages_with_items),
        "two_item_pages": len(two_item_pages),
        "total_detected_segments": len(extracted_ids),
        "catalog_item_count": catalog["item_count"],
        "catalog_json_items": len(catalog_items),
        "all_detected_items_present_in_catalog": not missing_from_catalog,
        "all_catalog_items_present_in_pdf_detection": not missing_from_pdf,
        "all_catalog_images_exist": not missing_images,
        "duplicate_detected_ids": duplicate_extracted_ids,
        "missing_from_catalog": missing_from_catalog,
        "missing_from_pdf_detection": missing_from_pdf,
        "missing_images": missing_images,
        "first_item_page": pages_with_items[0]["page_number"] if pages_with_items else None,
        "last_item_page": pages_with_items[-1]["page_number"] if pages_with_items else None,
    }

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
      writer = csv.DictWriter(
          handle,
          fieldnames=[
              "page_number",
              "segment_count",
              "has_items",
              "item_ids",
              "standards",
              "years",
              "question_numbers",
          ],
      )
      writer.writeheader()
      writer.writerows(page_rows)

    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md_lines = [
        "# PDF Coverage Report",
        "",
        f"- Collection root: `{summary['collection_root']}`",
        f"- PDF pages: {summary['pdf_pages']}",
        f"- Pages with extracted items: {summary['pages_with_items']}",
        f"- Pages without extracted items: {summary['pages_without_items']}",
        f"- Two-item pages: {summary['two_item_pages']}",
        f"- Total detected segments: {summary['total_detected_segments']}",
        f"- Catalog item count: {summary['catalog_item_count']}",
        f"- First item page: {summary['first_item_page']}",
        f"- Last item page: {summary['last_item_page']}",
        f"- All detected items present in catalog: {summary['all_detected_items_present_in_catalog']}",
        f"- All catalog items present in PDF detection: {summary['all_catalog_items_present_in_pdf_detection']}",
        f"- All catalog images exist: {summary['all_catalog_images_exist']}",
        "",
        "## Exceptions",
        "",
        f"- Duplicate detected ids: {len(summary['duplicate_detected_ids'])}",
        f"- Missing from catalog: {len(summary['missing_from_catalog'])}",
        f"- Missing from PDF detection: {len(summary['missing_from_pdf_detection'])}",
        f"- Missing images: {len(summary['missing_images'])}",
        "",
        "## Outputs",
        "",
        f"- CSV: `{csv_path.relative_to(ROOT).as_posix()}`",
        f"- JSON: `{json_path.relative_to(ROOT).as_posix()}`",
    ]
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"Wrote {csv_path}")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
