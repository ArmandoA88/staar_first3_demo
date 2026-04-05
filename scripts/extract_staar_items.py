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
from PIL import Image


YEAR_RE = re.compile(
    r"(?P<year>20(?:1[3-9]|2[0-5]))\s*[\u2013-]?\s*Q(?:(?P<question>\d+)(?:\s+(?P<sample>Sample))?|"
    r"\s*-\s*(?P<non_numbered_label>.+?))(?=\s+Passage\s+#|\s*$)",
    re.S,
)
STANDARD_RE = re.compile(
    r"(?P<standard>\d+\.\d+\([A-Z]\))\s+(?P<description>.+?)\s+Analysis of Assessed Standards",
    re.S,
)
PROCESS_CODE_RE = re.compile(r"\d+\.\d+\([A-Z]\)")
ORDINAL_POSITION_RE = re.compile(r"(\d+)(?:st|nd|rd|th)\s+option", re.I)
PERCENT_TOKEN_RE = re.compile(r"^(NA|\d+)$", re.I)
SLUG_RE = re.compile(r"[^a-z0-9]+")
ENGLISH_COURSE_GRADE_MAP = {
    "I": 9,
    "II": 10,
    "III": 11,
    "IV": 12,
}


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
    render_spans: list[tuple[int, tuple[float, float, float, float]]] | None = None
    source_page_numbers: list[int] | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection-root", default="collections/grade-3/math")
    parser.add_argument("--pdf", default=None)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--images-dir", default=None)
    parser.add_argument("--vision-cache-dir", default=None)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--model", default="gpt-4.1-mini")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--skip-vision", action="store_true")
    parser.add_argument("--force-vision", action="store_true")
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--progress-json", default=None)
    return parser.parse_args()


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def match_year_block_text(value: str | None) -> re.Match[str] | None:
    if not value:
        return None
    return YEAR_RE.search(normalize_space(value))


def slugify_standard(standard: str) -> str:
    return standard.replace("(", "").replace(")", "")


def slugify_text(value: str) -> str:
    normalized = normalize_space(value).lower()
    return SLUG_RE.sub("-", normalized).strip("-")


def infer_subject_and_grade(doc: fitz.Document) -> tuple[str | None, int | None]:
    cover_text = doc.load_page(0).get_text("text")
    subject_match = re.search(r"\b(Math|Reading|Science|Social Studies|ELAR)\b", cover_text, re.I)
    grade_match = re.search(r"Grade\s+(\d+)", cover_text, re.I)
    course_match = re.search(r"\bEnglish\s+(I{1,3}|IV)\b", cover_text, re.I)
    if subject_match:
        raw_subject = subject_match.group(1).upper()
        subject = "ELAR" if raw_subject == "ELAR" else subject_match.group(1).title()
    else:
        subject = None
    if grade_match:
        grade = int(grade_match.group(1))
    elif course_match:
        grade = ENGLISH_COURSE_GRADE_MAP.get(course_match.group(1).upper())
    else:
        grade = None
    return subject, grade


def load_collection_manifest(collection_root: Path) -> dict[str, Any]:
    manifest_path = collection_root / "collection.json"
    if not manifest_path.exists():
        return {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def resolve_collection_metadata(doc: fitz.Document, collection_root: Path) -> tuple[str | None, int | None, str | None]:
    subject, grade = infer_subject_and_grade(doc)
    manifest = load_collection_manifest(collection_root)

    manifest_subject = manifest.get("subject")
    if isinstance(manifest_subject, str) and manifest_subject.strip():
        subject = manifest_subject.strip()

    manifest_grade = manifest.get("grade")
    if isinstance(manifest_grade, int):
        grade = manifest_grade

    manifest_label = manifest.get("label")
    collection_label = manifest_label.strip() if isinstance(manifest_label, str) and manifest_label.strip() else None
    return subject, grade, collection_label


def iter_large_image_rects(page: fitz.Page) -> list[fitz.Rect]:
    rects: list[fitz.Rect] = []
    for image in page.get_images(full=True):
        for rect in page.get_image_rects(image[0], transform=False):
            if rect.x0 < 100 and rect.width > 150 and rect.height >= 20:
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
        "extended constructed response": "constructed_response",
        "extended constructed response composition": "constructed_response",
    }
    return mapping.get(normalized, normalized.replace(" ", "_"))


def extract_stimulus_reference(year_block_text: str | None) -> str | None:
    if not year_block_text:
        return None
    normalized = normalize_space(year_block_text)
    if not match_year_block_text(normalized):
        return None
    passage_match = re.search(r"(Passage\s+#\S+)", normalized, re.I)
    if not passage_match:
        return None
    reference = normalize_space(passage_match.group(1))
    return None if reference.lower() == "passage #none" else reference


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


def parse_metadata(segment_text: str, raw_answer_block_text: str, year_block_text: str | None = None) -> dict[str, Any]:
    text = normalize_space(segment_text)
    standard_match = STANDARD_RE.search(text)
    year_match = match_year_block_text(year_block_text) or match_year_block_text(text)

    if not standard_match or not year_match:
        raise ValueError(f"Unable to parse segment metadata from: {text[:300]}")

    standard = standard_match.group("standard")
    standard_description = normalize_space(standard_match.group("description"))
    year = int(year_match.group("year"))
    question_number = int(year_match.group("question")) if year_match.group("question") else 0
    is_sample = bool(year_match.group("sample"))
    non_numbered_label = normalize_space(year_match.group("non_numbered_label")) if year_match.group("non_numbered_label") else None

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
    if not item_type_display and cluster and "Extended Constructed Response" in cluster:
        item_type_display = cluster
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
        "question_label": non_numbered_label,
        "sample_item": is_sample,
        "stimulus_reference": extract_stimulus_reference(year_block_text),
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


def trim_leading_answer_blocks(
    year_blocks: list[tuple[float, float, float, float, str, int, int]],
    answer_blocks: list[tuple[float, float, float, float, str, int, int]],
) -> list[tuple[float, float, float, float, str, int, int]]:
    trimmed = list(answer_blocks)
    while year_blocks and len(trimmed) > len(year_blocks) and trimmed and trimmed[0][1] < year_blocks[0][1]:
        trimmed = trimmed[1:]
    return trimmed


def leading_answer_block_before_year(
    page: fitz.Page,
) -> tuple[float, float, float, float, str, int, int] | None:
    answer_blocks = iter_matching_blocks(page, lambda text: "Correct Answer" in text)
    if not answer_blocks:
        return None
    year_blocks = iter_matching_blocks(page, lambda text: bool(match_year_block_text(text)))
    if not year_blocks or answer_blocks[0][1] < year_blocks[0][1]:
        return answer_blocks[0]
    return None


def carryover_answer_block(
    page: fitz.Page,
    answer_block: tuple[float, float, float, float, str, int, int],
) -> tuple[float, float, float, float, str, int, int]:
    return (
        answer_block[0],
        page.rect.height - 2.0,
        answer_block[2],
        page.rect.height,
        answer_block[4],
        answer_block[5],
        answer_block[6],
    )


def match_question_image_rects(
    year_blocks: list[tuple[float, float, float, float, str, int, int]],
    image_rects: list[fitz.Rect],
) -> list[fitz.Rect]:
    if not year_blocks:
        return []

    matched_rects: list[fitz.Rect] = []
    search_start = 0

    for index, year_block in enumerate(year_blocks):
        next_year_top = year_blocks[index + 1][1] if index + 1 < len(year_blocks) else float("inf")
        chosen_index = None
        for rect_index in range(search_start, len(image_rects)):
            rect = image_rects[rect_index]
            if rect.y1 <= year_block[1]:
                continue
            if rect.y0 >= next_year_top + 10.0:
                break
            chosen_index = rect_index
            break
        if chosen_index is None:
            return []
        matched_rects.append(image_rects[chosen_index])
        search_start = chosen_index + 1

    return matched_rects


def segment_page(page: fitz.Page, next_page: fitz.Page | None = None) -> list[Segment]:
    year_blocks = iter_matching_blocks(page, lambda text: bool(match_year_block_text(text)))
    answer_blocks = trim_leading_answer_blocks(
        year_blocks,
        iter_matching_blocks(page, lambda text: "Correct Answer" in text),
    )
    if year_blocks and len(answer_blocks) < len(year_blocks) and next_page is not None:
        next_page_leading_answer = leading_answer_block_before_year(next_page)
        if next_page_leading_answer is not None:
            answer_blocks = answer_blocks + [carryover_answer_block(page, next_page_leading_answer)]
    image_rects = match_question_image_rects(year_blocks, iter_large_image_rects(page))

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
        metadata = parse_metadata(segment_text, answer_block[4], year_block[4])
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
                render_spans=[(page.number, rect_to_tuple(crop_rect))],
                source_page_numbers=[page.number + 1],
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


def load_question_image_postprocess_config(collection_root: Path) -> dict[str, Any] | None:
    manifest_path = collection_root / "collection.json"
    if not manifest_path.exists():
        return None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    config = manifest.get("question_image_postprocess")
    return config if isinstance(config, dict) and config else None


def trim_right_artifact_strip(image: Image.Image, config: dict[str, Any]) -> Image.Image:
    trim_config = config.get("trim_right_artifact_strip")
    if not isinstance(trim_config, dict):
        return image

    dark_threshold = int(trim_config.get("dark_threshold", 245))
    search_window = max(1, int(trim_config.get("search_window_px", 320)))
    min_gap_width = max(1, int(trim_config.get("min_gap_width_px", 20)))
    min_tail_width = max(1, int(trim_config.get("min_tail_width_px", 24)))
    max_tail_width = max(min_tail_width, int(trim_config.get("max_tail_width_px", 80)))
    preserve_right_margin = max(0, int(trim_config.get("preserve_right_margin_px", 0)))

    mask = image.convert("L").point(lambda value: 255 if value < dark_threshold else 0)
    projection, _ = mask.getprojection()
    width = len(projection)
    search_start = max(0, width - search_window)

    gap_start: int | None = None
    candidate_gap_start: int | None = None
    candidate_gap_end: int | None = None

    for x in range(search_start, width):
        if projection[x]:
            if gap_start is not None:
                gap_width = x - gap_start
                if gap_width >= min_gap_width and x < width - min_tail_width:
                    candidate_gap_start = gap_start
                    candidate_gap_end = x - 1
                gap_start = None
            continue
        if gap_start is None:
            gap_start = x

    if gap_start is not None:
        trailing_gap_width = width - gap_start
        if trailing_gap_width >= min_gap_width and gap_start > 0:
            trim_x = min(width, gap_start + preserve_right_margin)
            return image.crop((0, 0, trim_x, image.height))

    if candidate_gap_start is None or candidate_gap_end is None:
        return image

    tail_projection = projection[candidate_gap_end + 1 :]
    tail_active_columns = [index for index, value in enumerate(tail_projection) if value]
    if not tail_active_columns:
        trim_x = min(width, candidate_gap_start + preserve_right_margin)
        return image.crop((0, 0, trim_x, image.height))

    tail_width = tail_active_columns[-1] - tail_active_columns[0] + 1
    if min_tail_width <= tail_width <= max_tail_width and candidate_gap_start > 0:
        trim_x = min(candidate_gap_start + preserve_right_margin, candidate_gap_end + 1)
        return image.crop((0, 0, trim_x, image.height))
    return image


def apply_question_image_postprocess(
    image: Image.Image,
    question_image_postprocess: dict[str, Any] | None,
) -> Image.Image:
    if not question_image_postprocess:
        return image
    processed = trim_right_artifact_strip(image, question_image_postprocess)
    return processed if processed.size[0] > 0 and processed.size[1] > 0 else image


def save_rendered_question_image(
    image: Image.Image,
    output_path: Path,
    crop_bbox_pdf_points: list[float],
    dpi: int,
    question_image_postprocess: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_image = apply_question_image_postprocess(image, question_image_postprocess)
    final_image.save(output_path)
    digest = hashlib.sha256(output_path.read_bytes()).hexdigest()
    return {
        "crop_bbox_pdf_points": crop_bbox_pdf_points,
        "render_dpi": dpi,
        "image_width_px": final_image.width,
        "image_height_px": final_image.height,
        "sha256": digest,
    }


def expand_rect(rect: fitz.Rect, page_rect: fitz.Rect, padding: float = 8.0) -> fitz.Rect:
    return fitz.Rect(
        max(page_rect.x0, rect.x0 - padding),
        max(page_rect.y0, rect.y0 - padding),
        min(page_rect.x1, rect.x1 + padding),
        min(page_rect.y1, rect.y1 + padding),
    )


def rect_to_tuple(rect: fitz.Rect) -> tuple[float, float, float, float]:
    return (rect.x0, rect.y0, rect.x1, rect.y1)


def tuple_to_rect(value: tuple[float, float, float, float]) -> fitz.Rect:
    return fitz.Rect(value[0], value[1], value[2], value[3])


def render_page_crop_to_image(page: fitz.Page, crop_rect: fitz.Rect, dpi: int) -> tuple[Image.Image, dict[str, Any]]:
    matrix = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    pixmap = page.get_pixmap(matrix=matrix, clip=crop_rect, alpha=False)
    image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    info = {
        "crop_bbox_pdf_points": [round(crop_rect.x0, 3), round(crop_rect.y0, 3), round(crop_rect.x1, 3), round(crop_rect.y1, 3)],
        "render_dpi": dpi,
        "image_width_px": pixmap.width,
        "image_height_px": pixmap.height,
    }
    return image, info


def render_segment(
    doc: fitz.Document,
    segment: Segment,
    output_path: Path,
    dpi: int,
    question_image_postprocess: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    render_spans = segment.render_spans or [(segment.source_page_numbers or [1])[0] - 1, rect_to_tuple(segment.crop_rect)]

    if len(render_spans) == 1:
        page_index, rect_tuple = render_spans[0]
        page = doc.load_page(page_index)
        image, info = render_page_crop_to_image(page, tuple_to_rect(rect_tuple), dpi)
        info = save_rendered_question_image(
            image,
            output_path,
            info["crop_bbox_pdf_points"],
            dpi,
            question_image_postprocess=question_image_postprocess,
        )
        info["page_span"] = segment.source_page_numbers or [page_index + 1]
        return info

    images: list[Image.Image] = []
    crop_boxes: list[list[float]] = []
    widths: list[int] = []
    heights: list[int] = []

    for page_index, rect_tuple in render_spans:
        page = doc.load_page(page_index)
        image, info = render_page_crop_to_image(page, tuple_to_rect(rect_tuple), dpi)
        images.append(image)
        crop_boxes.append(info["crop_bbox_pdf_points"])
        widths.append(info["image_width_px"])
        heights.append(info["image_height_px"])

    canvas = Image.new("RGB", (max(widths), sum(heights)), "white")
    offset_y = 0
    for image in images:
        canvas.paste(image, (0, offset_y))
        offset_y += image.height

    saved_info = save_rendered_question_image(
        canvas,
        output_path,
        crop_boxes[0],
        dpi,
        question_image_postprocess=question_image_postprocess,
    )
    return {
        "crop_bbox_pdf_points": saved_info["crop_bbox_pdf_points"],
        "stitched_crop_bboxes_pdf_points": crop_boxes,
        "stitched_page_count": len(render_spans),
        "page_span": segment.source_page_numbers or [page_index + 1 for page_index, _ in render_spans],
        "render_dpi": saved_info["render_dpi"],
        "image_width_px": saved_info["image_width_px"],
        "image_height_px": saved_info["image_height_px"],
        "sha256": saved_info["sha256"],
    }


def build_cross_page_standard_segment(
    doc: fitz.Document,
    page_index: int,
) -> tuple[Segment, int] | None:
    if page_index + 2 >= doc.page_count:
        return None

    page = doc.load_page(page_index)
    year_blocks = iter_matching_blocks(page, lambda text: bool(match_year_block_text(text)))
    answer_blocks = iter_matching_blocks(page, lambda text: "Correct Answer" in text)
    image_rects = iter_large_image_rects(page)

    if len(year_blocks) != 1 or answer_blocks or image_rects:
        return None

    continuation_page = doc.load_page(page_index + 1)
    continuation_year_blocks = iter_matching_blocks(continuation_page, lambda text: bool(match_year_block_text(text)))
    continuation_answer_blocks = iter_matching_blocks(continuation_page, lambda text: "Correct Answer" in text)
    continuation_image_rects = iter_large_image_rects(continuation_page)
    if continuation_year_blocks or continuation_answer_blocks or not continuation_image_rects:
        return None

    answer_page = doc.load_page(page_index + 2)
    leading_answer = leading_answer_block_before_year(answer_page)
    if leading_answer is None:
        return None

    merged_rect = fitz.Rect(continuation_image_rects[0])
    for rect in continuation_image_rects[1:]:
        merged_rect.include_rect(rect)
    continuation_crop_rect = expand_rect(merged_rect, continuation_page.rect, padding=10.0)

    year_block = year_blocks[0]
    first_crop_rect = fitz.Rect(50.0, max(0.0, year_block[1] - 10.0), 413.0, page.rect.height - 10.0)
    answer_block = carryover_answer_block(page, leading_answer)
    segment_text = "\n".join(
        [
            page.get_text("text"),
            continuation_page.get_text("text"),
            leading_answer[4],
        ]
    )
    metadata = parse_metadata(segment_text, leading_answer[4], year_block[4])

    return (
        Segment(
            index_on_page=1,
            image_rect=merged_rect,
            year_block=year_block,
            answer_block=answer_block,
            crop_rect=first_crop_rect,
            segment_text=segment_text,
            raw_answer_block_text=leading_answer[4],
            metadata=metadata,
            render_spans=[
                (page_index, rect_to_tuple(first_crop_rect)),
                (page_index + 1, rect_to_tuple(continuation_crop_rect)),
            ],
            source_page_numbers=[page_index + 1, page_index + 2, page_index + 3],
        ),
        page_index + 2,
    )


def collect_standard_segment_entries(doc: fitz.Document) -> list[tuple[int, Segment]]:
    entries: list[tuple[int, Segment]] = []
    skip_until = -1

    for page_index in range(doc.page_count):
        if page_index <= skip_until:
            continue

        cross_page_segment = build_cross_page_standard_segment(doc, page_index)
        if cross_page_segment is not None:
            segment, consumed_until = cross_page_segment
            entries.append((page_index, segment))
            skip_until = consumed_until
            continue

        page = doc.load_page(page_index)
        next_page = doc.load_page(page_index + 1) if page_index + 1 < doc.page_count else None
        for segment in segment_page(page, next_page):
            entries.append((page_index, segment))

    return entries


def extract_packet_header(page_text: str) -> str | None:
    lines = [normalize_space(line) for line in page_text.splitlines() if normalize_space(line)]
    meaningful = [
        line
        for line in lines
        if "lead4ward" not in line.lower()
        and "http" not in line.lower()
        and not re.fullmatch(r"\d+/\d+", line)
        and not re.fullmatch(r"\d+/\d+/\d+.*", line)
    ]
    if not meaningful:
        return None
    if len(meaningful) >= 2 and "Investigating the Question" in meaningful[0]:
        return meaningful[1]
    return meaningful[0]


def build_stimulus_group_id(
    grade: int | None,
    subject: str | None,
    year: int,
    label: str,
    first_page_number: int,
) -> str:
    subject_slug = slugify_text(subject or "unknown") or "unknown"
    label_slug = slugify_text(label) or "stimulus"
    return f"g{grade or 'x'}_{subject_slug}_{year}_{label_slug}_p{first_page_number}"


def build_elar_extraction_plan(
    doc: fitz.Document,
    subject: str | None,
    grade: int | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    item_plans: list[dict[str, Any]] = []
    stimulus_group_plans: list[dict[str, Any]] = []
    pending_stimulus_pages: list[dict[str, Any]] = []
    active_stimulus_group_id: str | None = None

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        page_text = page.get_text("text")
        next_page = doc.load_page(page_index + 1) if page_index + 1 < doc.page_count else None
        segments = segment_page(page, next_page)
        large_image_rects = iter_large_image_rects(page)

        if segments:
            if pending_stimulus_pages:
                first_segment = segments[0]
                label = (
                    first_segment.metadata.get("stimulus_reference")
                    or pending_stimulus_pages[0].get("header")
                    or f"Stimulus packet starting on page {pending_stimulus_pages[0]['page_number']}"
                )
                group_id = build_stimulus_group_id(
                    grade=grade,
                    subject=subject,
                    year=first_segment.metadata["year"],
                    label=label,
                    first_page_number=pending_stimulus_pages[0]["page_number"],
                )
                stimulus_group_plans.append(
                    {
                        "id": group_id,
                        "label": label,
                        "year": first_segment.metadata["year"],
                        "pages": pending_stimulus_pages,
                    }
                )
                active_stimulus_group_id = group_id
                pending_stimulus_pages = []

            for segment in segments:
                stimulus_group_id = active_stimulus_group_id if segment.metadata.get("stimulus_reference") else None
                item_plans.append(
                    {
                        "page_index": page_index,
                        "segment": segment,
                        "stimulus_group_id": stimulus_group_id,
                    }
                )
            continue

        if large_image_rects and "Correct Answer" not in page_text:
            if "Investigating the Question" not in page_text and not pending_stimulus_pages:
                continue
            pending_stimulus_pages.append(
                {
                    "page_index": page_index,
                    "page_number": page_index + 1,
                    "image_rects": large_image_rects,
                    "header": extract_packet_header(page_text),
                }
            )
            active_stimulus_group_id = None

    return item_plans, stimulus_group_plans


def render_stimulus_group(
    doc: fitz.Document,
    root: Path,
    stimuli_dir: Path,
    dpi: int,
    group_plan: dict[str, Any],
) -> dict[str, Any]:
    page_images: list[str] = []
    page_numbers: list[int] = []

    for page_position, page_plan in enumerate(group_plan["pages"], start=1):
        page = doc.load_page(page_plan["page_index"])
        rects = page_plan["image_rects"]
        if not rects:
            continue
        merged_rect = fitz.Rect(rects[0])
        for rect in rects[1:]:
            merged_rect.include_rect(rect)
        crop_rect = expand_rect(merged_rect, page.rect, padding=10.0)
        image_path = stimuli_dir / f"{group_plan['id']}_stimulus_{page_position}.png"
        render_crop(page, crop_rect, image_path, dpi)
        page_images.append(image_path.relative_to(root).as_posix())
        page_numbers.append(page_plan["page_number"])

    return {
        "id": group_plan["id"],
        "label": group_plan["label"],
        "year": group_plan["year"],
        "page_count": len(page_images),
        "page_numbers": page_numbers,
        "page_images": page_images,
        "question_ids": [],
    }


def encode_image(image_path: Path) -> str:
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")


def strip_json_fences(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    return text


def parse_vision_response_text(raw_text: str) -> dict[str, Any]:
    text = strip_json_fences(raw_text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def extract_partial_stem(raw_text: str) -> str | None:
    text = strip_json_fences(raw_text)
    stem_match = re.search(r'"stem"\s*:\s*"(?P<stem>.*)', text, re.S)
    if not stem_match:
        return None
    stem = stem_match.group("stem")
    for marker in ['","instruction"', '", "instruction"', '"instruction"']:
        marker_index = stem.find(marker)
        if marker_index != -1:
            stem = stem[:marker_index]
            break
    stem = (
        stem.replace("\\n", "\n")
        .replace("\\r", "\r")
        .replace("\\t", "\t")
        .replace('\\"', '"')
        .replace("\\\\", "\\")
        .strip()
        .rstrip('"')
    )
    return normalize_space(stem) or None


def build_incomplete_vision_payload(
    item_metadata: dict[str, Any],
    raw_text: str,
    reason: str,
) -> dict[str, Any]:
    stem = extract_partial_stem(raw_text) or "See question image for the full prompt."
    declared_item_type = normalize_item_type(item_metadata.get("declared_item_type_display"))
    return {
        "stem": stem,
        "instruction": None,
        "options": [],
        "choice_pool": [],
        "response_template": None,
        "visual_elements": [],
        "item_type_inferred": declared_item_type or "unknown",
        "confidence": 0.0,
        "notes": f"Vision extraction incomplete ({reason}). Use the original question image for exact wording.",
    }


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

    for attempt in range(1, 6):
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
                max_output_tokens=2000,
            )
            incomplete_reason = getattr(getattr(response, "incomplete_details", None), "reason", None)
            if incomplete_reason == "content_filter":
                parsed = build_incomplete_vision_payload(item_metadata, response.output_text, incomplete_reason)
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")
                return parsed
            parsed = parse_vision_response_text(response.output_text)
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
    stimulus_group: dict[str, Any] | None = None,
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
        "stimulus_reference": metadata.get("stimulus_reference"),
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

    record = {
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
    if stimulus_group:
        record["stimulus"] = {
            "group_id": stimulus_group["id"],
            "label": stimulus_group["label"],
            "page_count": stimulus_group["page_count"],
        }
    return record


def write_progress(progress_path: Path, payload: dict[str, Any]) -> None:
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def resolve_path(root: Path, collection_root: Path, value: str | None, default: Path) -> Path:
    if value is None:
        return default
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    root_candidate = root / candidate
    if root_candidate.exists() or root_candidate.parent.exists():
        return root_candidate
    return collection_root / candidate


def resolve_pdf_path(root: Path, collection_root: Path, value: str | None) -> Path:
    if value:
        return resolve_path(root, collection_root, value, collection_root / value)

    source_dir = collection_root / "source"
    pdfs = sorted(source_dir.glob("*.pdf"))
    if len(pdfs) == 1:
        return pdfs[0]
    if not pdfs:
        raise FileNotFoundError(f"No PDF found in {source_dir}")
    raise RuntimeError(f"Multiple PDFs found in {source_dir}; pass --pdf explicitly.")


def build_skipped_vision_payload(segment: Segment) -> dict[str, Any]:
    return {
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


def build_catalog_payload(
    *,
    root: Path,
    collection_root: Path,
    pdf_path: Path,
    subject: str | None,
    grade: int | None,
    collection_label: str | None,
    items: list[dict[str, Any]],
    stimulus_groups: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    catalog = {
        "source_pdf": pdf_path.name,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "schema_version": "staar_catalog_v4",
        "item_count": len(items),
        "subject": subject,
        "grade": grade,
        "collection_label": collection_label,
        "collection_root": collection_root.relative_to(root).as_posix(),
        "extraction_method": {
            "question_region": "Rendered page crop transcribed with OpenAI vision",
            "answer_key": "Parsed from PDF text layer footer",
            "difficulty": "Derived from state percent-correct data in the PDF text layer",
        },
        "items": items,
    }
    if stimulus_groups:
        catalog["stimulus_groups"] = stimulus_groups
        catalog["stimulus_group_count"] = len(stimulus_groups)
    return catalog


def dedupe_items_by_id(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    deduped: list[dict[str, Any]] = []
    duplicate_ids: list[str] = []
    seen_ids: set[str] = set()

    for item in items:
        if item["id"] in seen_ids:
            duplicate_ids.append(item["id"])
            continue
        seen_ids.add(item["id"])
        deduped.append(item)

    return deduped, duplicate_ids


def process_standard_collection(
    *,
    args: argparse.Namespace,
    root: Path,
    collection_root: Path,
    pdf_path: Path,
    output_json: Path,
    images_dir: Path,
    vision_cache_dir: Path,
    progress_path: Path,
    doc: fitz.Document,
    subject: str | None,
    grade: int | None,
    collection_label: str | None,
    client: OpenAI | None,
    question_image_postprocess: dict[str, Any] | None,
) -> int:
    all_segments = collect_standard_segment_entries(doc)

    if args.limit is not None:
        all_segments = all_segments[: args.limit]

    items: list[dict[str, Any]] = []
    started_at = time.time()

    for item_number, (page_index, segment) in enumerate(all_segments, start=1):
        standard_slug = slugify_standard(segment.metadata["standard"])
        image_name = (
            f"g{grade or 'x'}_{slugify_text(subject or 'unknown') or 'unknown'}_{standard_slug}_"
            f"{segment.metadata['year']}_q{segment.metadata['question_number']}.png"
        )
        image_path = images_dir / image_name
        render_info = render_segment(
            doc,
            segment,
            image_path,
            args.dpi,
            question_image_postprocess=question_image_postprocess,
        )

        if args.skip_vision:
            vision_payload = build_skipped_vision_payload(segment)
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
        write_progress(
            progress_path,
            {
                "status": "running",
                "processed_items": item_number,
                "total_items": len(all_segments),
                "elapsed_seconds": round(elapsed, 1),
                "last_item_id": record["id"],
                "output_json": output_json.as_posix(),
            },
        )
        print(f"[{item_number}/{len(all_segments)}] {record['id']}")

        if args.sleep_seconds:
            time.sleep(args.sleep_seconds)

    items, duplicate_ids = dedupe_items_by_id(items)
    if duplicate_ids:
        print(f"Skipped {len(duplicate_ids)} duplicate items after first occurrence dedupe.")

    catalog = build_catalog_payload(
        root=root,
        collection_root=collection_root,
        pdf_path=pdf_path,
        subject=subject,
        grade=grade,
        collection_label=collection_label,
        items=items,
    )
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


def process_elar_collection(
    *,
    args: argparse.Namespace,
    root: Path,
    collection_root: Path,
    pdf_path: Path,
    output_json: Path,
    images_dir: Path,
    vision_cache_dir: Path,
    progress_path: Path,
    doc: fitz.Document,
    subject: str | None,
    grade: int | None,
    collection_label: str | None,
    client: OpenAI | None,
    question_image_postprocess: dict[str, Any] | None,
) -> int:
    stimuli_dir = collection_root / "images" / "stimuli"
    item_plans, stimulus_group_plans = build_elar_extraction_plan(doc, subject, grade)

    if args.limit is not None:
        item_plans = item_plans[: args.limit]

    referenced_group_ids = {plan["stimulus_group_id"] for plan in item_plans if plan["stimulus_group_id"]}
    stimulus_groups: list[dict[str, Any]] = []
    stimulus_groups_by_id: dict[str, dict[str, Any]] = {}
    for group_plan in stimulus_group_plans:
        if group_plan["id"] not in referenced_group_ids:
            continue
        record = render_stimulus_group(doc, root, stimuli_dir, args.dpi, group_plan)
        stimulus_groups.append(record)
        stimulus_groups_by_id[record["id"]] = record

    items: list[dict[str, Any]] = []
    started_at = time.time()

    for item_number, item_plan in enumerate(item_plans, start=1):
        page_index = item_plan["page_index"]
        segment = item_plan["segment"]
        standard_slug = slugify_standard(segment.metadata["standard"])
        image_name = (
            f"g{grade or 'x'}_{slugify_text(subject or 'unknown') or 'unknown'}_{standard_slug}_"
            f"{segment.metadata['year']}_q{segment.metadata['question_number']}.png"
        )
        image_path = images_dir / image_name
        render_info = render_segment(
            doc,
            segment,
            image_path,
            args.dpi,
            question_image_postprocess=question_image_postprocess,
        )

        if args.skip_vision:
            vision_payload = build_skipped_vision_payload(segment)
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

        stimulus_group = stimulus_groups_by_id.get(item_plan["stimulus_group_id"])
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
            stimulus_group=stimulus_group,
        )
        items.append(record)
        if stimulus_group:
            stimulus_group["question_ids"].append(record["id"])

        elapsed = time.time() - started_at
        write_progress(
            progress_path,
            {
                "status": "running",
                "processed_items": item_number,
                "total_items": len(item_plans),
                "elapsed_seconds": round(elapsed, 1),
                "last_item_id": record["id"],
                "output_json": output_json.as_posix(),
            },
        )
        print(f"[{item_number}/{len(item_plans)}] {record['id']}")

        if args.sleep_seconds:
            time.sleep(args.sleep_seconds)

    items, duplicate_ids = dedupe_items_by_id(items)
    if duplicate_ids:
        print(f"Skipped {len(duplicate_ids)} duplicate items after first occurrence dedupe.")

    for stimulus_group in stimulus_groups:
        stimulus_group["question_ids"] = []
    referenced_group_ids: set[str] = set()
    for item in items:
        stimulus_group_id = item.get("stimulus", {}).get("group_id")
        if not stimulus_group_id:
            continue
        referenced_group_ids.add(stimulus_group_id)
        if stimulus_group_id in stimulus_groups_by_id:
            stimulus_groups_by_id[stimulus_group_id]["question_ids"].append(item["id"])
    stimulus_groups = [group for group in stimulus_groups if group["id"] in referenced_group_ids]

    catalog = build_catalog_payload(
        root=root,
        collection_root=collection_root,
        pdf_path=pdf_path,
        subject=subject,
        grade=grade,
        collection_label=collection_label,
        items=items,
        stimulus_groups=stimulus_groups,
    )
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


def main() -> int:
    args = parse_args()
    root = Path.cwd()
    collection_root = resolve_path(root, root, args.collection_root, root / "collections/grade-3/math")
    pdf_path = resolve_pdf_path(root, collection_root, args.pdf)
    output_json = resolve_path(root, collection_root, args.output_json, collection_root / "data" / "staar_catalog.json")
    images_dir = resolve_path(root, collection_root, args.images_dir, collection_root / "images" / "extracted")
    vision_cache_dir = resolve_path(root, collection_root, args.vision_cache_dir, collection_root / "cache" / "vision")
    progress_path = resolve_path(root, collection_root, args.progress_json, collection_root / "cache" / "progress.json")
    question_image_postprocess = load_question_image_postprocess_config(collection_root)

    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    doc = fitz.open(pdf_path)
    subject, grade, collection_label = resolve_collection_metadata(doc, collection_root)
    client = OpenAI() if (not args.skip_vision and os.environ.get("OPENAI_API_KEY")) else None

    if subject == "ELAR":
        return process_elar_collection(
            args=args,
            root=root,
            collection_root=collection_root,
            pdf_path=pdf_path,
            output_json=output_json,
            images_dir=images_dir,
            vision_cache_dir=vision_cache_dir,
            progress_path=progress_path,
            doc=doc,
            subject=subject,
            grade=grade,
            collection_label=collection_label,
            client=client,
            question_image_postprocess=question_image_postprocess,
        )

    return process_standard_collection(
        args=args,
        root=root,
        collection_root=collection_root,
        pdf_path=pdf_path,
        output_json=output_json,
        images_dir=images_dir,
        vision_cache_dir=vision_cache_dir,
        progress_path=progress_path,
        doc=doc,
        subject=subject,
        grade=grade,
        collection_label=collection_label,
        client=client,
        question_image_postprocess=question_image_postprocess,
    )


if __name__ == "__main__":
    raise SystemExit(main())
