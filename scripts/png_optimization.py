from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from PIL import Image, ImageChops


@dataclass(slots=True)
class PngOptimizationResult:
    original_bytes: int
    optimized_bytes: int
    bytes_saved: int
    grayscale_converted: bool
    mode_before: str
    mode_after: str
    rewritten: bool


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_exact_grayscale(image: Image.Image) -> bool:
    if image.mode not in {"RGB", "RGBA"}:
        return False
    red, green, blue = image.split()[:3]
    return (
        ImageChops.difference(red, green).getbbox() is None
        and ImageChops.difference(red, blue).getbbox() is None
    )


def normalize_png_image(image: Image.Image) -> tuple[Image.Image, bool]:
    image.load()
    if image.mode == "RGB" and is_exact_grayscale(image):
        return image.getchannel("R"), True
    if image.mode == "RGBA" and is_exact_grayscale(image):
        return Image.merge("LA", (image.getchannel("R"), image.getchannel("A"))), True
    if image.mode in {"1", "L", "LA", "P", "PA", "RGB", "RGBA"}:
        return image.copy(), False
    if "A" in image.getbands():
        return image.convert("RGBA"), False
    return image.convert("RGB"), False


def save_optimized_png(image: Image.Image, output_path: Path) -> tuple[str, str, bool]:
    prepared_image, grayscale_converted = normalize_png_image(image)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prepared_image.save(output_path, format="PNG", optimize=True, compress_level=9)
    return image.mode, prepared_image.mode, grayscale_converted


def optimize_png_file(path: Path) -> PngOptimizationResult:
    original_bytes = path.stat().st_size
    with Image.open(path) as image:
        mode_before = image.mode
        prepared_image, grayscale_converted = normalize_png_image(image)
        mode_after = prepared_image.mode

    temp_path: Path | None = None
    try:
        with NamedTemporaryFile(delete=False, dir=path.parent, prefix=path.stem + ".", suffix=".png") as handle:
            temp_path = Path(handle.name)
        prepared_image.save(temp_path, format="PNG", optimize=True, compress_level=9)
        optimized_bytes = temp_path.stat().st_size
        rewritten = optimized_bytes <= original_bytes
        if rewritten:
            temp_path.replace(path)
        else:
            temp_path.unlink()
            optimized_bytes = original_bytes
        return PngOptimizationResult(
            original_bytes=original_bytes,
            optimized_bytes=optimized_bytes,
            bytes_saved=max(0, original_bytes - optimized_bytes),
            grayscale_converted=grayscale_converted,
            mode_before=mode_before,
            mode_after=mode_after,
            rewritten=rewritten,
        )
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
