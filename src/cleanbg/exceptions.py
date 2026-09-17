class CleanBgError(Exception):
    """Base error for the package."""


class UnsupportedInputError(CleanBgError):
    """Path or input type cannot be processed."""


class UnknownModelError(CleanBgError):
    """Requested model name is not in the catalog."""


class OutputError(CleanBgError):
    """Output path is missing or invalid."""
