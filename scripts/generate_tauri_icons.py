from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ICONS_DIR = ROOT / "src-tauri" / "icons"


def make_base_image(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), "#f4ece7")
    draw = ImageDraw.Draw(image)

    inset = int(size * 0.08)
    draw.rounded_rectangle(
        (inset, inset, size - inset, size - inset),
        radius=int(size * 0.18),
        fill="#7d4f3f",
    )

    bar_width = int(size * 0.12)
    gap = int(size * 0.08)
    baseline = int(size * 0.24)
    heights = [0.34, 0.5, 0.68]
    start_x = int(size * 0.25)

    for index, height_ratio in enumerate(heights):
        x0 = start_x + index * (bar_width + gap)
        x1 = x0 + bar_width
        y1 = size - baseline
        y0 = int(y1 - size * height_ratio)
        draw.rounded_rectangle((x0, y0, x1, y1), radius=int(size * 0.03), fill="#fff8f4")

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
