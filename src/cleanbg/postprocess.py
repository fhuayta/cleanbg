from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageColor

from cleanbg.exceptions import UnsupportedInputError

BackgroundSpec = str | tuple[int, ...] | Image.Image | None


def parse_color(value: str | tuple[int, ...]) -> tuple[int, int, int, int]:
    if isinstance(value, tuple):
        if len(value) == 3:
            return (*value, 255)
        if len(value) == 4:
            return (value[0], value[1], value[2], value[3])
        raise UnsupportedInputError("color tuple must be RGB or RGBA")

    text = value.strip()
    if text.startswith("#") and len(text) == 4:
        text = "#" + "".join(ch * 2 for ch in text[1:])
    try:
        r, g, b, *rest = ImageColor.getrgb(text)
    except ValueError as exc:
        raise UnsupportedInputError(f"invalid color: {value!r}") from exc
    alpha = rest[0] if rest else 255
    return r, g, b, alpha


def crop_to_subject(image: Image.Image, padding: int = 8) -> Image.Image:
    rgba = image.convert("RGBA")
    bbox = rgba.split()[-1].getbbox()
    if bbox is None:
        return rgba

    left, top, right, bottom = bbox
    return rgba.crop(
        (
            max(0, left - padding),
            max(0, top - padding),
            min(rgba.width, right + padding),
            min(rgba.height, bottom + padding),
        )
    )


def apply_background(image: Image.Image, background: BackgroundSpec) -> Image.Image:
    foreground = image.convert("RGBA")
    if background is None:
        return foreground

    size = foreground.size
    if isinstance(background, Image.Image):
        return Image.alpha_composite(_fit(background, size), foreground)

    if isinstance(background, str) and Path(background).is_file():
        with Image.open(background) as bg_image:
            layer = _fit(bg_image, size)
        return Image.alpha_composite(layer, foreground)

    layer = Image.new("RGBA", size, parse_color(background))
    return Image.alpha_composite(layer, foreground)


def _fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return image.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
