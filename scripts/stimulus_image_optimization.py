from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps

STIMULUS_WEBP_QUALITY = 80
STIMULUS_WEBP_METHOD = 6


def normalize_stimulus_image_for_webp(image: Image.Image) -> Image.Image:
    image.load()
    if image.mode == "L":
        return image.copy()
    if image.mode == "LA":
        luminance, alpha = image.split()
        return Image.merge("RGBA", (luminance, luminance, luminance, alpha))
    if "A" in image.getbands():
        rgba = image.convert("RGBA")
        grayscale = ImageOps.grayscale(rgba.convert("RGB"))
        alpha = rgba.getchannel("A")
        return Image.merge("RGBA", (grayscale, grayscale, grayscale, alpha))
    return ImageOps.grayscale(image.convert("RGB"))


def save_grayscale_webp(
    image: Image.Image,
    output_path: Path,
    quality: int = STIMULUS_WEBP_QUALITY,
    method: int = STIMULUS_WEBP_METHOD,
) -> tuple[str, str]:
    prepared_image = normalize_stimulus_image_for_webp(image)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prepared_image.save(output_path, format="WEBP", quality=quality, method=method)
    return image.mode, prepared_image.mode
