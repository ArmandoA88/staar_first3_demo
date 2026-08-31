from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS_ROOT = ROOT / "collections"
IQ_URL = "https://iq.lead4ward.com/"
RELEASE_YEAR = 2026
USER_AGENT = "STAAR-Problem-Browser/2026-import"


@dataclass(frozen=True)
class CollectionSource:
    collection_id: str
    content_area: str
    grade_field: str
    grade_value: str
    panel_prefix: str


SOURCES = (
    CollectionSource("grade-3-elar", "ELAR", "grades-elar", "Grade 3", "eg3"),
    CollectionSource("grade-3-math", "Math", "grades-math", "Grade 3", "mg3"),
    CollectionSource("grade-4-elar", "ELAR", "grades-elar", "Grade 4", "eg4"),
    CollectionSource("grade-4-math", "Math", "grades-math", "Grade 4", "mg4"),
    CollectionSource("grade-5-elar", "ELAR", "grades-elar", "Grade 5", "eg5"),
    CollectionSource("grade-5-math", "Math", "grades-math", "Grade 5", "mg5"),
    CollectionSource("grade-5-science", "Science", "grades-science", "Grade 5", "scg5"),
    CollectionSource("grade-6-elar", "ELAR", "grades-elar", "Grade 6", "eg6"),
    CollectionSource("grade-6-math", "Math", "grades-math", "Grade 6", "mg6"),
    CollectionSource("grade-7-elar", "ELAR", "grades-elar", "Grade 7", "eg7"),
    CollectionSource("grade-7-math", "Math", "grades-math", "Grade 7", "mg7"),
    CollectionSource("grade-8-elar", "ELAR", "grades-elar", "Grade 8", "eg8"),
    CollectionSource("grade-8-math", "Math", "grades-math", "Grade 8", "mg8"),
    CollectionSource("grade-8-science", "Science", "grades-science", "Grade 8", "scg8"),
    CollectionSource("grade-8-social-studies", "Social Studies", "grades-ss", "Grade 8", "ssg8"),
    CollectionSource("grade-9-elar", "ELAR", "grades-elar", "English I", "ege1"),
    CollectionSource("grade-9-math", "Math", "grades-math", "Algebra I", "mga1"),
    CollectionSource("grade-9-science", "Science", "grades-science", "Biology", "scgbio"),
    CollectionSource("grade-10-elar", "ELAR", "grades-elar", "English II", "ege2"),
    CollectionSource("grade-11-social-studies", "Social Studies", "grades-ss", "U.S. History", "ssush"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import all 2026 released STAAR items exposed by the lead4ward IQ tool."
    )
    parser.add_argument(
        "--collection",
        action="append",
        dest="collection_ids",
        help="Only import this collection id. May be supplied more than once.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and parse every requested collection without writing catalogs or images.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=6,
        help="Concurrent image downloads (default: 6).",
    )
    return parser.parse_args()


def normalize_space(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_collection_manifests() -> dict[str, dict[str, Any]]:
    index = load_json(COLLECTIONS_ROOT / "index.json")
    return {collection["id"]: collection for collection in index.get("collections", [])}


def request(session: requests.Session, method: str, url: str, **kwargs: Any) -> requests.Response:
    response = session.request(method, url, timeout=120, **kwargs)
    response.raise_for_status()
    response.encoding = "utf-8"
    return response


def get_student_expectation_control(
    form_soup: BeautifulSoup, source: CollectionSource
) -> tuple[str, list[str]]:
    panels = form_soup.select(f'.iq-grade[data-prefix="{source.panel_prefix}"]')
    controls: list[Tag] = []
    for panel in panels:
        controls.extend(
            control
            for control in panel.find_all("input")
            if control.get("name") and str(control.get("name")).endswith("se[]")
        )

    names = {str(control.get("name")) for control in controls}
    if len(names) != 1:
        raise RuntimeError(
            f"Expected one student-expectation control for {source.collection_id}; found {sorted(names)}"
        )

    values: list[str] = []
    for control in controls:
        value = normalize_space(str(control.get("value") or ""))
        if value and value not in values:
            values.append(value)
    if not values:
        raise RuntimeError(f"No student expectations found for {source.collection_id}")
    return names.pop(), values


def fetch_collection_result(
    session: requests.Session,
    form_soup: BeautifulSoup,
    source: CollectionSource,
) -> BeautifulSoup:
    expectation_name, expectations = get_student_expectation_control(form_soup, source)
    payload = [
        ("content-area", source.content_area),
        (source.grade_field, source.grade_value),
        ("filter-selector", "expectations"),
        (str(RELEASE_YEAR), str(RELEASE_YEAR)),
    ]
    payload.extend((expectation_name, expectation) for expectation in expectations)
    response = request(session, "POST", urljoin(IQ_URL, "createiq.php"), data=payload)
    result_soup = BeautifulSoup(response.text, "html.parser")
    if "2026 Released Tests" not in normalize_space(result_soup.get_text(" ", strip=True)):
        raise RuntimeError(f"Unexpected IQ response for {source.collection_id}")
    return result_soup


def split_cluster(value: str) -> tuple[str, str]:
    if ":" not in value:
        return value, ""
    cluster, subcluster = value.split(":", 1)
    return normalize_space(cluster), normalize_space(subcluster)


def parse_standard_cell(table: Tag) -> tuple[str, str, str]:
    cell = table.select_one("td.iq-main-se")
    if not cell:
        raise RuntimeError("IQ item is missing its student-expectation row")
    strong = cell.find("strong")
    standard = normalize_space(strong.get_text(" ", strip=True) if strong else "")
    full_text = normalize_space(cell.get_text(" ", strip=True))
    description = full_text[len(standard) :].strip() if full_text.startswith(standard) else full_text
    content_match = re.search(r"\((Readiness|Supporting)\)\s*$", description, re.IGNORECASE)
    content = content_match.group(1).title() if content_match else ""
    if content_match:
        description = description[: content_match.start()].strip()
    return standard, description, content


def parse_item_number(table: Tag) -> int:
    year_cell = table.select_one("td.iq-main-item-year")
    year_text = normalize_space(year_cell.get_text(" ", strip=True) if year_cell else "")
    match = re.search(r"\bQ(\d+)\b", year_text, re.IGNORECASE)
    if not match:
        raise RuntimeError(f"Could not parse question number from {year_text!r}")
    return int(match.group(1))


def parse_stimulus_reference(table: Tag) -> str:
    year_cell = table.select_one("td.iq-main-item-year")
    year_text = normalize_space(year_cell.get_text(" ", strip=True) if year_cell else "")
    match = re.search(r"\bQ\d+\b\s*(.+)$", year_text, re.IGNORECASE)
    return normalize_space(match.group(1)) if match else ""


def parse_analysis_rows(table: Tag) -> tuple[str, int | None, int | None]:
    item_type = "Unknown"
    points: int | None = None
    percent_correct: int | None = None

    for row in table.find_all("tr"):
        cells = row.find_all("td", recursive=False)
        if not cells:
            continue
        values = [normalize_space(cell.get_text(" ", strip=True)) for cell in cells]
        if values[0] == "Item Type" and len(values) > 1:
            item_type = values[1]
        elif values[0] == "Points" and len(values) > 1:
            match = re.search(r"\d+", values[1])
            points = int(match.group()) if match else None
        elif len(values) > 1:
            state_match = re.fullmatch(r"\d{1,3}", values[1])
            if state_match and ("*" in values[0] or values[0].lower() == "full credit"):
                percent_correct = int(values[1])

    return item_type, points, percent_correct


def normalize_item_type(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    aliases = {
        "drag_drop": "drag_and_drop",
        "multiple_select": "multiselect",
        "multi_select": "multiselect",
        "multiple_choice": "multiple_choice",
        "short_constructed_response_2_points": "short_constructed_response",
        "extended_constructed_response_composition": "extended_constructed_response_(composition)",
    }
    return aliases.get(normalized, normalized or "unknown")


def derive_difficulty(percent_correct: int | None) -> dict[str, Any]:
    if percent_correct is None:
        return {
            "label": "unknown",
            "score": None,
            "percent_correct": None,
            "rationale": "No state percent-correct value was available in the IQ data analysis row.",
            "source": "state_percent_correct",
        }

    if percent_correct >= 90:
        score = 1
    elif percent_correct >= 70:
        score = 2
    elif percent_correct >= 50:
        score = 3
    elif percent_correct >= 30:
        score = 4
    else:
        score = 5
    label = "easy" if percent_correct >= 70 else "medium" if percent_correct >= 50 else "hard"
    return {
        "label": label,
        "score": score,
        "percent_correct": percent_correct,
        "rationale": (
            f"Derived from {percent_correct}% of students earning credit in the State data analysis row."
        ),
        "source": "state_percent_correct",
    }


def normalize_standard_for_id(value: str) -> str:
    normalized = re.sub(r"[()]", "", value)
    normalized = re.sub(r"\s+", "", normalized)
    normalized = re.sub(r"[^A-Za-z0-9._-]", "", normalized)
    return normalized or "unknown"


def parse_answer(table: Tag) -> dict[str, Any]:
    answer_cell = table.select_one("td.iq-main-answer")
    raw = normalize_space(answer_cell.get_text(" ", strip=True) if answer_cell else "")
    raw = re.sub(r"^\*\s*", "", raw)
    match = re.search(r"Correct Answer\s*\((.*?)\)", raw, re.IGNORECASE)
    correct_text = normalize_space(match.group(1)) if match else ""
    if re.fullmatch(r"[A-Z]", correct_text):
        return {
            "raw_pdf_answer_text": raw,
            "answer_format": "single_choice_label",
            "correct_label": correct_text,
            "correct_text": None,
        }
    return {
        "raw_pdf_answer_text": raw,
        "answer_format": "text",
        "correct_text": correct_text or raw or None,
    }


def parse_item(
    table: Tag,
    *,
    collection: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    image = table.select_one("img.iq-main-item-image")
    if not image or not image.get("src"):
        raise RuntimeError("IQ item is missing its question image")
    remote_image_path = str(image.get("src"))
    question_number = parse_item_number(table)
    standard, standard_description, content = parse_standard_cell(table)

    cluster_cell = table.select_one("td.iq-main-cluster-head")
    cluster_text = normalize_space(cluster_cell.get_text(" ", strip=True) if cluster_cell else "")
    cluster, subcluster = split_cluster(cluster_text)
    item_type_display, points, percent_correct = parse_analysis_rows(table)
    item_type = normalize_item_type(item_type_display)
    stimulus_reference = parse_stimulus_reference(table)

    grade = int(collection["grade"])
    subject = str(collection["subject"])
    subject_slug = re.sub(r"[^a-z0-9]+", "_", subject.lower()).strip("_")
    item_id = (
        f"g{grade}_{subject_slug}_{normalize_standard_for_id(standard)}_"
        f"{RELEASE_YEAR}_q{question_number}"
    )
    extension = Path(remote_image_path.split("?", 1)[0]).suffix.lower() or ".png"
    local_image_path = Path(collection["root"]) / "images" / "extracted" / f"{item_id}{extension}"

    item = {
        "id": item_id,
        "source": {
            "pdf_file": "2026 STAAR released test (TEA via lead4ward IQ)",
            "page_number": None,
            "crop_bbox_pdf_points": None,
            "render_dpi": None,
            "image_width_px": None,
            "image_height_px": None,
            "sha256": None,
            "question_image": local_image_path.as_posix(),
            "source_url": urljoin(IQ_URL, remote_image_path),
        },
        "metadata": {
            "grade": grade,
            "subject": subject,
            "standard": standard,
            "standard_description": standard_description,
            "year": RELEASE_YEAR,
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
            "stem": f"2026 released STAAR {subject} item Q{question_number}",
            "instruction": "",
            "options": [],
            "choice_pool": [],
            "response_template": None,
            "visual_elements": ["Official released item image"],
        },
        "answer_key": parse_answer(table),
        "extraction_quality": {
            "question_content_source": "official released item image",
            "answer_source": "lead4ward IQ data analysis row",
            "vision_model": None,
            "vision_confidence": None,
            "needs_review": False,
            "notes": "Imported from the 2026 lead4ward IQ release; source credited to TEA.",
        },
    }
    return item, remote_image_path


def parse_stimulus_assets(
    result_soup: BeautifulSoup,
    collection: dict[str, Any],
) -> dict[str, tuple[str, Path]]:
    if str(collection.get("subject")) != "ELAR":
        return {}

    assets: dict[str, tuple[str, Path]] = {}
    grade = int(collection["grade"])
    for image in result_soup.find_all("img"):
        remote_path = str(image.get("src") or "")
        if not remote_path.startswith("items/elar/26/"):
            continue
        if "iq-main-item-image" in image.get("class", []):
            continue
        match = re.search(r"_26_(\d+[a-z]?)_", Path(remote_path).name, re.IGNORECASE)
        if not match:
            continue
        token = match.group(1).upper()
        extension = Path(remote_path.split("?", 1)[0]).suffix.lower() or ".png"
        local_path = (
            Path(collection["root"])
            / "images"
            / "stimuli"
            / f"g{grade}_elar_2026_passage-{token.lower()}{extension}"
        )
        assets[token] = (remote_path, local_path)
    return assets


def stimulus_tokens(reference: str) -> list[str]:
    tokens: list[str] = []
    for match in re.finditer(r"Passage\s+#(\d+[A-Z]?)", reference, re.IGNORECASE):
        token = match.group(1).upper()
        if token not in tokens:
            tokens.append(token)
    return tokens


def prepare_stimulus_groups(
    parsed_items: list[tuple[dict[str, Any], str]],
    assets: dict[str, tuple[str, Path]],
    collection: dict[str, Any],
) -> list[dict[str, Any]]:
    if str(collection.get("subject")) != "ELAR":
        return []

    groups: dict[str, dict[str, Any]] = {}
    grade = int(collection["grade"])
    for item, _ in parsed_items:
        reference = normalize_space(str(item.get("metadata", {}).get("stimulus_reference") or ""))
        tokens = stimulus_tokens(reference)
        if not tokens:
            raise RuntimeError(f"Missing passage reference for {item['id']}")
        missing = [token for token in tokens if token not in assets]
        if missing:
            raise RuntimeError(
                f"Missing passage image(s) {', '.join(missing)} for {item['id']} ({reference})"
            )

        group_suffix = "-".join(f"passage-{token.lower()}" for token in tokens)
        group_id = f"g{grade}_elar_2026_{group_suffix}"
        page_images = [assets[token][1].as_posix() for token in tokens]
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
                "year": RELEASE_YEAR,
                "page_count": len(page_images),
                "page_numbers": [],
                "page_images": page_images,
                "question_ids": [],
            },
        )
        group["question_ids"].append(item["id"])

    return sorted(groups.values(), key=lambda group: str(group["id"]))


def parse_collection_items(
    result_soup: BeautifulSoup,
    collection: dict[str, Any],
) -> list[tuple[dict[str, Any], str]]:
    parsed: list[tuple[dict[str, Any], str]] = []
    seen_images: set[str] = set()
    for table in result_soup.select("table.iq-main-table"):
        image = table.select_one("img.iq-main-item-image")
        if not image or not image.get("src"):
            continue
        remote_path = str(image.get("src"))
        if remote_path in seen_images:
            continue
        seen_images.add(remote_path)
        parsed.append(parse_item(table, collection=collection))
    if not parsed:
        raise RuntimeError(f"No 2026 item tables found for {collection['id']}")
    return parsed


def download_image(
    remote_path: str,
    destination: Path,
) -> tuple[Path, str]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    response: requests.Response | None = None
    last_error: requests.RequestException | None = None
    for attempt in range(1, 5):
        try:
            response = requests.get(
                urljoin(IQ_URL, remote_path),
                headers={"User-Agent": USER_AGENT},
                timeout=(20, 120),
            )
            response.raise_for_status()
            break
        except requests.RequestException as exc:
            last_error = exc
            if attempt < 4:
                time.sleep(1.5 * attempt)
    if response is None or last_error is not None and not response.ok:
        raise last_error or RuntimeError(f"Unable to download {remote_path}")
    content_type = response.headers.get("Content-Type", "")
    if not content_type.lower().startswith("image/"):
        raise RuntimeError(f"Expected an image at {response.url}; received {content_type!r}")
    destination.write_bytes(response.content)
    return destination, hashlib.sha256(response.content).hexdigest()


def download_collection_images(
    parsed_items: list[tuple[dict[str, Any], str]], workers: int
) -> None:
    futures = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        for item, remote_path in parsed_items:
            destination = ROOT / Path(item["source"]["question_image"])
            future = executor.submit(download_image, remote_path, destination)
            futures[future] = item
        for future in as_completed(futures):
            item = futures[future]
            destination, sha256 = future.result()
            item["source"]["sha256"] = sha256
            try:
                from PIL import Image

                with Image.open(destination) as image:
                    item["source"]["image_width_px"] = image.width
                    item["source"]["image_height_px"] = image.height
            except Exception:
                pass


def download_stimulus_images(assets: dict[str, tuple[str, Path]], workers: int) -> None:
    futures = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        for remote_path, local_path in assets.values():
            future = executor.submit(download_image, remote_path, ROOT / local_path)
            futures[future] = local_path
        for future in as_completed(futures):
            future.result()


def item_sort_key(item: dict[str, Any]) -> tuple[str, int, str]:
    metadata = item.get("metadata", {})
    return (
        str(metadata.get("standard") or ""),
        int(metadata.get("question_number") or 0),
        str(item.get("id") or ""),
    )


def update_catalog(
    collection: dict[str, Any],
    parsed_items: list[tuple[dict[str, Any], str]],
    stimulus_groups: list[dict[str, Any]],
) -> tuple[int, int]:
    catalog_path = ROOT / Path(collection["catalog"])
    catalog = load_json(catalog_path)
    existing_items = list(catalog.get("items", []))
    retained_items = [
        item for item in existing_items if int(item.get("metadata", {}).get("year") or 0) != RELEASE_YEAR
    ]
    imported_items = [item for item, _ in parsed_items]
    merged_items = retained_items + sorted(imported_items, key=item_sort_key)
    catalog["generated_at_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    catalog["item_count"] = len(merged_items)
    catalog["items"] = merged_items
    existing_groups = list(catalog.get("stimulus_groups", []))
    retained_groups = [
        group for group in existing_groups if int(group.get("year") or 0) != RELEASE_YEAR
    ]
    catalog["stimulus_groups"] = retained_groups + stimulus_groups
    catalog["stimulus_group_count"] = len(catalog["stimulus_groups"])
    extraction = catalog.setdefault("extraction_method", {})
    extraction["2026_release"] = "Official item images and metadata imported from lead4ward IQ (source: TEA)"
    write_json(catalog_path, catalog)
    return len(existing_items), len(merged_items)


def remove_stale_2026_images(collection: dict[str, Any], imported_paths: set[Path]) -> int:
    images_dir = ROOT / Path(collection["root"]) / "images" / "extracted"
    removed = 0
    for candidate in images_dir.glob("*2026_q*"):
        if candidate.is_file() and candidate.resolve() not in imported_paths:
            candidate.unlink()
            removed += 1
    return removed


def remove_stale_2026_stimuli(collection: dict[str, Any], imported_paths: set[Path]) -> int:
    images_dir = ROOT / Path(collection["root"]) / "images" / "stimuli"
    if not images_dir.exists():
        return 0
    removed = 0
    for candidate in images_dir.glob("*2026_passage-*"):
        if candidate.is_file() and candidate.resolve() not in imported_paths:
            candidate.unlink()
            removed += 1
    return removed


def selected_sources(collection_ids: list[str] | None) -> list[CollectionSource]:
    if not collection_ids:
        return list(SOURCES)
    requested = set(collection_ids)
    available = {source.collection_id for source in SOURCES}
    unknown = sorted(requested - available)
    if unknown:
        raise ValueError(f"Unknown collection id(s): {', '.join(unknown)}")
    return [source for source in SOURCES if source.collection_id in requested]


def main() -> int:
    args = parse_args()
    sources = selected_sources(args.collection_ids)
    manifests = load_collection_manifests()
    missing = [source.collection_id for source in sources if source.collection_id not in manifests]
    if missing:
        raise RuntimeError(f"Collection manifest(s) not found: {', '.join(missing)}")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    form_soup = BeautifulSoup(request(session, "GET", IQ_URL).text, "html.parser")

    total_items = 0
    for source in sources:
        collection = manifests[source.collection_id]
        print(f"Fetching {source.collection_id} ...", flush=True)
        result_soup = fetch_collection_result(session, form_soup, source)
        parsed_items = parse_collection_items(result_soup, collection)
        stimulus_assets = parse_stimulus_assets(result_soup, collection)
        stimulus_groups = prepare_stimulus_groups(parsed_items, stimulus_assets, collection)
        total_items += len(parsed_items)
        print(
            f"  Found {len(parsed_items)} released items and "
            f"{len(stimulus_assets)} passage images.",
            flush=True,
        )
        if args.dry_run:
            continue

        download_collection_images(parsed_items, args.workers)
        download_stimulus_images(stimulus_assets, args.workers)
        previous_count, current_count = update_catalog(collection, parsed_items, stimulus_groups)
        imported_paths = {
            (ROOT / Path(item["source"]["question_image"])).resolve() for item, _ in parsed_items
        }
        removed = remove_stale_2026_images(collection, imported_paths)
        imported_stimulus_paths = {
            (ROOT / local_path).resolve() for _, local_path in stimulus_assets.values()
        }
        removed_stimuli = remove_stale_2026_stimuli(collection, imported_stimulus_paths)
        print(
            f"  Catalog {previous_count} -> {current_count}; "
            f"downloaded {len(parsed_items)} item and {len(stimulus_assets)} passage images; "
            f"removed {removed + removed_stimuli} stale images.",
            flush=True,
        )

    mode = "Validated" if args.dry_run else "Imported"
    print(f"{mode} {total_items} items across {len(sources)} collections.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (requests.RequestException, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
