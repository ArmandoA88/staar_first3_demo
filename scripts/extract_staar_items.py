from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fitz
from openai import APIError, OpenAI, RateLimitError


YEAR_RE = re.compile(
    r"(?P<year>20(?:1[5-9]|2[0-5]))\s+[\u2013-]\s+Q(?P<question>\d+)(?:\s+(?P<sample>Sample))?"
)
STANDARD_RE = re.compile(
    r"(?P<standard>\d+\.\d+\([A-Z]\))\s+(?P<description>.+?)\s+Analysis of Assessed Standards",
    re.S,
)
PROCESS_CODE_RE = re.compile(r"\d+\.\d+\([A-Z]\)")
ORDINAL_POSITION_RE = re.compile(r"(\d+)(?:st|nd|rd|th)\s+option", re.I)
PERCENT_TOKEN_RE = re.compile(r"^(NA|\d+)$", re.I)


@dataclass
class Segment:
    index_on_page: int
    image_rect: fitz.Rect
    year_block: tuple[float, float, float, float, str, int, int]
    answer_block: tuple[float, float, float, float, str, int, int]
    crop_rect: fitz.Rect
    segment_text: str
    raw_answer_block_text: str
    metadata: dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", default="ALL STAAR QUESTIONS.pdf")
    parser.add_argument("--output-json", default="data/staar_catalog.json")
    parser.add_argument("--images-dir", default="images/extracted")
    parser.add_argument("--vision-cache-dir", default="cache/vision")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--model", default="gpt-4.1-mini")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--skip-vision", action="store_true")
    parser.add_argument("--force-vision", action="store_true")
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--progress-json", default="cache/progress.json")
    return parser.parse_args()


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def slugify_standard(standard: str) -> str:
    return standard.replace("(", "").replace(")", "")


def infer_subject_and_grade(doc: fitz.Document) -> tuple[str | None, int | None]:
    cover_text = doc.load_page(0).get_text("text")
    subject_match = re.search(r"\b(Math|Reading|Science|Social Studies)\b", cover_text, re.I)
    grade_match = re.search(r"Grade\s+(\d+)", cover_text, re.I)
    subject = subject_match.group(1).title() if subject_match else None
    grade = int(grade_match.group(1)) if grade_match else None
    return subject, grade


def iter_large_image_rects(page: fitz.Page) -> list[fitz.Rect]:
    rects: list[fitz.Rect] = []
    for image in page.get_images(full=True):
        for rect in page.get_image_rects(image[0], transform=False):
            if rect.x0 < 100 and rect.width > 150 and rect.height > 40:
                rects.append(rect)
    return sorted(rects, key=lambda rect: (round(rect.y0, 3), round(rect.x0, 3)))


def iter_matching_blocks(
    page: fitz.Page, predicate: Any
) -> list[tuple[float, float, float, float, str, int, int]]:
    blocks = []
    for block in page.get_text("blocks"):
        text = block[4]
        if predicate(text):
            blocks.append(block)
    return sorted(blocks, key=lambda block: (round(block[1], 3), round(block[0], 3)))


def extract_between(text: str, start_label: str, end_labels: list[str]) -> str | None:
    start = text.find(start_label)
    if start == -1:
        return None
    start += len(start_label)
    end = len(text)
    for end_label in end_labels:
        end_pos = text.find(end_label, start)
        if end_pos != -1 and end_pos < end:
            end = end_pos
    extracted = normalize_space(text[start:end])
    return extracted or None


def normalize_item_type(value: str | None) -> str | None:
    if not value:
        return None
    normalized = normalize_space(value).lower()
    normalized = re.sub(r"\(\d+\s*pts?\)", "", normalized).strip()
    mapping = {
        "multiple choice": "multiple_choice",
        "multiselect": "multiselect",
        "drag and drop": "drag_and_drop",
        "hot text": "hot_text",
        "inline choice": "inline_choice",
        "table": "table",
    }
    return mapping.get(normalized, normalized.replace(" ", "_"))


def infer_item_type_from_content(
    declared_item_type: str | None,
    vision_payload: dict[str, Any],
    answer_key: dict[str, Any],
) -> str:
    if declared_item_type:
        return declared_item_type
    raw = answer_key.get("raw_pdf_answer_text", "")
    if answer_key.get("answer_format") == "single_choice_label":
        return "multiple_choice"
    if answer_key.get("answer_format") == "multi_select_positions":
        return "multiselect"
    if answer_key.get("answer_format") == "ordered_blanks":
        return "drag_and_drop"
    if vision_payload.get("options"):
        return "multiple_choice"
    if vision_payload.get("choice_pool") and vision_payload.get("response_template"):
        return "drag_and_drop"
    if re.search(r"Correct Answer \([^)]*\d", raw):
        return "numeric_response"
    inferred = normalize_item_type(vision_payload.get("item_type_inferred"))
    return inferred or "unknown"


def parse_metadata(segment_text: str, raw_answer_block_text: str) -> dict[str, Any]:
    text = normalize_space(segment_text)
    standard_match = STANDARD_RE.search(text)
    year_match = YEAR_RE.search(text)

    if not standard_match or not year_match:
        raise ValueError(f"Unable to parse segment metadata from: {text[:300]}")

    standard = standard_match.group("standard")
    standard_description = normalize_space(standard_match.group("description"))
    year = int(year_match.group("year"))
    question_number = int(year_match.group("question"))
    is_sample = bool(year_match.group("sample"))

    cluster = extract_between(text, "Cluster", ["Subcluster"])
    subcluster = extract_between(text, "Subcluster", ["Content"])
    content = extract_between(text, "Content", ["Process"])
    process = extract_between(
        text,
        "Process",
        [
            "Item Type",
            "Stimulus",
            "Data Analysis",
            "Error Analysis",
            "Learning from Mistakes",
            "Instructional Implications",
            "Correct Answer",
        ],
    )
    data_analysis_text = extract_between(text, "Item State Local", ["Error Analysis"]) or ""
    item_type_display = extract_between(text, "Item Type", ["Stimulus"])
    points_match = re.search(r"\((\d+)\s*pts?\)", item_type_display or "", re.I)
    points = int(points_match.group(1)) if points_match else None

    raw_answer_text = normalize_space(raw_answer_block_text).replace(" *", "").strip("* ").strip()
    answer_match = re.search(r"Correct Answer\s*\((.*?)\)", raw_answer_text)
    distractor_match = re.search(r"highly chosen incorrect answer\s*\(([A-Z])\)", raw_answer_text, re.I)

    return {
        "standard": standard,
        "standard_description": standard_description,
        "year": year,
        "question_number": question_number,
        "sample_item": is_sample,
        "cluster": cluster,
        "subcluster": subcluster,
        "content": content,
        "process": process or "",
        "process_codes": PROCESS_CODE_RE.findall(process or ""),
        "declared_item_type_display": item_type_display,
        "declared_item_type": normalize_item_type(item_type_display),
        "points": points,
        "data_analysis_text": data_analysis_text,
        "raw_pdf_answer_text": f"Correct Answer ({answer_match.group(1)})" if answer_match else raw_answer_text,
        "raw_pdf_answer_value": answer_match.group(1) if answer_match else None,
        "raw_pdf_distractor_text": raw_answer_text if distractor_match else None,
        "raw_pdf_distractor_label": distractor_match.group(1).upper() if distractor_match else None,
    }


def segment_page(page: fitz.Page) -> list[Segment]:
    year_blocks = iter_matching_blocks(page, lambda text: bool(YEAR_RE.search(text)))
    answer_blocks = iter_matching_blocks(page, lambda text: "Correct Answer" in text)
    image_rects = iter_large_image_rects(page)

    if not year_blocks and not answer_blocks:
        return []
    if len(year_blocks) != len(answer_blocks) or len(year_blocks) != len(image_rects):
        raise ValueError(
            f"Page {page.number + 1} mismatch: {len(year_blocks)} year blocks, "
            f"{len(answer_blocks)} answer blocks, {len(image_rects)} large image rects"
        )

    segments: list[Segment] = []
    for index, (year_block, answer_block, image_rect) in enumerate(
        zip(year_blocks, answer_blocks, image_rects), start=1
    ):
        crop_top = max(0.0, year_block[1] - 10.0)
        crop_bottom = min(page.rect.height - 10.0, answer_block[1] - 8.0)
        crop_rect = fitz.Rect(50.0, crop_top, 413.0, crop_bottom)
        clip_top = max(0.0, year_block[1] - 60.0)
        clip_bottom = min(page.rect.height, answer_block[3] + 20.0)
        segment_text = page.get_text("text", clip=fitz.Rect(0.0, clip_top, page.rect.width, clip_bottom))
        metadata = parse_metadata(segment_text, answer_block[4])
        segments.append(
            Segment(
                index_on_page=index,
                image_rect=image_rect,
                year_block=year_block,
                answer_block=answer_block,
                crop_rect=crop_rect,
                segment_text=segment_text,
                raw_answer_block_text=answer_block[4],
                metadata=metadata,
            )
        )
    return segments


def render_crop(page: fitz.Page, crop_rect: fitz.Rect, output_path: Path, dpi: int) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    matrix = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    pixmap = page.get_pixmap(matrix=matrix, clip=crop_rect, alpha=False)
    pixmap.save(output_path)
    digest = hashlib.sha256(output_path.read_bytes()).hexdigest()
    return {
        "crop_bbox_pdf_points": [round(crop_rect.x0, 3), round(crop_rect.y0, 3), round(crop_rect.x1, 3), round(crop_rect.y1, 3)],
        "render_dpi": dpi,
        "image_width_px": pixmap.width,
        "image_height_px": pixmap.height,
        "sha256": digest,
    }


def encode_image(image_path: Path) -> str:
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")


def strip_json_fences(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    return text


def build_vision_prompt(item_metadata: dict[str, Any]) -> str:
    declared = item_metadata.get("declared_item_type_display") or "Unknown"
    return (
        "Extract one STAAR problem from this image and return strict JSON only.\n"
        "Preserve wording and visible math exactly when readable.\n"
        "Ignore decorative icons and page chrome.\n"
        "If the problem has answer choices, return them in display order.\n"
        "If labels are visible, keep them exactly. If no labels are visible, use null for label.\n"
        "For drag/drop or fill-in-the-blank content, put draggable tokens in choice_pool and rewrite the target line "
        "using [blank_1], [blank_2], etc. in response_template.\n"
        "For numeric-response items, keep options empty.\n"
        f"Known metadata: standard={item_metadata['standard']}, year={item_metadata['year']}, "
        f"question_number={item_metadata['question_number']}, declared_item_type={declared}.\n"
        "Return this JSON object exactly:\n"
        "{"
        '"stem": string, '
        '"instruction": string|null, '
        '"options": [{"label": string|null, "text": string}], '
        '"choice_pool": [string], '
        '"response_template": string|null, '
        '"visual_elements": [string], '
        '"item_type_inferred": string, '
        '"confidence": number, '
        '"notes": string|null'
        "}"
    )


def extract_with_vision(
    client: OpenAI | None,
    image_path: Path,
    model: str,
    item_metadata: dict[str, Any],
    cache_path: Path,
    force: bool,
) -> dict[str, Any]:
    if cache_path.exists() and not force:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    if client is None:
        raise RuntimeError(
            f"OPENAI_API_KEY is required to create missing vision cache for {image_path.name}."
        )

    prompt = build_vision_prompt(item_metadata)
    data_url = f"data:image/png;base64,{encode_image(image_path)}"
    last_error: Exception | None = None

    for attempt in range(1, 4):
        try:
            response = client.responses.create(
                model=model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {"type": "input_image", "image_url": data_url},
                        ],
                    }
                ],
                max_output_tokens=1200,
            )
            parsed = json.loads(strip_json_fences(response.output_text))
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")
            return parsed
        except (json.JSONDecodeError, APIError, RateLimitError) as exc:
            last_error = exc
            time.sleep(attempt * 2)

    raise RuntimeError(f"Vision extraction failed for {image_path.name}: {last_error}") from last_error


def validate_vision_payload(payload: dict[str, Any]) -> dict[str, Any]:
    cleaned = {
        "stem": normalize_space(str(payload.get("stem", ""))),
        "instruction": normalize_space(str(payload["instruction"])) if payload.get("instruction") else None,
        "options": [],
        "choice_pool": [normalize_space(str(choice)) for choice in payload.get("choice_pool", []) if normalize_space(str(choice))],
        "response_template": normalize_space(str(payload["response_template"])) if payload.get("response_template") else None,
        "visual_elements": [normalize_space(str(value)) for value in payload.get("visual_elements", []) if normalize_space(str(value))],
        "item_type_inferred": normalize_item_type(str(payload.get("item_type_inferred") or "")) or "unknown",
        "confidence": round(float(payload.get("confidence", 0.0)), 3),
        "notes": normalize_space(str(payload["notes"])) if payload.get("notes") else None,
    }

    for position, option in enumerate(payload.get("options", []), start=1):
        label = option.get("label")
        label_value = normalize_space(str(label)) if label is not None else None
        text_value = normalize_space(str(option.get("text", "")))
        if text_value:
            cleaned["options"].append({"position": position, "label": label_value or None, "text": text_value})

    return cleaned


def parse_percent_token(value: str | None) -> int | None:
    if not value:
        return None
    token = normalize_space(value).upper()
    if token == "NA":
        return None
    if PERCENT_TOKEN_RE.match(token):
        return int(token)
    return None


def derive_difficulty_from_state_percent(state_percent_correct: int | None) -> dict[str, Any]:
    if state_percent_correct is None:
        return {
            "label": "unknown",
            "score": None,
            "percent_correct": None,
            "rationale": "No state percent-correct value was available in the PDF data analysis row.",
            "source": "state_percent_correct",
        }

    if state_percent_correct >= 90:
        score = 1
    elif state_percent_correct >= 70:
        score = 2
    elif state_percent_correct >= 50:
        score = 3
    elif state_percent_correct >= 30:
        score = 4
    else:
        score = 5

    if state_percent_correct >= 70:
        label = "easy"
    elif state_percent_correct >= 50:
        label = "medium"
    else:
        label = "hard"

    return {
        "label": label,
        "score": score,
        "percent_correct": state_percent_correct,
        "rationale": f"Derived from {state_percent_correct}% of students answering correctly in the State data analysis row.",
        "source": "state_percent_correct",
    }


def parse_state_percent_correct(raw_metadata: dict[str, Any], answer_key: dict[str, Any]) -> int | None:
    data_analysis_text = raw_metadata.get("data_analysis_text") or ""
    if not data_analysis_text:
        return None

    full_credit_match = re.search(r"\bFull Credit\s+(NA|\d+)\b", data_analysis_text, re.I)
    if full_credit_match:
        return parse_percent_token(full_credit_match.group(1))

    if answer_key.get("answer_format") == "single_choice_label":
        correct_label = answer_key.get("correct_label")
        if correct_label:
            label_match = re.search(
                rf"(?<!\w){re.escape(correct_label)}\*\s+(NA|\d+)\b",
                data_analysis_text,
                re.I,
            )
            if label_match:
                return parse_percent_token(label_match.group(1))

    answer_value_candidates = [
        raw_metadata.get("raw_pdf_answer_value"),
        answer_key.get("correct_text"),
    ]
    for candidate in answer_value_candidates:
        if not candidate:
            continue
        value_match = re.search(
            rf"(?<!\S){re.escape(str(candidate))}\s+(NA|\d+)\*?\b",
            data_analysis_text,
            re.I,
        )
        if value_match:
            return parse_percent_token(value_match.group(1))

    return None


def resolve_answer_key(
    raw_metadata: dict[str, Any], question_payload: dict[str, Any], inferred_item_type: str
) -> dict[str, Any]:
    answer_value = raw_metadata.get("raw_pdf_answer_value")
    answer_key: dict[str, Any] = {
        "raw_pdf_answer_text": raw_metadata["raw_pdf_answer_text"],
    }
    options = question_payload.get("options", [])

    if not answer_value:
        answer_key["answer_format"] = "unknown"
        return answer_key

    single_label_match = re.fullmatch(r"([A-Z])", answer_value.strip())
    if single_label_match:
        label = single_label_match.group(1)
        answer_key["answer_format"] = "single_choice_label"
        answer_key["correct_label"] = label
        option = next((item for item in options if item.get("label") == label), None)
        answer_key["correct_text"] = option.get("text") if option else None
    elif ORDINAL_POSITION_RE.search(answer_value):
        positions = [int(match.group(1)) for match in ORDINAL_POSITION_RE.finditer(answer_value)]
        answer_key["answer_format"] = "multi_select_positions"
        answer_key["correct_positions"] = positions
        texts = []
        for position in positions:
            option = next((item for item in options if item.get("position") == position), None)
            if option:
                texts.append(option["text"])
        answer_key["correct_texts"] = texts
    elif ";" in answer_value:
        blank_values = [normalize_space(piece) for piece in answer_value.split(";") if normalize_space(piece)]
        answer_key["answer_format"] = "ordered_blanks"
        answer_key["blank_values"] = blank_values
        answer_key["blank_map"] = {f"blank_{index}": value for index, value in enumerate(blank_values, start=1)}
        template = question_payload.get("response_template")
        if template:
            normalized = template
            for index, value in enumerate(blank_values, start=1):
                normalized = normalized.replace(f"[blank_{index}]", value)
            answer_key["normalized_expression"] = normalized
    else:
        answer_key["answer_format"] = "free_response"
        answer_key["correct_text"] = answer_value

    distractor_label = raw_metadata.get("raw_pdf_distractor_label")
    if distractor_label:
        distractor_option = next((item for item in options if item.get("label") == distractor_label), None)
        answer_key["distractor_note"] = {
            "raw_pdf_text": raw_metadata["raw_pdf_distractor_text"],
            "label": distractor_label,
            "text": distractor_option.get("text") if distractor_option else None,
        }

    if inferred_item_type == "numeric_response" and answer_key.get("answer_format") == "free_response":
        answer_key["answer_format"] = "numeric_response"
    return answer_key


def build_item_record(
    source_pdf: str,
    subject: str | None,
    grade: int | None,
    page_number: int,
    image_path: Path,
    render_info: dict[str, Any],
    segment: Segment,
    vision_payload: dict[str, Any],
    vision_model_name: str,
) -> dict[str, Any]:
    metadata = dict(segment.metadata)
    question_payload = validate_vision_payload(vision_payload)
    inferred_item_type = infer_item_type_from_content(
        metadata.get("declared_item_type"),
        question_payload,
        {"raw_pdf_answer_text": metadata.get("raw_pdf_answer_text")},
    )
    answer_key = resolve_answer_key(metadata, question_payload, inferred_item_type)
    state_percent_correct = parse_state_percent_correct(metadata, answer_key)
    difficulty = derive_difficulty_from_state_percent(state_percent_correct)

    item_id = (
        f"g{grade or 'x'}_"
        f"{(subject or 'unknown').lower()}_"
        f"{slugify_standard(metadata['standard'])}_"
        f"{metadata['year']}_"
        f"q{metadata['question_number']}"
    )

    needs_review = (
        question_payload["confidence"] < 0.75
        or not question_payload["stem"]
        or (
            inferred_item_type in {"multiple_choice", "multiselect"}
            and not question_payload["options"]
        )
        or metadata.get("declared_item_type") == "drag_and_drop"
        and not question_payload["response_template"]
    )

    metadata_out = {
        "grade": grade,
        "subject": subject,
        "standard": metadata["standard"],
        "standard_description": metadata["standard_description"],
        "year": metadata["year"],
        "question_number": metadata["question_number"],
        "cluster": metadata.get("cluster"),
        "subcluster": metadata.get("subcluster"),
        "content": metadata.get("content"),
        "process": metadata.get("process"),
        "process_codes": metadata.get("process_codes", []),
        "sample_item": metadata.get("sample_item", False),
        "item_type": inferred_item_type,
        "declared_item_type_display": metadata.get("declared_item_type_display"),
        "points": metadata.get("points"),
        "difficulty": difficulty,
    }

    question_out = {
        "stem": question_payload["stem"],
        "instruction": question_payload["instruction"],
        "options": question_payload["options"],
        "choice_pool": question_payload["choice_pool"],
        "response_template": question_payload["response_template"],
        "visual_elements": question_payload["visual_elements"],
    }

    return {
        "id": item_id,
        "source": {
            "pdf_file": source_pdf,
            "page_number": page_number,
            **render_info,
            "question_image": image_path.as_posix(),
        },
        "metadata": metadata_out,
        "question": question_out,
        "answer_key": answer_key,
        "extraction_quality": {
            "question_content_source": "vision on rendered crop",
            "answer_source": "pdf text layer footer",
            "vision_model": vision_model_name,
            "vision_confidence": question_payload["confidence"],
            "needs_review": needs_review,
            "notes": question_payload["notes"],
        },
    }


def write_progress(progress_path: Path, payload: dict[str, Any]) -> None:
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path.cwd()
    pdf_path = root / args.pdf
    output_json = root / args.output_json
    images_dir = root / args.images_dir
    vision_cache_dir = root / args.vision_cache_dir
    progress_path = root / args.progress_json

    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    doc = fitz.open(pdf_path)
    subject, grade = infer_subject_and_grade(doc)
    client = OpenAI() if (not args.skip_vision and os.environ.get("OPENAI_API_KEY")) else None

    all_segments: list[tuple[int, Segment]] = []
    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        page_segments = segment_page(page)
        for segment in page_segments:
            all_segments.append((page_index, segment))

    if args.limit is not None:
        all_segments = all_segments[: args.limit]

    items: list[dict[str, Any]] = []
    started_at = time.time()

    for item_number, (page_index, segment) in enumerate(all_segments, start=1):
        page = doc.load_page(page_index)
        standard_slug = slugify_standard(segment.metadata["standard"])
        image_name = (
            f"g{grade or 'x'}_{(subject or 'unknown').lower()}_{standard_slug}_"
            f"{segment.metadata['year']}_q{segment.metadata['question_number']}.png"
        )
        image_path = images_dir / image_name
        render_info = render_crop(page, segment.crop_rect, image_path, args.dpi)

        if args.skip_vision:
            vision_payload = {
                "stem": "",
                "instruction": None,
                "options": [],
                "choice_pool": [],
                "response_template": None,
                "visual_elements": [],
                "item_type_inferred": segment.metadata.get("declared_item_type") or "unknown",
                "confidence": 0.0,
                "notes": "Vision extraction skipped.",
            }
        else:
            cache_path = vision_cache_dir / image_name.replace(".png", ".json")
            vision_payload = extract_with_vision(
                client=client,
                image_path=image_path,
                model=args.model,
                item_metadata=segment.metadata,
                cache_path=cache_path,
                force=args.force_vision,
            )

        record = build_item_record(
            source_pdf=pdf_path.name,
            subject=subject,
            grade=grade,
            page_number=page_index + 1,
            image_path=image_path.relative_to(root),
            render_info=render_info,
            segment=segment,
            vision_payload=vision_payload,
            vision_model_name=args.model if not args.skip_vision else "skipped",
        )
        items.append(record)

        elapsed = time.time() - started_at
        progress = {
            "status": "running",
            "processed_items": item_number,
            "total_items": len(all_segments),
            "elapsed_seconds": round(elapsed, 1),
            "last_item_id": record["id"],
            "output_json": output_json.as_posix(),
        }
        write_progress(progress_path, progress)
        print(f"[{item_number}/{len(all_segments)}] {record['id']}")

        if args.sleep_seconds:
            time.sleep(args.sleep_seconds)

    catalog = {
        "source_pdf": pdf_path.name,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "schema_version": "staar_catalog_v2",
        "item_count": len(items),
        "subject": subject,
        "grade": grade,
        "extraction_method": {
            "question_region": "Rendered page crop transcribed with OpenAI vision",
            "answer_key": "Parsed from PDF text layer footer",
            "difficulty": "Derived from state percent-correct data in the PDF text layer",
        },
        "items": items,
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
    write_progress(
        progress_path,
        {
            "status": "completed",
            "processed_items": len(items),
            "total_items": len(items),
            "elapsed_seconds": round(time.time() - started_at, 1),
            "output_json": output_json.as_posix(),
        },
    )
    print(f"Wrote {len(items)} items to {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
