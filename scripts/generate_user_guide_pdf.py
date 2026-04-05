from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import fitz


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
    label: str
    grade: int
    subject: str
    count: int


class GuidePdf:
    def __init__(self, title: str, version: str) -> None:
        self.title = title
        self.version = version
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
        windows_installer_url: str,
        macos_installer_url: str,
    ) -> None:
        self.add_page(show_header=False)
        assert self.page is not None

        self.page.draw_rect(
            fitz.Rect(0, 0, PAGE_WIDTH, 286),
            color=COLOR_ACCENT,
            fill=COLOR_ACCENT,
        )
        self.page.draw_rect(
            fitz.Rect(MARGIN_X, 314, PAGE_WIDTH - MARGIN_X, 426),
            color=COLOR_LINE,
            fill=COLOR_ACCENT_LIGHT,
            width=1,
        )

        self.page.insert_textbox(
            fitz.Rect(MARGIN_X, 68, PAGE_WIDTH - MARGIN_X, 144),
            self.title,
            fontname="hebo",
            fontsize=28,
            color=COLOR_WHITE,
            align=0,
        )
        self.page.insert_textbox(
            fitz.Rect(MARGIN_X, 142, PAGE_WIDTH - MARGIN_X, 188),
            "Teacher Guide for installing, browsing, filtering, building tests, and printing packets.",
            fontname="helv",
            fontsize=13,
            color=COLOR_WHITE,
            align=0,
        )

        panel_gap = 12
        panel_width = (CONTENT_WIDTH - panel_gap) / 2
        left_panel = fitz.Rect(MARGIN_X, 188, MARGIN_X + panel_width, 300)
        right_panel = fitz.Rect(MARGIN_X + panel_width + panel_gap, 188, PAGE_WIDTH - MARGIN_X, 300)

        self._draw_download_panel(
            panel_rect=left_panel,
            title="WINDOWS INSTALLER",
            button_label="Open Windows Installer",
            url=windows_installer_url,
        )
        self._draw_download_panel(
            panel_rect=right_panel,
            title="MACOS INSTALLER",
            button_label="Open macOS Installer",
            url=macos_installer_url,
        )

        self.page.insert_text(
            fitz.Point(MARGIN_X, 198),
            "",
            fontname="helv",
            fontsize=1,
            color=COLOR_WHITE,
        )

        self.page.insert_textbox(
            fitz.Rect(MARGIN_X + 20, 336, PAGE_WIDTH - MARGIN_X - 20, 406),
            (
                f"This build includes {collection_count} ready collections and {total_items:,} released STAAR items "
                "across Grade 3-6 Math, ELAR, and Grade 5 Science."
            ),
            fontname="hebo",
            fontsize=15,
            color=COLOR_TEXT,
            align=0,
        )

        self.page.insert_textbox(
            fitz.Rect(MARGIN_X, 452, PAGE_WIDTH - MARGIN_X, 720),
            (
                "Included collections:\n"
                + "\n".join(f"- {entry.label}" for entry in collections)
                + "\n\nUse this guide as the PDF that ships with your desktop installers or TPT download."
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
        url_rect = fitz.Rect(panel_rect.x0 + 14, panel_rect.y0 + 68, panel_rect.x1 - 14, panel_rect.y1 - 10)
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
        self.add_uri_link(button_rect, url)
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


def load_version() -> str:
    data = json.loads(PACKAGE_JSON_PATH.read_text(encoding="utf-8"))
    return str(data.get("version", "0.0.0"))


def load_collection_summaries() -> list[CollectionSummary]:
    index_data = json.loads(COLLECTION_INDEX_PATH.read_text(encoding="utf-8"))
    collections: list[CollectionSummary] = []
    for entry in index_data.get("collections", []):
        catalog_path = ROOT / entry["catalog"]
        count = 0
        if catalog_path.exists():
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            count = len(catalog.get("items", []))
        collections.append(
            CollectionSummary(
                label=str(entry.get("label", "Unknown Collection")),
                grade=int(entry.get("grade", 0)),
                subject=str(entry.get("subject", "")),
                count=count,
            )
        )
    collections.sort(key=lambda item: (item.grade, item.subject, item.label))
    return collections


def build_guide(output_path: Path, windows_installer_url: str, macos_installer_url: str) -> Path:
    version = load_version()
    collections = load_collection_summaries()
    total_items = sum(entry.count for entry in collections)
    guide = GuidePdf(title="STAAR Problem Browser User Guide", version=version)

    guide.add_cover(
        total_items=total_items,
        collection_count=len(collections),
        collections=collections,
        windows_installer_url=windows_installer_url,
        macos_installer_url=macos_installer_url,
    )

    guide.add_page(show_header=True)
    guide.add_heading("1. Install and Launch")
    guide.add_numbered_steps(
        [
            "Download the installer that matches your computer. Use the Windows installer on Windows and the Mac installer on macOS. Both installer links are shown at the top of this guide.",
            "Open the installer and follow the prompts. After installation, launch STAAR Problem Browser from your desktop or applications list.",
            "Wait for the startup splash screen to finish. The first collection load may take a moment because the app is preparing local data and images.",
        ]
    )
    guide.add_callout(
        "The app runs locally after installation. You do not need the original STAAR source PDFs to browse questions, build tests, or print packets."
    )

    guide.add_heading("2. Included Collections")
    guide.add_paragraph(
        "This build currently includes the following ready-to-use collections. Counts are based on the packaged catalog data in this repo."
    )
    guide.add_collection_table(collections)

    guide.add_page(show_header=True)
    guide.add_heading("3. Choose a Collection and Filter Questions")
    guide.add_numbered_steps(
        [
            "Open the collection menu and choose the grade and subject you want to work in.",
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
    guide.add_bullets(
        [
            "Startup feels slow: wait through the first collection load. Large local image sets can take extra time to prepare.",
            "Nothing matches the current filters: clear one or more filters or use Reset Filters to return to the full collection.",
            "Printing is incomplete: reopen print preview and verify that the selected questions and passage bundles are still visible.",
            "A passage image is missing: do not use that packet until the linked source image is restored.",
            "The installer is blocked by the operating system: use the signed installer build that ships with your public release.",
        ]
    )
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = build_guide(
        args.output.resolve(),
        windows_installer_url=str(args.windows_installer_url),
        macos_installer_url=str(args.macos_installer_url),
    )
    print(f"Wrote user guide PDF to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
