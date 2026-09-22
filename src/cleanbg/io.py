from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from PIL import Image, ImageOps

from cleanbg.exceptions import OutputError, UnsupportedInputError

ImageSource = str | Path | Image.Image | bytes | BinaryIO

IMAGE_EXTENSIONS = {
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}


def _finalize(image: Image.Image) -> Image.Image:
    image.load()
    # Phone photos store rotation in EXIF; without this the cutout comes out sideways.
    oriented = ImageOps.exif_transpose(image)
    return (oriented or image).copy()


def load_image(source: ImageSource) -> Image.Image:
    if isinstance(source, Image.Image):
        return source.copy()

    if isinstance(source, (bytes, bytearray)):
        with Image.open(BytesIO(source)) as image:
            return _finalize(image)

    if hasattr(source, "read"):
        opened = Image.open(source)
        return _finalize(opened)

    path = Path(source)
    if not path.is_file():
        raise UnsupportedInputError(f"file not found: {path}")
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise UnsupportedInputError(
            f"unsupported format {path.suffix or path.name!r}; "
            f"expected {', '.join(sorted(IMAGE_EXTENSIONS))}"
        )
    with Image.open(path) as image:
        return _finalize(image)


def list_images(source: str | Path, *, recursive: bool = False) -> list[Path]:
    path = Path(source)
    if path.is_file():
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            raise UnsupportedInputError(f"not a supported image: {path}")
        return [path]
    if not path.is_dir():
        raise UnsupportedInputError(f"path not found: {path}")

    iterator = path.rglob("*") if recursive else path.glob("*")
    images = sorted(
        p for p in iterator if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )
    if not images:
        raise UnsupportedInputError(f"no images in {path}")
    return images


def default_output_path(
    source: Path,
    output: str | Path | None,
    *,
    suffix: str = "_nobg",
    is_batch: bool = False,
) -> Path:
    filename = f"{source.stem}{suffix}.png"
    if output is None:
        return source.with_name(filename)

    output_path = Path(output)
    if is_batch or output_path.suffix == "":
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path / filename

    if output_path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise OutputError(f"unsupported output extension: {output_path.suffix}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def save_image(image: Image.Image, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    suffix = destination.suffix.lower()

    if suffix in {".jpg", ".jpeg"} and image.mode == "RGBA":
        flattened = Image.new("RGB", image.size, (255, 255, 255))
        flattened.paste(image, mask=image.split()[-1])
        flattened.save(destination, quality=95, optimize=True)
        return destination

    to_save = image
    if suffix == ".png" and image.mode not in {"RGBA", "RGB", "L", "LA", "P"}:
        to_save = image.convert("RGBA")
    to_save.save(destination)
    return destination
