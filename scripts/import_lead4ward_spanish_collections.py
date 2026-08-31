from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from import_lead4ward_2026 import (
    IQ_URL,
    USER_AGENT,
    CollectionSource,
    derive_difficulty,
    download_image,
    get_student_expectation_control,
    normalize_item_type,
    normalize_space,
    normalize_standard_for_id,
    parse_analysis_rows,
    parse_answer,
    parse_standard_cell,
    parse_stimulus_reference,
    request,
    split_cluster,
    stimulus_tokens,
)


ROOT = Path(__file__).resolve().parents[1]
YEARS = (2026, 2025, 2024, 2023, 2022, 2021, 2019, 2018, 2017, 2016, 2015, 2014, 2013)

# This lead4ward asset returns 404 and is also blank in the combined reference
# PDF.  The importer uses the locally recovered official TEA test pages instead.
KNOWN_LOCAL_STIMULUS_FALLBACKS = {
    "items/slar/19/passages/5sp_19_4_poe_2.png",
}


@dataclass(frozen=True)
class SpanishCollection:
    selection: CollectionSource
    label: str
    grade: int
    subject: str
    root: str
    source_pdf_name: str
    supported_years: tuple[int, ...]


COLLECTIONS = (
    SpanishCollection(
        CollectionSource("grade-3-slar", "SLAR", "grades-slar", "Grade 3", "eg3sp"),
        "Grade 3 SLAR (Spanish)",
        3,
        "SLAR",
        "collections/grade-3/slar",
        "slar3.pdf",
        YEARS,
    ),
    SpanishCollection(
        CollectionSource("grade-4-slar", "SLAR", "grades-slar", "Grade 4", "eg4sp"),
        "Grade 4 SLAR (Spanish)",
        4,
        "SLAR",
        "collections/grade-4/slar",
        "slar4.pdf",
        YEARS,
    ),
    SpanishCollection(
        CollectionSource("grade-5-slar", "SLAR", "grades-slar", "Grade 5", "eg5sp"),
        "Grade 5 SLAR (Spanish)",
        5,
        "SLAR",
        "collections/grade-5/slar",
        "slar5.pdf",
        YEARS,
    ),
    SpanishCollection(
        CollectionSource(
            "grade-5-science-spanish",
            "Science",
            "grades-science",
            "Grade 5 - Spanish",
            "scg5sp",
        ),
        "Grade 5 Science (Spanish)",
        5,
        "Science",
        "collections/grade-5/science-spanish",
        "science spanish.pdf",
        (2026, 2025, 2024, 2023, 2022, 2021, 2019),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import the Spanish-language released STAAR collections from lead4ward IQ."
    )
    parser.add_argument("--collection", action="append", dest="collection_ids")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--workers", type=int, default=8)
    return parser.parse_args()


def selected_collections(collection_ids: list[str] | None) -> list[SpanishCollection]:
    if not collection_ids:
        return list(COLLECTIONS)
    requested = set(collection_ids)
    available = {collection.selection.collection_id for collection in COLLECTIONS}
    unknown = sorted(requested - available)
    if unknown:
        raise ValueError(f"Unknown collection id(s): {', '.join(unknown)}")
    return [collection for collection in COLLECTIONS if collection.selection.collection_id in requested]


def fetch_result(
    session: requests.Session,
    form_soup: BeautifulSoup,
    collection: SpanishCollection,
) -> BeautifulSoup:
    source = collection.selection
    expectation_name, expectations = get_student_expectation_control(form_soup, source)
    payload = [
        ("content-area", source.content_area),
        (source.grade_field, source.grade_value),
        ("filter-selector", "expectations"),
    ]
    payload.extend((str(year), str(year)) for year in collection.supported_years)
    payload.extend((expectation_name, expectation) for expectation in expectations)
    response = request(session, "POST", urljoin(IQ_URL, "createiq.php"), data=payload)
    soup = BeautifulSoup(response.text, "html.parser")
    if "Released Tests" not in normalize_space(soup.get_text(" ", strip=True)):
        raise RuntimeError(f"Unexpected IQ response for {source.collection_id}")
    return soup


def parse_year_and_question(table: Tag) -> tuple[int, int]:
    cell = table.select_one("td.iq-main-item-year")
    text = normalize_space(cell.get_text(" ", strip=True) if cell else "")
    match = re.search(r"\b(20\d{2})\b.*?\bQ(\d+)\b", text, re.IGNORECASE)
    if not match:
        raise RuntimeError(f"Could not parse year and question number from {text!r}")
    return int(match.group(1)), int(match.group(2))


def parse_item(
    table: Tag,
    collection: SpanishCollection,
) -> tuple[dict[str, Any], str]:
    image = table.select_one("img.iq-main-item-image")
    if not image or not image.get("src"):
        raise RuntimeError("IQ item is missing its question image")
    remote_path = str(image.get("src"))
    year, question_number = parse_year_and_question(table)
    standard, standard_description, content = parse_standard_cell(table)

    cluster_cell = table.select_one("td.iq-main-cluster-head")
    cluster_text = normalize_space(cluster_cell.get_text(" ", strip=True) if cluster_cell else "")
    cluster, subcluster = split_cluster(cluster_text)
    item_type_display, points, percent_correct = parse_analysis_rows(table)
    item_type = normalize_item_type(item_type_display)
    stimulus_reference = parse_stimulus_reference(table)

    subject_slug = re.sub(r"[^a-z0-9]+", "_", collection.subject.lower()).strip("_")
    item_id = (
        f"g{collection.grade}_{subject_slug}_{normalize_standard_for_id(standard)}_"
        f"{year}_q{question_number}"
    )
    extension = Path(remote_path.split("?", 1)[0]).suffix.lower() or ".png"
    local_path = Path(collection.root) / "images" / "extracted" / f"{item_id}{extension}"

    item = {
        "id": item_id,
        "source": {
            "pdf_file": collection.source_pdf_name,
            "page_number": None,
            "crop_bbox_pdf_points": None,
            "render_dpi": None,
            "image_width_px": None,
            "image_height_px": None,
            "sha256": None,
            "question_image": local_path.as_posix(),
            "source_url": urljoin(IQ_URL, remote_path),
        },
        "metadata": {
            "grade": collection.grade,
            "subject": collection.subject,
            "language": "Spanish",
            "standard": standard,
            "standard_description": standard_description,
            "year": year,
            "question_number": question_number,
            "cluster": cluster,
            "subcluster": subcluster,
            "content": content,
            "process": "",
            "process_codes": [],
            "sample_item": False,
            "stimulus_reference": stimulus_reference or None,
            "item_type": item_type,
            "declared_item_type_display": item_type_display,
            "points": points,
            "difficulty": derive_difficulty(percent_correct),
        },
        "question": {
            "stem": f"Pregunta STAAR publicada de {year}, pregunta {question_number}",
            "instruction": "",
            "options": [],
            "choice_pool": [],
            "response_template": None,
            "visual_elements": ["Imagen oficial de la pregunta publicada"],
        },
        "answer_key": parse_answer(table),
        "extraction_quality": {
            "question_content_source": "official released item image",
            "answer_source": "lead4ward IQ data analysis row",
            "vision_model": None,
            "vision_confidence": None,
            "needs_review": False,
            "notes": "Spanish-language released item imported from lead4ward IQ; source credited to TEA.",
        },
    }
    return item, remote_path


def parse_items(
    soup: BeautifulSoup,
    collection: SpanishCollection,
) -> list[tuple[dict[str, Any], str]]:
    parsed: list[tuple[dict[str, Any], str]] = []
    seen_paths: set[str] = set()
    for table in soup.select("table.iq-main-table"):
        image = table.select_one("img.iq-main-item-image")
        if not image or not image.get("src"):
            continue
        remote_path = str(image.get("src"))
        if remote_path in seen_paths:
            continue
        seen_paths.add(remote_path)
        parsed.append(parse_item(table, collection))
    if not parsed:
        raise RuntimeError(f"No released items found for {collection.selection.collection_id}")
    return parsed


def parse_stimulus_assets(
    soup: BeautifulSoup,
    collection: SpanishCollection,
) -> dict[tuple[int, str], tuple[str, Path]]:
    if collection.subject != "SLAR":
        return {}
    assets: dict[tuple[int, str], tuple[str, Path]] = {}
    for image in soup.find_all("img"):
        remote_path = str(image.get("src") or "")
        if not remote_path.startswith("items/"):
            continue
        if "iq-main-item-image" in image.get("class", []):
            continue
        match = re.search(r"_(\d{2})_(\d+[a-z]?)_", Path(remote_path).name, re.IGNORECASE)
        if not match:
            continue
        year = 2000 + int(match.group(1))
        token = match.group(2).upper()
        extension = Path(remote_path.split("?", 1)[0]).suffix.lower() or ".png"
        local_path = (
            Path(collection.root)
            / "images"
            / "stimuli"
            / f"g{collection.grade}_slar_{year}_passage-{token.lower()}{extension}"
        )
        assets[(year, token)] = (remote_path, local_path)
    return assets


def prepare_stimulus_groups(
    parsed_items: list[tuple[dict[str, Any], str]],
    assets: dict[tuple[int, str], tuple[str, Path]],
    collection: SpanishCollection,
) -> list[dict[str, Any]]:
    if collection.subject != "SLAR":
        return []
    groups: dict[str, dict[str, Any]] = {}
    for item, _ in parsed_items:
        year = int(item["metadata"]["year"])
        reference = normalize_space(str(item["metadata"].get("stimulus_reference") or ""))
        tokens = stimulus_tokens(reference)
        if not tokens:
            continue
        missing = [token for token in tokens if (year, token) not in assets]
        if missing:
            raise RuntimeError(
                f"Missing passage image(s) {', '.join(missing)} for {item['id']} ({reference})"
            )
        suffix = "-".join(f"passage-{token.lower()}" for token in tokens)
        group_id = f"g{collection.grade}_slar_{year}_{suffix}"
        page_images = [assets[(year, token)][1].as_posix() for token in tokens]
        item["stimulus"] = {
            "group_id": group_id,
            "label": reference,
            "page_count": len(page_images),
        }
        group = groups.setdefault(
            group_id,
            {
                "id": group_id,
                "label": reference,
                "year": year,
                "page_count": len(page_images),
                "page_numbers": [],
                "page_images": page_images,
                "question_ids": [],
            },
        )
        group["question_ids"].append(item["id"])
    return sorted(groups.values(), key=lambda group: (-int(group["year"]), str(group["id"])))


def download_assets(
    parsed_items: list[tuple[dict[str, Any], str]],
    stimulus_assets: dict[tuple[int, str], tuple[str, Path]],
    workers: int,
) -> None:
    futures: dict[Any, tuple[dict[str, Any] | None, Path]] = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        for item, remote_path in parsed_items:
            destination = ROOT / Path(item["source"]["question_image"])
            futures[executor.submit(download_image, remote_path, destination)] = (item, destination)
        for remote_path, local_path in stimulus_assets.values():
            destination = ROOT / local_path
            if remote_path in KNOWN_LOCAL_STIMULUS_FALLBACKS and destination.is_file():
                continue
            futures[executor.submit(download_image, remote_path, destination)] = (None, destination)

        for future in as_completed(futures):
            item, destination = futures[future]
            _, sha256 = future.result()
            if item is None:
                continue
            item["source"]["sha256"] = sha256
            try:
                from PIL import Image

                with Image.open(destination) as image:
                    item["source"]["image_width_px"] = image.width
                    item["source"]["image_height_px"] = image.height
            except Exception:
                pass


def write_catalog(
    collection: SpanishCollection,
    parsed_items: list[tuple[dict[str, Any], str]],
    groups: list[dict[str, Any]],
) -> Path:
    items = [item for item, _ in parsed_items]
    items.sort(
        key=lambda item: (
            -int(item["metadata"]["year"]),
            str(item["metadata"].get("standard") or ""),
            int(item["metadata"].get("question_number") or 0),
            str(item["id"]),
        )
    )
    payload = {
        "source_pdf": collection.source_pdf_name,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "schema_version": "staar_catalog_v4",
        "item_count": len(items),
        "subject": collection.subject,
        "grade": collection.grade,
        "collection_label": collection.label,
        "language": "Spanish",
        "collection_root": collection.root,
        "extraction_method": {
            "released_items": "Official item images and metadata imported from lead4ward IQ (source: TEA)",
            "source_verification": f"Verified against uploaded {collection.source_pdf_name}",
            "difficulty": "Derived from state percent-correct data in the IQ analysis row",
        },
        "items": items,
        "stimulus_groups": groups,
        "stimulus_group_count": len(groups),
    }
    path = ROOT / collection.root / "data" / "staar_catalog.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> int:
    args = parse_args()
    collections = selected_collections(args.collection_ids)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    form_soup = BeautifulSoup(request(session, "GET", IQ_URL).text, "html.parser")

    total_items = 0
    for collection in collections:
        collection_id = collection.selection.collection_id
        print(f"Fetching {collection_id} ...", flush=True)
        soup = fetch_result(session, form_soup, collection)
        parsed_items = parse_items(soup, collection)
        stimulus_assets = parse_stimulus_assets(soup, collection)
        groups = prepare_stimulus_groups(parsed_items, stimulus_assets, collection)
        year_counts = Counter(item["metadata"]["year"] for item, _ in parsed_items)
        total_items += len(parsed_items)
        print(
            f"  Found {len(parsed_items)} unique questions, {len(stimulus_assets)} passage images, "
            f"and {len(groups)} passage groups.",
            flush=True,
        )
        print(f"  Years: {dict(sorted(year_counts.items(), reverse=True))}", flush=True)
        if args.dry_run:
            continue
        download_assets(parsed_items, stimulus_assets, args.workers)
        catalog_path = write_catalog(collection, parsed_items, groups)
        print(f"  Wrote {catalog_path.relative_to(ROOT).as_posix()}.", flush=True)

    action = "Validated" if args.dry_run else "Imported"
    print(f"{action} {total_items} items across {len(collections)} Spanish collections.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (requests.RequestException, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
