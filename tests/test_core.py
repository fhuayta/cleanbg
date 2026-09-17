from pathlib import Path

import pytest
from PIL import Image

from cleanbg.core import BackgroundRemover, remove_background
from cleanbg.exceptions import UnknownModelError
from cleanbg.models import DEFAULT_MODEL, list_models, validate_model


def _clear_left(image: Image.Image, **kwargs: object) -> Image.Image:
    result = image.convert("RGBA")
    pixels = result.load()
    assert pixels is not None
    for x in range(result.width // 2):
        for y in range(result.height):
            r, g, b, _a = pixels[x, y]
            pixels[x, y] = (r, g, b, 0)
    return result


def test_catalog_includes_default() -> None:
    names = {info.name for info in list_models()}
    assert DEFAULT_MODEL in names
    assert "u2net_human_seg" in names


def test_validate_model_accepts_known() -> None:
    assert validate_model("isnet-general-use") == "isnet-general-use"


def test_validate_model_rejects_unknown() -> None:
    with pytest.raises(UnknownModelError):
        validate_model("not-a-model")


def test_remove_background_writes_png(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "in.png"
    Image.new("RGB", (10, 10), "purple").save(source)

    monkeypatch.setattr(
        "cleanbg.core._import_rembg",
        lambda: (lambda *_a, **_k: object(), _clear_left),
    )

    dest = tmp_path / "out.png"
    result = remove_background(source, dest, crop=True, background="#FFFFFF")
    assert dest.is_file()
    assert result.mode == "RGBA"
    assert Image.open(dest).size[0] <= 10


def test_remove_many_reuses_session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("a.png", "b.png"):
        Image.new("RGB", (6, 6), "navy").save(tmp_path / name)

    sessions: list[object] = []

    def fake_session(*_args: object, **_kwargs: object) -> object:
        token = object()
        sessions.append(token)
        return token

    monkeypatch.setattr(
        "cleanbg.core._import_rembg",
        lambda: (fake_session, _clear_left),
    )

    results = BackgroundRemover("u2net").remove_many(tmp_path, tmp_path / "out")
    assert len(results) == 2
    assert len(sessions) == 1
    assert all(item.output and item.output.is_file() for item in results)
