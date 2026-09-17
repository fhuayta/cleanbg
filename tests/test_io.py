from pathlib import Path

import pytest
from PIL import Image

from cleanbg.exceptions import OutputError, UnsupportedInputError
from cleanbg.io import default_output_path, list_images, load_image, save_image


def test_load_image_from_path(tmp_path: Path) -> None:
    path = tmp_path / "photo.png"
    Image.new("RGB", (8, 8), "red").save(path)
    assert load_image(path).size == (8, 8)


def test_load_image_missing_file(tmp_path: Path) -> None:
    with pytest.raises(UnsupportedInputError):
        load_image(tmp_path / "missing.png")


def test_list_images_skips_non_images(tmp_path: Path) -> None:
    Image.new("RGB", (4, 4), "blue").save(tmp_path / "a.jpg")
    Image.new("RGB", (4, 4), "green").save(tmp_path / "b.png")
    (tmp_path / "notes.txt").write_text("skip", encoding="utf-8")
    assert [p.name for p in list_images(tmp_path)] == ["a.jpg", "b.png"]


def test_default_output_path_next_to_source(tmp_path: Path) -> None:
    source = tmp_path / "portrait.jpg"
    assert default_output_path(source, None) == tmp_path / "portrait_nobg.png"


def test_default_output_path_into_directory(tmp_path: Path) -> None:
    source = tmp_path / "portrait.jpg"
    out_dir = tmp_path / "out"
    result = default_output_path(source, out_dir)
    assert result == out_dir / "portrait_nobg.png"
    assert out_dir.is_dir()


def test_default_output_path_rejects_unknown_extension(tmp_path: Path) -> None:
    with pytest.raises(OutputError):
        default_output_path(tmp_path / "a.jpg", tmp_path / "a.pdf")


def test_save_jpeg_drops_alpha(tmp_path: Path) -> None:
    image = Image.new("RGBA", (4, 4), (255, 0, 0, 128))
    dest = tmp_path / "flat.jpg"
    save_image(image, dest)
    assert Image.open(dest).mode == "RGB"
