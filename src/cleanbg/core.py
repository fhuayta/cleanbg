from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from PIL import Image

from cleanbg.exceptions import UnknownModelError
from cleanbg.io import ImageSource, default_output_path, list_images, load_image, save_image
from cleanbg.models import DEFAULT_MODEL, validate_model
from cleanbg.postprocess import BackgroundSpec, apply_background, crop_to_subject

ProgressCallback = Callable[[int, int, Path], None]


def _import_rembg() -> tuple[Any, Any]:
    try:
        from rembg import new_session, remove
    except ImportError as exc:
        raise ImportError("rembg is required: pip install cleanbg") from exc
    return new_session, remove


def _as_image(result: Any) -> Image.Image:
    if isinstance(result, Image.Image):
        return result
    if hasattr(result, "read"):
        return Image.open(result)
    return load_image(result)


@dataclass
class RemovalResult:
    image: Image.Image
    source: Path | None = None
    output: Path | None = None


class BackgroundRemover:
    """Holds one ONNX session so a folder of photos does not reload the model."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        *,
        alpha_matting: bool = False,
        alpha_matting_foreground_threshold: int = 240,
        alpha_matting_background_threshold: int = 10,
        alpha_matting_erode_size: int = 10,
        post_process_mask: bool = False,
        decontaminate: bool = False,
        session_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.model = validate_model(model)
        self.alpha_matting = alpha_matting
        self.alpha_matting_foreground_threshold = alpha_matting_foreground_threshold
        self.alpha_matting_background_threshold = alpha_matting_background_threshold
        self.alpha_matting_erode_size = alpha_matting_erode_size
        self.post_process_mask = post_process_mask
        self.decontaminate = decontaminate
        self.session_kwargs = session_kwargs or {}
        self._session: Any | None = None

    @property
    def session(self) -> Any:
        if self._session is None:
            new_session, _ = _import_rembg()
            try:
                self._session = new_session(self.model, **self.session_kwargs)
            except ValueError as exc:
                raise UnknownModelError(str(exc)) from exc
        return self._session

    def remove(
        self,
        source: ImageSource,
        output: str | Path | None = None,
        *,
        background: BackgroundSpec = None,
        crop: bool = False,
        crop_padding: int = 8,
        only_mask: bool = False,
        suffix: str = "_nobg",
    ) -> Image.Image:
        source_path = Path(source) if isinstance(source, (str, Path)) else None
        image = load_image(source)
        _, remove_fn = _import_rembg()

        kwargs = self._inference_kwargs(only_mask=only_mask)
        try:
            result = _as_image(remove_fn(image, **kwargs))
        except TypeError:
            kwargs.pop("decontaminate", None)
            result = _as_image(remove_fn(image, **kwargs))

        if not only_mask:
            if crop:
                result = crop_to_subject(result, padding=crop_padding)
            result = apply_background(result, background)

        if output is not None:
            destination = (
                default_output_path(source_path, output, suffix=suffix)
                if source_path is not None
                else Path(output)
            )
            save_image(result, destination)
        return result

    def remove_many(
        self,
        source: str | Path,
        output: str | Path | None = None,
        *,
        recursive: bool = False,
        background: BackgroundSpec = None,
        crop: bool = False,
        crop_padding: int = 8,
        only_mask: bool = False,
        suffix: str = "_nobg",
        progress: ProgressCallback | None = None,
    ) -> list[RemovalResult]:
        paths = list_images(source, recursive=recursive)
        is_batch = len(paths) > 1 or Path(source).is_dir()
        results: list[RemovalResult] = []

        for index, path in enumerate(paths, start=1):
            destination = default_output_path(
                path, output, suffix=suffix, is_batch=is_batch
            )
            image = self.remove(
                path,
                destination,
                background=background,
                crop=crop,
                crop_padding=crop_padding,
                only_mask=only_mask,
                suffix=suffix,
            )
            if progress is not None:
                progress(index, len(paths), path)
            results.append(RemovalResult(image=image, source=path, output=destination))
        return results

    def _inference_kwargs(self, *, only_mask: bool) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "session": self.session,
            "only_mask": only_mask,
            "post_process_mask": self.post_process_mask,
            "alpha_matting": self.alpha_matting,
            "alpha_matting_foreground_threshold": self.alpha_matting_foreground_threshold,
            "alpha_matting_background_threshold": self.alpha_matting_background_threshold,
            "alpha_matting_erode_size": self.alpha_matting_erode_size,
        }
        if self.decontaminate:
            kwargs["decontaminate"] = True
        return kwargs


def remove_background(
    source: ImageSource,
    output: str | Path | None = None,
    *,
    model: str = DEFAULT_MODEL,
    background: BackgroundSpec = None,
    crop: bool = False,
    crop_padding: int = 8,
    only_mask: bool = False,
    alpha_matting: bool = False,
    post_process_mask: bool = False,
    decontaminate: bool = False,
    suffix: str = "_nobg",
    session_kwargs: dict[str, Any] | None = None,
) -> Image.Image:
    """Cut the background from one image. Loads the model on every call."""
    remover = BackgroundRemover(
        model,
        alpha_matting=alpha_matting,
        post_process_mask=post_process_mask,
        decontaminate=decontaminate,
        session_kwargs=session_kwargs,
    )
    return remover.remove(
        source,
        output,
        background=background,
        crop=crop,
        crop_padding=crop_padding,
        only_mask=only_mask,
        suffix=suffix,
    )


def remove_backgrounds(
    source: str | Path,
    output: str | Path | None = None,
    *,
    model: str = DEFAULT_MODEL,
    recursive: bool = False,
    background: BackgroundSpec = None,
    crop: bool = False,
    crop_padding: int = 8,
    only_mask: bool = False,
    alpha_matting: bool = False,
    post_process_mask: bool = False,
    decontaminate: bool = False,
    suffix: str = "_nobg",
    progress: ProgressCallback | None = None,
    session_kwargs: dict[str, Any] | None = None,
) -> list[RemovalResult]:
    """Cut backgrounds from a file or a directory, reusing one session."""
    remover = BackgroundRemover(
        model,
        alpha_matting=alpha_matting,
        post_process_mask=post_process_mask,
        decontaminate=decontaminate,
        session_kwargs=session_kwargs,
    )
    return remover.remove_many(
        source,
        output,
        recursive=recursive,
        background=background,
        crop=crop,
        crop_padding=crop_padding,
        only_mask=only_mask,
        suffix=suffix,
        progress=progress,
    )
