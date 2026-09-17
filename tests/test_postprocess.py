from pathlib import Path

import pytest
from PIL import Image

from cleanbg.exceptions import UnsupportedInputError
from cleanbg.postprocess import apply_background, crop_to_subject, parse_color


def test_parse_short_hex() -> None:
    assert parse_color("#f00") == (255, 0, 0, 255)


def test_parse_named_color() -> None:
    assert parse_color("white") == (255, 255, 255, 255)


def test_parse_rgb_tuple() -> None:
    assert parse_color((10, 20, 30)) == (10, 20, 30, 255)


def test_parse_invalid_color() -> None:
    with pytest.raises(UnsupportedInputError):
        parse_color("not-a-color")


def test_crop_to_subject() -> None:
    image = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    for x in range(10, 18):
        for y in range(12, 20):
            image.putpixel((x, y), (255, 0, 0, 255))
    assert crop_to_subject(image, padding=2).size == (12, 12)


def test_apply_solid_background() -> None:
    foreground = Image.new("RGBA", (2, 2), (255, 0, 0, 255))
    foreground.putpixel((0, 0), (0, 0, 0, 0))
    result = apply_background(foreground, "#00FF00")
    assert result.getpixel((0, 0)) == (0, 255, 0, 255)
    assert result.getpixel((1, 1))[:3] == (255, 0, 0)


def test_apply_image_background(tmp_path: Path) -> None:
    fg = Image.new("RGBA", (2, 2), (0, 0, 255, 255))
    fg.putpixel((0, 0), (0, 0, 0, 0))
    bg_path = tmp_path / "bg.png"
    Image.new("RGB", (8, 8), (255, 255, 0)).save(bg_path)
    result = apply_background(fg, str(bg_path))
    assert result.getpixel((0, 0))[:3] == (255, 255, 0)
