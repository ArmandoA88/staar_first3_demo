from __future__ import annotations

import argparse
import io
import json
from dataclasses import dataclass
from pathlib import Path

import fitz
import qrcode


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "STAAR_Problem_Browser_User_Guide.pdf"
COLLECTION_INDEX_PATH = ROOT / "collections" / "index.json"
PACKAGE_JSON_PATH = ROOT / "package.json"
DEFAULT_WINDOWS_INSTALLER_URL = (
    "https://drive.google.com/file/d/1mmRieq_iGFiQZERsALE-vF1yV9dwAP5X/view?usp=sharing"
)
DEFAULT_MACOS_INSTALLER_URL = (
    "https://drive.google.com/file/d/1mmRieq_iGFiQZERsALE-vF1yV9dwAP5X/view?usp=sharing"
)

PAGE_WIDTH = 612
PAGE_HEIGHT = 792
MARGIN_X = 54
TOP_MARGIN = 68
BOTTOM_MARGIN = 48
CONTENT_WIDTH = PAGE_WIDTH - (MARGIN_X * 2)

COLOR_TEXT = (0.14, 0.16, 0.21)
COLOR_MUTED = (0.39, 0.43, 0.50)
COLOR_LINE = (0.80, 0.84, 0.89)
COLOR_ACCENT = (0.12, 0.32, 0.55)
COLOR_ACCENT_LIGHT = (0.91, 0.95, 0.99)
COLOR_ROW_ALT = (0.97, 0.98, 0.99)
COLOR_WHITE = (1.0, 1.0, 1.0)


@dataclass
class CollectionSummary:
    collection_id: str
    label: str
    grade: int
    subject: str
    count: int


@dataclass
class DownloadPanel:
    title: str
    button_label: str
    url: str


class GuidePdf:
    def __init__(
        self,
        title: str,
        version: str,
        cover_title: str | None = None,
        edition_label: str | None = None,
    ) -> None:
        self.title = title
        self.version = version
        self.cover_title = cover_title or title
        self.edition_label = edition_label
        self.doc = fitz.open()
        self.page_number = 0
        self.page: fitz.Page | None = None
        self.cursor_y = TOP_MARGIN

    def add_page(self, show_header: bool = True) -> None:
        self.page_number += 1
        self.page = self.doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        self.cursor_y = TOP_MARGIN
        if show_header:
            self._draw_header()

    def _draw_header(self) -> None:
        assert self.page is not None
        self.page.draw_line(
            fitz.Point(MARGIN_X, 42),
            fitz.Point(PAGE_WIDTH - MARGIN_X, 42),
            color=COLOR_LINE,
            width=1,
        )
        self.page.insert_text(
            fitz.Point(MARGIN_X, 30),
            self.title,
            fontname="hebo",
            fontsize=10,
            color=COLOR_MUTED,
        )
        self.page.insert_text(
            fitz.Point(PAGE_WIDTH - MARGIN_X - 48, 30),
            f"v{self.version}",
            fontname="helv",
            fontsize=10,
            color=COLOR_MUTED,
        )

    def finalize(self) -> None:
        for index, page in enumerate(self.doc, start=1):
            page.draw_line(
                fitz.Point(MARGIN_X, PAGE_HEIGHT - 34),
                fitz.Point(PAGE_WIDTH - MARGIN_X, PAGE_HEIGHT - 34),
                color=COLOR_LINE,
                width=1,
            )
            page.insert_text(
                fitz.Point(MARGIN_X, PAGE_HEIGHT - 20),
                self.title,
                fontname="helv",
                fontsize=9,
                color=COLOR_MUTED,
            )
            page.insert_text(
                fitz.Point(PAGE_WIDTH - MARGIN_X - 16, PAGE_HEIGHT - 20),
                str(index),
                fontname="hebo",
                fontsize=9,
                color=COLOR_MUTED,
            )

    def save(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.finalize()
        self.doc.save(output_path)

    def add_uri_link(self, rect: fitz.Rect, uri: str) -> None:
        assert self.page is not None
        self.page.insert_link({"kind": fitz.LINK_URI, "from": rect, "uri": uri})

    def ensure_space(self, required_height: float) -> None:
        if self.cursor_y + required_height <= PAGE_HEIGHT - BOTTOM_MARGIN:
            return
        self.add_page(show_header=True)

    def add_cover(
        self,
        total_items: int,
        collection_count: int,
        collections: list[CollectionSummary],
        download_panels: list[DownloadPanel],
        scope_descriptor: str,
        delivery_context_label: str,
        cover_subtitle: str,
    ) -> None:
        self.add_page(show_header=False)
        assert self.page is not None

        self.page.draw_rect(
            fitz.Rect(0, 0, PAGE_WIDTH, 324),
            color=COLOR_ACCENT,
            fill=COLOR_ACCENT,
        )
        self.page.draw_rect(
            fitz.Rect(MARGIN_X, 338, PAGE_WIDTH - MARGIN_X, 450),
            color=COLOR_LINE,
            fill=COLOR_ACCENT_LIGHT,
            width=1,
        )

        self.page.insert_textbox(
            fitz.Rect(MARGIN_X, 68, PAGE_WIDTH - MARGIN_X, 136),
            self.cover_title,
            fontname="hebo",
            fontsize=28,
            color=COLOR_WHITE,
            align=0,
        )
        subtitle_top = 138
        if self.edition_label:
            self.page.insert_text(
                fitz.Point(MARGIN_X, 154),
                self.edition_label,
                fontname="hebo",
                fontsize=16,
                color=COLOR_WHITE,
            )
            subtitle_top = 164

        self.page.insert_textbox(
            fitz.Rect(MARGIN_X, subtitle_top, PAGE_WIDTH - MARGIN_X, 188),
            cover_subtitle,
            fontname="helv",
            fontsize=13,
            color=COLOR_WHITE,
            align=0,
        )

        if len(download_panels) == 1:
            self._draw_download_panel(
                panel_rect=fitz.Rect(MARGIN_X, 188, PAGE_WIDTH - MARGIN_X, 314),
                title=download_panels[0].title,
                button_label=download_panels[0].button_label,
                url=download_panels[0].url,
            )
        else:
            panel_gap = 12
            panel_width = (CONTENT_WIDTH - panel_gap) / 2
            for index, panel in enumerate(download_panels[:2]):
                panel_left = MARGIN_X + (index * (panel_width + panel_gap))
                panel_rect = fitz.Rect(panel_left, 188, panel_left + panel_width, 314)
                self._draw_download_panel(
                    panel_rect=panel_rect,
                    title=panel.title,
                    button_label=panel.button_label,
                    url=panel.url,
                )

        self.page.insert_text(
            fitz.Point(MARGIN_X, 198),
            "",
            fontname="helv",
            fontsize=1,
            color=COLOR_WHITE,
        )

        self.page.insert_textbox(
            fitz.Rect(MARGIN_X + 20, 360, PAGE_WIDTH - MARGIN_X - 20, 430),
            (
                f"This build includes {collection_count} ready collection{'s' if collection_count != 1 else ''} and {total_items:,} released STAAR items "
                f"across {scope_descriptor}."
            ),
            fontname="hebo",
            fontsize=15,
            color=COLOR_TEXT,
            align=0,
        )

        self.page.insert_textbox(
            fitz.Rect(MARGIN_X, 476, PAGE_WIDTH - MARGIN_X, 720),
            (
                "Included collections:\n"
                + "\n".join(f"- {entry.label}" for entry in collections)
                + f"\n\nUse this guide as the PDF that ships with your {delivery_context_label} TPT download."
            ),
            fontname="helv",
            fontsize=12,
            color=COLOR_TEXT,
            align=0,
        )

    def _draw_download_panel(
        self,
        panel_rect: fitz.Rect,
        title: str,
        button_label: str,
        url: str,
    ) -> None:
        assert self.page is not None
        self.page.draw_rect(panel_rect, color=COLOR_WHITE, fill=COLOR_WHITE, width=1)
        self.page.insert_text(
            fitz.Point(panel_rect.x0 + 14, panel_rect.y0 + 20),
            title,
            fontname="hebo",
            fontsize=11.5,
            color=COLOR_ACCENT,
        )
        button_rect = fitz.Rect(panel_rect.x0 + 14, panel_rect.y0 + 34, panel_rect.x0 + 180, panel_rect.y0 + 62)
        qr_size = 54
        qr_rect = fitz.Rect(
            panel_rect.x0 + 14,
            panel_rect.y0 + 70,
            panel_rect.x0 + 14 + qr_size,
            panel_rect.y0 + 70 + qr_size,
        )
        url_rect = fitz.Rect(qr_rect.x1 + 10, panel_rect.y0 + 72, panel_rect.x1 - 14, panel_rect.y1 - 12)
        self.page.draw_rect(button_rect, color=COLOR_ACCENT_LIGHT, fill=COLOR_ACCENT_LIGHT, width=0)
        self.page.insert_textbox(
            button_rect,
            button_label,
            fontname="hebo",
            fontsize=10,
            color=COLOR_ACCENT,
            align=1,
        )
        self.page.insert_textbox(
            url_rect,
            url,
            fontname="helv",
            fontsize=7.3,
            color=COLOR_MUTED,
            align=0,
        )
        self.page.insert_image(qr_rect, stream=build_qr_png_bytes(url))
        self.add_uri_link(button_rect, url)
        self.add_uri_link(qr_rect, url)
        self.add_uri_link(url_rect, url)

    def add_heading(self, text: str) -> None:
        self.ensure_space(30)
        assert self.page is not None
        self.page.insert_text(
            fitz.Point(MARGIN_X, self.cursor_y),
            text,
            fontname="hebo",
            fontsize=18,
            color=COLOR_ACCENT,
        )
        self.cursor_y += 24

    def add_subheading(self, text: str) -> None:
        self.ensure_space(24)
        assert self.page is not None
        self.page.insert_text(
            fitz.Point(MARGIN_X, self.cursor_y),
            text,
            fontname="hebo",
            fontsize=13,
            color=COLOR_TEXT,
        )
        self.cursor_y += 18

    def add_paragraph(self, text: str, fontsize: float = 11.5) -> None:
        lines = wrap_text(text, CONTENT_WIDTH, fontname="helv", fontsize=fontsize)
        line_height = fontsize * 1.42
        self.ensure_space(line_height * len(lines) + 8)
        assert self.page is not None
        for line in lines:
            self.page.insert_text(
                fitz.Point(MARGIN_X, self.cursor_y),
                line,
                fontname="helv",
                fontsize=fontsize,
                color=COLOR_TEXT,
            )
            self.cursor_y += line_height
        self.cursor_y += 6

    def add_bullets(self, items: list[str], fontsize: float = 11.5) -> None:
        prefix = "- "
        prefix_width = fitz.get_text_length(prefix, fontname="hebo", fontsize=fontsize)
        usable_width = CONTENT_WIDTH - prefix_width
        line_height = fontsize * 1.42
        for item in items:
            lines = wrap_text(item, usable_width, fontname="helv", fontsize=fontsize)
            self.ensure_space(line_height * len(lines) + 4)
            assert self.page is not None
            for index, line in enumerate(lines):
                x = MARGIN_X
                text = line
                if index == 0:
                    self.page.insert_text(
                        fitz.Point(x, self.cursor_y),
                        prefix,
                        fontname="hebo",
                        fontsize=fontsize,
                        color=COLOR_TEXT,
                    )
                    x += prefix_width
                else:
                    x += prefix_width
                self.page.insert_text(
                    fitz.Point(x, self.cursor_y),
                    text,
                    fontname="helv",
                    fontsize=fontsize,
                    color=COLOR_TEXT,
                )
                self.cursor_y += line_height
            self.cursor_y += 2
        self.cursor_y += 4

    def add_numbered_steps(self, items: list[str], fontsize: float = 11.5) -> None:
        line_height = fontsize * 1.42
        for step_index, item in enumerate(items, start=1):
            prefix = f"{step_index}. "
            prefix_width = fitz.get_text_length(prefix, fontname="hebo", fontsize=fontsize)
            usable_width = CONTENT_WIDTH - prefix_width
            lines = wrap_text(item, usable_width, fontname="helv", fontsize=fontsize)
            self.ensure_space(line_height * len(lines) + 4)
            assert self.page is not None
            for line_index, line in enumerate(lines):
                x = MARGIN_X
                if line_index == 0:
                    self.page.insert_text(
                        fitz.Point(x, self.cursor_y),
                        prefix,
                        fontname="hebo",
                        fontsize=fontsize,
                        color=COLOR_TEXT,
                    )
                    x += prefix_width
                else:
                    x += prefix_width
                self.page.insert_text(
                    fitz.Point(x, self.cursor_y),
                    line,
                    fontname="helv",
                    fontsize=fontsize,
                    color=COLOR_TEXT,
                )
                self.cursor_y += line_height
            self.cursor_y += 2
        self.cursor_y += 4

    def add_callout(self, text: str) -> None:
        fontsize = 11
        padding = 12
        lines = wrap_text(text, CONTENT_WIDTH - (padding * 2), fontname="helv", fontsize=fontsize)
        line_height = fontsize * 1.42
        box_height = (line_height * len(lines)) + (padding * 2)
        self.ensure_space(box_height + 8)
        assert self.page is not None
        rect = fitz.Rect(MARGIN_X, self.cursor_y, PAGE_WIDTH - MARGIN_X, self.cursor_y + box_height)
        self.page.draw_rect(rect, color=COLOR_LINE, fill=COLOR_ACCENT_LIGHT, width=1)
        text_y = self.cursor_y + padding + fontsize
        for line in lines:
            self.page.insert_text(
                fitz.Point(MARGIN_X + padding, text_y),
                line,
                fontname="helv",
                fontsize=fontsize,
                color=COLOR_TEXT,
            )
            text_y += line_height
        self.cursor_y += box_height + 10

    def add_collection_table(self, collections: list[CollectionSummary]) -> None:
        header_height = 24
        row_height = 22
        total_height = header_height + (row_height * len(collections)) + 10
        self.ensure_space(total_height)
        assert self.page is not None

        left = MARGIN_X
        right = PAGE_WIDTH - MARGIN_X
        label_right = right - 90
        table_top = self.cursor_y

        self.page.draw_rect(
            fitz.Rect(left, table_top, right, table_top + header_height),
            color=COLOR_ACCENT,
            fill=COLOR_ACCENT,
        )
        self.page.insert_text(
            fitz.Point(left + 10, table_top + 16),
            "Collection",
            fontname="hebo",
            fontsize=11,
            color=COLOR_WHITE,
        )
        self.page.insert_text(
            fitz.Point(label_right + 10, table_top + 16),
            "Items",
            fontname="hebo",
            fontsize=11,
            color=COLOR_WHITE,
        )

        y = table_top + header_height
        for index, collection in enumerate(collections):
            fill = COLOR_ROW_ALT if index % 2 == 0 else COLOR_WHITE
            self.page.draw_rect(
                fitz.Rect(left, y, right, y + row_height),
                color=COLOR_LINE,
                fill=fill,
                width=0.5,
            )
            self.page.draw_line(
                fitz.Point(label_right, y),
                fitz.Point(label_right, y + row_height),
                color=COLOR_LINE,
                width=0.5,
            )
            self.page.insert_text(
                fitz.Point(left + 10, y + 15),
                collection.label,
                fontname="helv",
                fontsize=10.5,
                color=COLOR_TEXT,
            )
            self.page.insert_text(
                fitz.Point(label_right + 10, y + 15),
                f"{collection.count:,}",
                fontname="hebo",
                fontsize=10.5,
                color=COLOR_TEXT,
            )
            y += row_height
        self.cursor_y = y + 10


def wrap_text(text: str, width: float, fontname: str, fontsize: float) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if fitz.get_text_length(candidate, fontname=fontname, fontsize=fontsize) <= width:
            current = candidate
            continue
        lines.append(current)
        current = word
    lines.append(current)
    return lines


def build_qr_png_bytes(url: str) -> bytes:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def load_version() -> str:
    data = json.loads(PACKAGE_JSON_PATH.read_text(encoding="utf-8"))
    return str(data.get("version", "0.0.0"))


def load_collection_summaries(collection_ids: list[str] | None = None) -> list[CollectionSummary]:
    index_data = json.loads(COLLECTION_INDEX_PATH.read_text(encoding="utf-8"))
    requested_ids = set(collection_ids or [])
    collections: list[CollectionSummary] = []
    for entry in index_data.get("collections", []):
        collection_id = str(entry.get("id", ""))
        if requested_ids and collection_id not in requested_ids:
            continue
        catalog_path = ROOT / entry["catalog"]
        count = 0
        if catalog_path.exists():
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            count = len(catalog.get("items", []))
        collections.append(
            CollectionSummary(
                collection_id=collection_id,
                label=str(entry.get("label", "Unknown Collection")),
                grade=int(entry.get("grade", 0)),
                subject=str(entry.get("subject", "")),
                count=count,
            )
        )
    collections.sort(key=lambda item: (item.grade, item.subject, item.label))
    if requested_ids:
        found_ids = {entry.collection_id for entry in collections}
        missing_ids = sorted(requested_ids - found_ids)
        if missing_ids:
            missing_display = ", ".join(missing_ids)
            raise ValueError(f"Unknown collection id(s): {missing_display}")
    return collections


def format_label_list(labels: list[str]) -> str:
    if not labels:
        return "selected STAAR collections"
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    if len(labels) == 3:
        return f"{labels[0]}, {labels[1]}, and {labels[2]}"
    if len(labels) == 4:
        return f"{labels[0]}, {labels[1]}, {labels[2]}, and {labels[3]}"
    return f"{len(labels)} selected collections"


def infer_installers_context_label(collections: list[CollectionSummary]) -> str:
    if not collections:
        return "desktop"
    grades = {entry.grade for entry in collections}
    if len(grades) == 1:
        grade = next(iter(grades))
        return f"Grade {grade}"
    if len(collections) == 1:
        return collections[0].label
    return "selected"


def build_download_panels(
    *,
    download_url: str | None,
    windows_installer_url: str,
    macos_installer_url: str,
    download_title: str,
    download_button_label: str,
) -> tuple[list[DownloadPanel], str]:
    if download_url:
        return (
            [
                DownloadPanel(
                    title=download_title,
                    button_label=download_button_label,
                    url=download_url,
                )
            ],
            "HTML file",
        )

    return (
        [
            DownloadPanel(
                title="WINDOWS INSTALLER",
                button_label="Open Windows Installer",
                url=windows_installer_url,
            ),
            DownloadPanel(
                title="MACOS INSTALLER",
                button_label="Open macOS Installer",
                url=macos_installer_url,
            ),
        ],
        "desktop installers",
    )


def build_launch_steps(*, delivery_mode: str) -> list[str]:
    if delivery_mode == "html":
        return [
            "Download the single HTML file using the link or QR code shown at the top of this guide.",
            "Save the file to your computer, then open the .html file in Microsoft Edge or Google Chrome.",
            "Wait for the app to finish loading. The first open may take a moment because the file includes local catalogs and images.",
        ]

    return [
        "Download the installer that matches your computer. Use the Windows installer on Windows and the Mac installer on macOS. Both installer links and QR codes are shown at the top of this guide.",
        "Open the installer and follow the prompts. After installation, launch STAAR Problem Browser from your desktop or applications list.",
        "Wait for the startup splash screen to finish. The first collection load may take a moment because the app is preparing local data and images.",
    ]


def build_launch_callout(*, delivery_mode: str) -> str:
    if delivery_mode == "html":
        return (
            "No installation is required. The app runs locally from a single HTML file after download. "
            "You do not need the original STAAR source PDFs to browse questions, build tests, or print packets."
        )

    return (
        "The app runs locally after installation. You do not need the original STAAR source PDFs to browse questions, "
        "build tests, or print packets."
    )


def build_troubleshooting_bullets(*, delivery_mode: str) -> list[str]:
    bullets = [
        "Startup feels slow: wait through the first collection load. Large local image sets can take extra time to prepare.",
        "Nothing matches the current filters: clear one or more filters or use Reset Filters to return to the full collection.",
        "Printing is incomplete: reopen print preview and verify that the selected questions and passage bundles are still visible.",
        "A passage image is missing: do not use that packet until the linked source image is restored.",
    ]

    if delivery_mode == "html":
        bullets.append(
            "The file opens in the wrong app or as text: right-click the .html file and open it with Microsoft Edge or Google Chrome."
        )
        return bullets

    bullets.append("The installer is blocked by the operating system: use the signed installer build that ships with your public release.")
    return bullets


def build_cover_subtitle(*, delivery_mode: str) -> str:
    if delivery_mode == "html":
        return "Teacher guide for downloading, opening, browsing, filtering, building tests, and printing packets."

    return "Teacher guide for installing, browsing, filtering, building tests, and printing packets."


def build_collection_choice_instruction(collections: list[CollectionSummary]) -> str:
    if len(collections) == 1:
        return f"Open the collection menu and choose {collections[0].label}."

    grades = {entry.grade for entry in collections}
    subjects = {entry.subject for entry in collections}
    if len(grades) == 1 and len(subjects) == len(collections):
        grade = next(iter(grades))
        return f"Open the collection menu and choose the Grade {grade} subject you want to work in."

    return "Open the collection menu and choose the grade and subject you want to work in."


def build_guide(
    output_path: Path,
    windows_installer_url: str,
    macos_installer_url: str,
    download_url: str | None = None,
    download_title: str = "HTML FILE DOWNLOAD",
    download_button_label: str = "Open HTML File Download",
    collection_ids: list[str] | None = None,
    title: str = "STAAR Problem Browser User Guide",
    cover_title: str | None = None,
    edition_label: str | None = None,
) -> Path:
    version = load_version()
    collections = load_collection_summaries(collection_ids=collection_ids)
    total_items = sum(entry.count for entry in collections)
    if not collections:
        raise ValueError("No collections matched the requested guide scope.")

    scope_descriptor = format_label_list([entry.label for entry in collections])
    installers_context_label = infer_installers_context_label(collections)
    download_panels, delivery_label = build_download_panels(
        download_url=download_url,
        windows_installer_url=windows_installer_url,
        macos_installer_url=macos_installer_url,
        download_title=download_title,
        download_button_label=download_button_label,
    )
    delivery_mode = "html" if download_url else "installers"
    guide = GuidePdf(
        title=title,
        version=version,
        cover_title=cover_title,
        edition_label=edition_label,
    )

    guide.add_cover(
        total_items=total_items,
        collection_count=len(collections),
        collections=collections,
        download_panels=download_panels,
        scope_descriptor=scope_descriptor,
        delivery_context_label=f"{installers_context_label} {delivery_label}".strip(),
        cover_subtitle=build_cover_subtitle(delivery_mode=delivery_mode),
    )

    guide.add_page(show_header=True)
    guide.add_heading("1. Download and Launch" if delivery_mode == "html" else "1. Install and Launch")
    guide.add_numbered_steps(build_launch_steps(delivery_mode=delivery_mode))
    guide.add_callout(build_launch_callout(delivery_mode=delivery_mode))

    guide.add_heading("2. Included Collections")
    guide.add_paragraph(
        "This build currently includes the following ready-to-use collections. Counts are based on the packaged catalog data in this repo."
    )
    guide.add_collection_table(collections)

    guide.add_page(show_header=True)
    guide.add_heading("3. Choose a Collection and Filter Questions")
    guide.add_numbered_steps(
        [
            build_collection_choice_instruction(collections),
            "Use the search box when you already know a keyword, TEKS idea, or question stem you want to find quickly.",
            "Refine the visible question set with filters such as TEKS, year, difficulty, item type, content, and review status.",
            "Watch the summary area as you filter. It updates to show how many questions and passage bundles are still visible.",
        ]
    )
    guide.add_bullets(
        [
            "TEKS filter: narrow the catalog to one or more standards.",
            "Year filter: focus on recent released questions or compare across years.",
            "Difficulty filter: use easy, medium, or hard groups based on state percent-correct data.",
            "Item type and content filters: isolate multiple choice, multi-select, constructed response, numeric response, and content strands.",
            "Review only: surface items that may need an extra teacher check before printing.",
        ]
    )
    guide.add_callout(
        "ELAR collections can show passage bundles. If questions share a reading passage or paired passage set, the app keeps those linked resources together."
    )

    guide.add_heading("4. Build a Test Fast")
    guide.add_numbered_steps(
        [
            "Add individual questions from the visible results, or use Add Filtered Questions to bring in the whole filtered set at once.",
            "Use built-in presets when you want a quick first draft. Presets include Hardest Test, Easier Test, Latest Questions Only, Spiral Review, Single-TEKS Mastery, Intervention Set, Reteach Set, Benchmark Lite, Mini Quiz, Warm-Up, and Exit Ticket.",
            "Enter a test title and teacher or class label so the printed packet is already organized.",
            "Reorder questions, remove questions, or swap them out until the packet matches your instructional goal.",
        ]
    )

    guide.add_page(show_header=True)
    guide.add_heading("5. Print Student Packets and Answer Keys")
    guide.add_numbered_steps(
        [
            "When your selection is ready, choose Print Student Test to create the student-facing packet.",
            "Choose Print Answer Key to print the teacher key with answer choices and metadata.",
            "Review the print preview before sharing. This is the last check for question order, passage grouping, and formatting.",
        ]
    )
    guide.add_bullets(
        [
            "ELAR passage pages print with their linked questions, including multi-page and paired-passage sets.",
            "Teacher answer keys include details such as TEKS, year, item type, difficulty, and state percent-correct information when available.",
            "Constructed response and response-template items are preserved in the printable layout.",
        ]
    )
    guide.add_callout(
        'If a question is marked "needs review" or a passage image is missing, inspect it before giving the packet to students.'
    )

    guide.add_heading("6. Common Classroom Uses")
    guide.add_bullets(
        [
            "Daily spiral review",
            "Targeted intervention groups",
            "Reteach after a quiz or checkpoint",
            "Benchmark-style mixed review",
            "Exit tickets and warm-ups",
            "Single-TEKS mastery practice",
            "Fast sub plans or station work",
        ]
    )

    guide.add_heading("7. Troubleshooting")
    guide.add_bullets(build_troubleshooting_bullets(delivery_mode=delivery_mode))
    guide.add_paragraph(
        "For buyer support, include your store email or support instructions in the Start Here guide that ships with the product."
    )

    guide.save(output_path)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the STAAR Problem Browser user guide PDF.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output PDF path. Defaults to {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--windows-installer-url",
        default=DEFAULT_WINDOWS_INSTALLER_URL,
        help="Visible and clickable Windows installer URL to place on the cover.",
    )
    parser.add_argument(
        "--macos-installer-url",
        default=DEFAULT_MACOS_INSTALLER_URL,
        help="Visible and clickable macOS installer URL to place on the cover.",
    )
    parser.add_argument(
        "--download-url",
        help="Visible and clickable single download URL to place on the cover instead of installer links.",
    )
    parser.add_argument(
        "--download-title",
        default="HTML FILE DOWNLOAD",
        help="Short uppercase title for the single download panel.",
    )
    parser.add_argument(
        "--download-button-label",
        default="Open HTML File Download",
        help="Button label for the single download panel.",
    )
    parser.add_argument(
        "--collection-ids",
        help="Comma-separated collection ids to include, such as grade-4-elar,grade-4-math.",
    )
    parser.add_argument(
        "--title",
        default="STAAR Problem Browser User Guide",
        help="Header and footer title for the generated guide.",
    )
    parser.add_argument(
        "--cover-title",
        help="Optional cover title override. Defaults to the guide title.",
    )
    parser.add_argument(
        "--edition-label",
        help="Optional short label shown below the cover title, such as Grade 4 Edition.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    collection_ids = None
    if args.collection_ids:
        collection_ids = [entry.strip() for entry in str(args.collection_ids).split(",") if entry.strip()]
    output_path = build_guide(
        args.output.resolve(),
        windows_installer_url=str(args.windows_installer_url),
        macos_installer_url=str(args.macos_installer_url),
        download_url=str(args.download_url) if args.download_url else None,
        download_title=str(args.download_title),
        download_button_label=str(args.download_button_label),
        collection_ids=collection_ids,
        title=str(args.title),
        cover_title=str(args.cover_title) if args.cover_title else None,
        edition_label=str(args.edition_label) if args.edition_label else None,
    )
    print(f"Wrote user guide PDF to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
