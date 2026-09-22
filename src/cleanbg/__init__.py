"""Remove image backgrounds locally. Keep the subject, drop the rest."""

from cleanbg.core import BackgroundRemover, RemovalResult, remove_background, remove_backgrounds
from cleanbg.exceptions import CleanBgError, OutputError, UnknownModelError, UnsupportedInputError
from cleanbg.models import DEFAULT_MODEL, MODELS, list_models

__all__ = [
    "DEFAULT_MODEL",
    "MODELS",
    "BackgroundRemover",
    "CleanBgError",
    "OutputError",
    "RemovalResult",
    "UnknownModelError",
    "UnsupportedInputError",
    "list_models",
    "remove_background",
    "remove_backgrounds",
    "__version__",
]

__version__ = "0.1.1"
