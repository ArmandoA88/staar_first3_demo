from __future__ import annotations

import math
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "marketing"
HTML_PATH = ROOT / "STAARProblemBrowserGrade4.html"
SCREENSHOT_PATH = OUT_DIR / "grade4_app_screenshot.png"

QUESTION_PATHS = [
    ROOT / "collections" / "grade-4" / "elar" / "images" / "extracted" / "g4_elar_4.6C_2025_q5.png",
    ROOT / "collections" / "grade-4" / "math" / "images" / "extracted" / "g4_math_4.2A_2024_q2.png",
    ROOT / "collections" / "grade-4" / "math" / "images" / "extracted" / "g4_math_4.6B_2023_q1.png",
]

COLORS = {
    "navy": "#1E3D73",
    "navy_dark": "#152B52",
    "red": "#C93E43",
    "cream": "#F6F1EA",
    "warm": "#E9DDD2",
    "paper": "#FFFDF8",
    "ink": "#2B2B2B",
    "brown": "#AA774D",
    "brown_dark": "#8D5E39",
    "gold": "#E8B860",
    "slate": "#576579",
    "green": "#6E8B5C",
    "panel": "#FCF8F1",
}


def ensure_output_dir() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def ensure_screenshot() -> Path:
    if SCREENSHOT_PATH.exists():
        return SCREENSHOT_PATH

    edge_candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    edge_path = next((path for path in edge_candidates if path.exists()), None)
    if not edge_path:
        raise FileNotFoundError("Microsoft Edge was not found. Cannot capture the Grade 4 HTML screenshot.")
    if not HTML_PATH.exists():
        raise FileNotFoundError(f"Missing HTML bundle: {HTML_PATH}")

    command = [
        str(edge_path),
        "--headless=new",
        "--disable-gpu",
        "--window-size=1440,1024",
        "--virtual-time-budget=15000",
        "--hide-scrollbars",
        f"--screenshot={SCREENSHOT_PATH}",
        HTML_PATH.resolve().as_uri(),
    ]
    subprocess.run(command, check=True, cwd=str(OUT_DIR))
    if not SCREENSHOT_PATH.exists():
        raise FileNotFoundError("Edge did not create the Grade 4 screenshot.")
    return SCREENSHOT_PATH


def font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_dir = Path(r"C:\Windows\Fonts")
    for candidate in candidates:
        path = font_dir / candidate
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


FONT_SANS = lambda size: font(["arial.ttf", "segoeui.ttf"], size)
FONT_SANS_BOLD = lambda size: font(["arialbd.ttf", "segoeuib.ttf"], size)
FONT_HEAVY = lambda size: font(["impact.ttf", "arialbd.ttf"], size)
FONT_SCRIPT = lambda size: font(["BRUSHSCI.TTF", "FRSCRIPT.TTF", "segoescb.ttf"], size)
FONT_SERIF_BOLD = lambda size: font(["georgiab.ttf", "arialbd.ttf"], size)


def hex_to_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def add_shadow(base: Image.Image, mask_box: tuple[int, int, int, int], radius: int = 28, alpha: int = 70, offset: tuple[int, int] = (0, 10)) -> None:
    x0, y0, x1, y1 = mask_box
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    ox, oy = offset
    draw.rounded_rectangle((x0 + ox, y0 + oy, x1 + ox, y1 + oy), radius=radius, fill=(0, 0, 0, alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(shadow)


def rounded_panel(base: Image.Image, box: tuple[int, int, int, int], fill: str, radius: int = 28, outline: str | None = None, width: int = 3, shadow: bool = True) -> None:
    if shadow:
        add_shadow(base, box, radius=radius)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def create_gradient_background(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    width, height = size
    top_rgb = hex_to_rgba(top)
    bottom_rgb = hex_to_rgba(bottom)
    image = Image.new("RGBA", size)
    pixels = image.load()
    for y in range(height):
        t = y / max(1, height - 1)
        row = tuple(int(top_rgb[i] * (1 - t) + bottom_rgb[i] * t) for i in range(3)) + (255,)
        for x in range(width):
            pixels[x, y] = row
    return image


def add_blobs(base: Image.Image, specs: list[tuple[int, int, int, str, int]]) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x, y, radius, color, alpha in specs:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=hex_to_rgba(color, alpha))
    overlay = overlay.filter(ImageFilter.GaussianBlur(40))
    base.alpha_composite(overlay)


def star_points(cx: float, cy: float, outer_r: float, inner_r: float, points: int = 5) -> list[tuple[float, float]]:
    result = []
    for i in range(points * 2):
        angle = -math.pi / 2 + i * math.pi / points
        radius = outer_r if i % 2 == 0 else inner_r
        result.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
    return result


def draw_texas_badge(base: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    width = x1 - x0
    height = y1 - y0
    badge = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width, height), radius=18, fill=255)

    badge_draw = ImageDraw.Draw(badge)
    badge_draw.rounded_rectangle((0, 0, width, height), radius=18, fill=COLORS["panel"], outline=COLORS["navy"], width=4)
    split_x = int(width * 0.42)
    badge_draw.rectangle((0, 0, split_x, height), fill=COLORS["navy"])
    badge_draw.rectangle((split_x, height // 2, width, height), fill=COLORS["red"])
    badge_draw.rectangle((split_x, 0, width, height // 2), fill="#FBFAF7")
    badge_draw.polygon(star_points(split_x * 0.52, height * 0.48, height * 0.22, height * 0.09), fill="#FBFAF7")

    clipped = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    clipped.paste(badge, mask=mask)
    base.alpha_composite(clipped, dest=(x0, y0))


def text_size(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.ImageFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=text_font)
    return right - left, bottom - top


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, text_font: ImageFont.ImageFont, fill: str, anchor: str | None = None) -> None:
    draw.text(xy, text, font=text_font, fill=fill, anchor=anchor)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=text_font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def trim_white(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, background)
    bbox = diff.getbbox()
    return rgb.crop(bbox) if bbox else rgb


def load_question_sheet(path: Path, size: tuple[int, int], angle: float = 0) -> Image.Image:
    image = trim_white(Image.open(path))
    paper = Image.new("RGBA", size, hex_to_rgba(COLORS["paper"]))
    paper_draw = ImageDraw.Draw(paper)
    paper_draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=12, fill=COLORS["paper"], outline="#D8D0C6", width=3)
    inset = 18
    fitted = ImageOps.contain(image, (size[0] - inset * 2, size[1] - inset * 2), Image.Resampling.LANCZOS)
    fx = (size[0] - fitted.width) // 2
    fy = (size[1] - fitted.height) // 2
    paper.alpha_composite(fitted.convert("RGBA"), dest=(fx, fy))
    if angle:
        paper = paper.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    return paper


def prepare_screen(screenshot_path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(screenshot_path).convert("RGBA")
    crop = image.crop((20, 10, image.width - 20, image.height - 95))
    return ImageOps.fit(crop, size, Image.Resampling.LANCZOS, centering=(0.5, 0.02))


def paste_center(base: Image.Image, overlay: Image.Image, xy: tuple[int, int]) -> None:
    base.alpha_composite(overlay, dest=xy)


def make_laptop(screen: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = size
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    screen_box = (30, 20, width - 30, int(height * 0.74))
    add_shadow(canvas, screen_box, radius=26, alpha=100, offset=(0, 16))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(screen_box, radius=26, fill="#2F333A")
    inner = (screen_box[0] + 14, screen_box[1] + 14, screen_box[2] - 14, screen_box[3] - 14)
    draw.rounded_rectangle(inner, radius=14, fill="#0A0A0A")
    fitted = ImageOps.fit(screen, (inner[2] - inner[0], inner[3] - inner[1]), Image.Resampling.LANCZOS)
    canvas.alpha_composite(fitted, dest=(inner[0], inner[1]))

    base_top = int(height * 0.73)
    base_polygon = [
        (12, base_top),
        (width - 12, base_top),
        (width - 78, height - 20),
        (78, height - 20),
    ]
    draw.polygon(base_polygon, fill="#808792")
    draw.polygon(
        [(40, base_top + 14), (width - 40, base_top + 14), (width - 96, height - 44), (96, height - 44)],
        fill="#A9AFB7",
    )
    draw.rounded_rectangle((width // 2 - 48, height - 88, width // 2 + 48, height - 36), radius=10, outline="#787F8B", width=3)
    return canvas


def make_monitor(screen: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = size
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    frame = (0, 0, width, int(height * 0.78))
    add_shadow(canvas, frame, radius=30, alpha=90, offset=(0, 18))
    draw.rounded_rectangle(frame, radius=28, fill="#22262D")
    inner = (24, 22, width - 24, int(height * 0.78) - 24)
    draw.rounded_rectangle(inner, radius=16, fill="#0E0E10")
    fitted = ImageOps.fit(screen, (inner[2] - inner[0], inner[3] - inner[1]), Image.Resampling.LANCZOS)
    canvas.alpha_composite(fitted, dest=(inner[0], inner[1]))

    stem = (width // 2 - 28, int(height * 0.78), width // 2 + 28, int(height * 0.93))
    draw.rounded_rectangle(stem, radius=10, fill="#4A4F57")
    base_rect = (width // 2 - 110, int(height * 0.9), width // 2 + 110, height)
    draw.rounded_rectangle(base_rect, radius=16, fill="#5D626B")
    return canvas


def draw_checkmark(draw: ImageDraw.ImageDraw, center: tuple[int, int], size: int, color: str) -> None:
    cx, cy = center
    draw.line((cx - size // 2, cy, cx - size // 8, cy + size // 3), fill=color, width=5)
    draw.line((cx - size // 8, cy + size // 3, cx + size // 2, cy - size // 3), fill=color, width=5)


def draw_checklist_panel(base: Image.Image, box: tuple[int, int, int, int], lines: list[str]) -> None:
    rounded_panel(base, box, COLORS["paper"], radius=26, outline="#DCCFC2")
    draw = ImageDraw.Draw(base)
    x0, y0, x1, y1 = box
    y = y0 + 28
    text_font = FONT_SANS_BOLD(30)
    line_gap = 14
    max_width = (x1 - x0) - 88
    line_height = 32

    for item in lines:
        draw_checkmark(draw, (x0 + 34, y + 18), 26, COLORS["red"])
        wrapped = wrap_text(draw, item, text_font, max_width)
        for index, line in enumerate(wrapped):
            draw_text(draw, (x0 + 62, y + index * line_height), line, text_font, COLORS["ink"])
        y += len(wrapped) * line_height + line_gap


def draw_chip_row(base: Image.Image, labels: list[str], y: int) -> None:
    draw = ImageDraw.Draw(base)
    x = 20
    gap = 12
    text_font = FONT_SANS_BOLD(26)
    for label in labels:
        tw, th = text_size(draw, label, text_font)
        width = tw + 34
        box = (x, y, x + width, y + 46)
        draw.rounded_rectangle(box, radius=14, fill=COLORS["navy"], outline="#35548B", width=2)
        draw_text(draw, (x + width // 2, y + 24), label, text_font, "#FFFFFF", anchor="mm")
        x += width + gap


def draw_footer_strip(base: Image.Image, labels: list[str], y: int, height: int) -> None:
    draw = ImageDraw.Draw(base)
    draw.rectangle((0, y, base.width, y + height), fill=COLORS["navy"])
    text_font = FONT_SANS_BOLD(26)
    total_width = sum(text_size(draw, label, text_font)[0] for label in labels) + (len(labels) - 1) * 42
    x = (base.width - total_width) // 2
    for index, label in enumerate(labels):
        draw_checkmark(draw, (x + 12, y + height // 2), 18, "#FFFFFF")
        draw_text(draw, (x + 26, y + height // 2 + 1), label, text_font, "#FFFFFF", anchor="lm")
        x += text_size(draw, label, text_font)[0] + 42


def draw_footer_note(base: Image.Image, text: str, y: int, height: int) -> None:
    draw = ImageDraw.Draw(base)
    draw.rectangle((0, y, base.width, y + height), fill="#F3EFE8")
    draw_text(draw, (base.width // 2, y + height // 2), text, FONT_SANS_BOLD(24), COLORS["navy_dark"], anchor="mm")


def add_paper_stack(base: Image.Image, placements: list[tuple[Image.Image, tuple[int, int]]]) -> None:
    for paper, (x, y) in placements:
        shadow_box = (x, y, x + paper.width, y + paper.height)
        add_shadow(base, shadow_box, radius=18, alpha=70, offset=(0, 8))
        paste_center(base, paper, (x, y))


def build_promo_one(screen: Image.Image, papers: list[Image.Image]) -> Image.Image:
    base = create_gradient_background((1080, 1080), COLORS["cream"], "#EEE3D7")
    add_blobs(base, [(170, 290, 150, "#FFFFFF", 145), (870, 310, 140, "#F7E5D8", 160), (960, 120, 90, "#F2D8D1", 150)])
    draw = ImageDraw.Draw(base)

    draw.rectangle((0, 600, 1080, 1080), fill=COLORS["brown"])
    for line_y in range(626, 1080, 42):
        draw.line((0, line_y, 1080, line_y), fill=COLORS["brown_dark"], width=2)

    draw_texas_badge(base, (18, 16, 198, 136))
    draw_text(draw, (216, 18), "STAAR Grade 4", FONT_SANS_BOLD(68), COLORS["navy"])
    draw_text(draw, (216, 74), "ELAR + MATH", FONT_HEAVY(88), COLORS["red"])
    draw_text(draw, (216, 130), "Problem Browser", FONT_SCRIPT(60), COLORS["navy_dark"])
    draw.rounded_rectangle((12, 186, 1068, 238), radius=10, fill=COLORS["navy"])
    draw_text(draw, (540, 212), "LOCAL HTML ASSESSMENT BUILDER | TEKS", FONT_SANS_BOLD(28), "#FFFFFF", anchor="mm")

    laptop = make_laptop(screen, (650, 500))
    paste_center(base, laptop, (56, 246))

    checklist_lines = [
        "1,007 STAAR Questions",
        "679 ELAR + 328 Math",
        "Sort, Search, & Filter by TEKS",
        "Build Printable Tests Fast",
        "Answer Keys Included",
    ]
    draw_checklist_panel(base, (748, 268, 1042, 738), checklist_lines)

    add_paper_stack(
        base,
        [
            (papers[0], (342, 782)),
            (papers[1], (145, 772)),
            (papers[2], (612, 782)),
        ],
    )
    draw_chip_row(base, ["ELA", "Math", "STAAR Prep", "Assessments", "TEKS-Aligned"], 1018)
    return base


def draw_classroom_background(base: Image.Image) -> None:
    add_blobs(base, [(130, 260, 140, "#D8E6D1", 180), (940, 260, 170, "#E8D8CB", 160), (560, 150, 200, "#FFFFFF", 140)])
    draw = ImageDraw.Draw(base)
    draw.rectangle((0, 720, 1080, 935), fill="#BE9066")
    for line_y in range(740, 935, 38):
        draw.line((0, line_y, 1080, line_y), fill="#A97B53", width=2)
    draw.rectangle((0, 935, 1080, 1080), fill="#EFEAE0")
    draw.rounded_rectangle((36, 340, 126, 610), radius=16, fill="#D6E4CC")
    draw.ellipse((48, 280, 112, 344), fill="#EEF5E8")
    draw.rounded_rectangle((44, 540, 102, 740), radius=10, fill="#24354D")
    draw.rectangle((72, 568, 82, 660), fill="#F3C056")
    draw.rectangle((60, 578, 70, 676), fill="#D76B53")
    draw.rectangle((84, 582, 94, 672), fill="#4D7BAA")


def draw_book_and_notebook(base: Image.Image) -> None:
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle((42, 820, 176, 972), radius=10, fill=COLORS["navy"], outline="#3C598D", width=3)
    draw_text(draw, (109, 865), "STAAR", FONT_SANS_BOLD(30), "#FFFFFF", anchor="mm")
    draw_text(draw, (109, 905), "GRADE 4", FONT_SANS_BOLD(28), "#FFFFFF", anchor="mm")

    draw.rounded_rectangle((910, 804, 1034, 956), radius=10, fill="#F7F7F4", outline="#CBD1D7", width=3)
    for offset in range(0, 102, 18):
        draw.line((930, 828 + offset, 1010, 828 + offset), fill="#9FA7B2", width=2)
    draw.line((930, 820, 930, 940), fill=COLORS["red"], width=3)


def build_promo_two(screen: Image.Image, papers: list[Image.Image]) -> Image.Image:
    base = create_gradient_background((1080, 1080), "#F7F3EC", "#E7DBCE")
    draw_classroom_background(base)
    draw_book_and_notebook(base)
    draw = ImageDraw.Draw(base)

    draw.rectangle((10, 10, 1070, 12), fill=COLORS["navy"])
    draw.rectangle((10, 12, 1070, 170), fill="#FAF8F3", outline=COLORS["navy"], width=4)
    draw_text(draw, (194, 30), "STAAR Grade 4", FONT_SANS_BOLD(66), COLORS["navy"])
    draw.rectangle((14, 82, 1066, 164), fill=COLORS["navy"])
    draw_text(draw, (540, 122), "ELAR + Math", FONT_HEAVY(80), "#FFFFFF", anchor="mm")
    draw.rectangle((14, 164, 1066, 252), fill=COLORS["red"])
    draw_text(draw, (540, 196), "Problem Browser", FONT_SANS_BOLD(56), "#FFFFFF", anchor="mm")
    draw_text(draw, (540, 228), "Local HTML Assessment Builder | TEKS", FONT_SANS(24), "#FDECEA", anchor="mm")
    draw_texas_badge(base, (26, 24, 168, 144))

    monitor = make_monitor(screen, (780, 540))
    paste_center(base, monitor, (150, 260))

    keyboard = Image.new("RGBA", (360, 60), (0, 0, 0, 0))
    kdraw = ImageDraw.Draw(keyboard)
    kdraw.rounded_rectangle((0, 0, 360, 60), radius=16, fill="#2F343B")
    for row in range(3):
        for col in range(10):
            x0 = 18 + col * 32
            y0 = 10 + row * 14
            kdraw.rounded_rectangle((x0, y0, x0 + 24, y0 + 10), radius=3, fill="#4E5560")
    paste_center(base, keyboard, (362, 792))

    add_paper_stack(
        base,
        [
            (papers[1], (300, 822)),
            (papers[0], (540, 820)),
        ],
    )

    draw_footer_strip(base, ["Grade 4 ELAR & Math", "Browse, Filter, Build", "Print Tests & Answer Keys"], 938, 58)
    draw_footer_note(base, "TEKS-Aligned  •  Released STAAR Questions  •  Single HTML File", 996, 56)
    return base


def main() -> None:
    ensure_output_dir()
    screenshot_path = ensure_screenshot()
    screen = prepare_screen(screenshot_path, (580, 340))
    papers = [
        load_question_sheet(QUESTION_PATHS[0], (230, 305), angle=-8),
        load_question_sheet(QUESTION_PATHS[1], (225, 300), angle=8),
        load_question_sheet(QUESTION_PATHS[2], (225, 295), angle=-3),
    ]

    promo_one = build_promo_one(screen, papers)
    promo_two = build_promo_two(screen, papers)

    promo_one.convert("RGB").save(OUT_DIR / "staar_grade4_tpt_promo_1.png", quality=95)
    promo_two.convert("RGB").save(OUT_DIR / "staar_grade4_tpt_promo_2.png", quality=95)

    print(OUT_DIR / "staar_grade4_tpt_promo_1.png")
    print(OUT_DIR / "staar_grade4_tpt_promo_2.png")


if __name__ == "__main__":
    main()
