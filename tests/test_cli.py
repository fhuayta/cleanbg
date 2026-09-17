from pathlib import Path

import pytest
from PIL import Image

from cleanbg.cli import main


def test_list_models(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--list-models"]) == 0
    out = capsys.readouterr().out
    assert "u2net" in out
    assert "birefnet-portrait" in out


def test_missing_input_exits() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2


def test_cli_writes_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "photo.jpg"
    Image.new("RGB", (8, 8), "orange").save(source)
    dest = tmp_path / "cutout.png"

    monkeypatch.setattr(
        "cleanbg.core._import_rembg",
        lambda: (
            lambda *_a, **_k: object(),
            lambda *_a, **_k: Image.new("RGBA", (8, 8), (255, 128, 0, 255)),
        ),
    )

    assert main([str(source), "-o", str(dest)]) == 0
    assert dest.is_file()
    assert str(dest) in capsys.readouterr().out
