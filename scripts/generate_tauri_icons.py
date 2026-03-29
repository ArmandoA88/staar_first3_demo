from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ICONS_DIR = ROOT / "src-tauri" / "icons"
NAVY = (0, 40, 104, 255)
RED = (191, 10, 48, 255)
WHITE = (255, 255, 255, 255)
INK = (22, 48, 66, 255)
FRAME = (22, 48, 66, 44)
SHADOW = (6, 20, 48, 86)


def star_points(center_x: float, center_y: float, outer_radius: float, inner_radius: float) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    start_angle = -math.pi / 2
    for index in range(10):
        radius = outer_radius if index % 2 == 0 else inner_radius
        angle = start_angle + index * math.pi / 5
        points.append((center_x + math.cos(angle) * radius, center_y + math.sin(angle) * radius))
    return points


def make_base_image(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    inset = max(1, round(size * 0.07))
    radius = max(4, round(size * 0.19))
    bounds = (inset, inset, size - inset, size - inset)
    x0, y0, x1, y1 = bounds
    width = x1 - x0
    height = y1 - y0
    flag_split = x0 + round(width * 0.36)
    row_split = y0 + round(height * 0.5)

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(bounds, radius=radius, fill=255)

    flag = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    flag_draw = ImageDraw.Draw(flag)
    flag_draw.rectangle(bounds, fill=WHITE)
    flag_draw.rectangle((x0, y0, flag_split, y1), fill=NAVY)
    flag_draw.rectangle((flag_split, row_split, x1, y1), fill=RED)

    sheen = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sheen_draw = ImageDraw.Draw(sheen)
    sheen_draw.polygon(
        [
            (x0, y0),
            (x0 + round(width * 0.72), y0),
            (x0 + round(width * 0.44), y0 + round(height * 0.45)),
            (x0, y0 + round(height * 0.26)),
        ],
        fill=(255, 255, 255, 26),
    )
    flag.alpha_composite(sheen)
    image = Image.composite(flag, image, mask)

    star_center_x = x0 + width * 0.54
    star_center_y = y0 + height * 0.5
    star_outer = width * 0.26
    star_inner = star_outer * 0.45
    points = star_points(star_center_x, star_center_y, star_outer, star_inner)

    shadow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_offset_x = max(1, round(size * 0.012))
    shadow_offset_y = max(1, round(size * 0.018))
    shadow_draw.polygon(
        [(x + shadow_offset_x, y + shadow_offset_y) for x, y in points],
        fill=SHADOW,
    )
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(max(1, round(size * 0.03))))
    image.alpha_composite(shadow_layer)

    star_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    star_draw = ImageDraw.Draw(star_layer)
    star_draw.polygon(points, fill=WHITE, outline=INK, width=max(1, round(size * 0.038)))
    image.alpha_composite(star_layer)

    frame_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    frame_draw = ImageDraw.Draw(frame_layer)
    frame_draw.rounded_rectangle(bounds, radius=radius, outline=FRAME, width=max(1, round(size * 0.02)))
    image.alpha_composite(frame_layer)

    return image


def save_png(size: int, filename: str) -> None:
    image = make_base_image(size)
    image.save(ICONS_DIR / filename)


def save_ico() -> None:
    image = make_base_image(512)
    image.save(
        ICONS_DIR / "icon.ico",
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )


def save_icns() -> None:
    image = make_base_image(1024)
    image.save(ICONS_DIR / "icon.icns", format="ICNS")


def main() -> int:
    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    save_png(32, "32x32.png")
    save_png(128, "128x128.png")
    save_png(256, "128x128@2x.png")
    save_png(30, "Square30x30Logo.png")
    save_png(44, "Square44x44Logo.png")
    save_png(71, "Square71x71Logo.png")
    save_png(89, "Square89x89Logo.png")
    save_png(107, "Square107x107Logo.png")
    save_png(142, "Square142x142Logo.png")
    save_png(150, "Square150x150Logo.png")
    save_png(284, "Square284x284Logo.png")
    save_png(310, "Square310x310Logo.png")
    save_png(50, "StoreLogo.png")
    save_ico()
    save_icns()
    print(f"Generated Tauri icons in {ICONS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
