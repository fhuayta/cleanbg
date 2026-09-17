from __future__ import annotations

from dataclasses import dataclass

from cleanbg.exceptions import UnknownModelError

DEFAULT_MODEL = "u2net"


@dataclass(frozen=True)
class ModelInfo:
    name: str
    summary: str
    size: str
    commercial: bool = True


MODELS: dict[str, ModelInfo] = {
    "u2net": ModelInfo("u2net", "general use, good default", "~176 MB"),
    "u2netp": ModelInfo("u2netp", "tiny and fast, lower quality", "~4 MB"),
    "u2net_human_seg": ModelInfo("u2net_human_seg", "people", "~176 MB"),
    "u2net_cloth_seg": ModelInfo("u2net_cloth_seg", "upper / lower / full garments", "~176 MB"),
    "silueta": ModelInfo("silueta", "u2net-like, smaller weights", "~43 MB"),
    "isnet-general-use": ModelInfo("isnet-general-use", "cleaner edges on objects", "~176 MB"),
    "isnet-anime": ModelInfo("isnet-anime", "illustration and anime", "~176 MB"),
    "birefnet-general": ModelInfo("birefnet-general", "high quality, slow, heavy", "~980 MB"),
    "birefnet-general-lite": ModelInfo("birefnet-general-lite", "lighter BiRefNet", "~370 MB"),
    "birefnet-portrait": ModelInfo("birefnet-portrait", "portraits and hair", "~980 MB"),
    "birefnet-dis": ModelInfo("birefnet-dis", "complex silhouettes", "~980 MB"),
    "birefnet-hrsod": ModelInfo("birefnet-hrsod", "small or detailed subjects", "~980 MB"),
    "birefnet-cod": ModelInfo("birefnet-cod", "low-contrast subjects", "~980 MB"),
    "birefnet-massive": ModelInfo("birefnet-massive", "hard general cases", "~980 MB"),
    "bria-rmbg": ModelInfo(
        "bria-rmbg",
        "very high quality; BRIA license, paid for commercial use",
        "~1.02 GB",
        commercial=False,
    ),
}


def list_models() -> list[ModelInfo]:
    return list(MODELS.values())


def validate_model(name: str) -> str:
    key = name.strip()
    if key not in MODELS:
        available = ", ".join(MODELS)
        raise UnknownModelError(f"unknown model {name!r}. choose one of: {available}")
    return key


def format_model_table() -> str:
    lines = [
        f"{'model':<24} {'size':<10} commercial  notes",
        "-" * 88,
    ]
    for info in MODELS.values():
        flag = "yes" if info.commercial else "check"
        marker = "  (default)" if info.name == DEFAULT_MODEL else ""
        lines.append(f"{info.name:<24} {info.size:<10} {flag:<11} {info.summary}{marker}")
    return "\n".join(lines)
