from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cleanbg.core import remove_backgrounds
from cleanbg.exceptions import CleanBgError
from cleanbg.models import DEFAULT_MODEL, MODELS, format_model_table


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cleanbg",
        description="Remove the background from a photo or from every image in a folder.",
        epilog=(
            "examples:\n"
            "  cleanbg photo.jpg\n"
            "  cleanbg shots/ -o out/\n"
            "  cleanbg photo.jpg --model u2net_human_seg --crop\n"
            "  cleanbg product.jpg --bg '#FFFFFF' -o product.png"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", nargs="?", help="image file or directory")
    parser.add_argument(
        "-o",
        "--output",
        help="output file or directory (default: <name>_nobg.png)",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=DEFAULT_MODEL,
        metavar="NAME",
        help=f"segmentation model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--bg",
        "--background",
        dest="background",
        help="hex color or image path; omit for a transparent PNG",
    )
    parser.add_argument("--crop", action="store_true", help="trim to the subject")
    parser.add_argument(
        "--crop-padding",
        type=int,
        default=8,
        metavar="PX",
        help="padding around the crop in pixels (default: 8)",
    )
    parser.add_argument("--only-mask", action="store_true", help="write the mask only")
    parser.add_argument(
        "-a",
        "--alpha-matting",
        action="store_true",
        help="refine soft edges (hair, fur); slower",
    )
    parser.add_argument(
        "--decontaminate",
        action="store_true",
        help="strip color fringing left by the original background",
    )
    parser.add_argument(
        "--post-process-mask",
        action="store_true",
        help="binarize the mask (no partial alpha)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="include subdirectories when the input is a folder",
    )
    parser.add_argument(
        "--suffix",
        default="_nobg",
        help="filename suffix in batch mode (default: _nobg)",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="print available models and exit",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_models:
        print(format_model_table())
        return 0

    if not args.input:
        parser.error("an image or folder is required (or pass --list-models)")

    if args.model not in MODELS:
        parser.error(f"unknown model {args.model!r}; try --list-models")

    source = Path(args.input)
    if not source.exists():
        parser.error(f"not found: {source}")

    def progress(index: int, total: int, path: Path) -> None:
        print(f"[{index}/{total}] {path}", file=sys.stderr)

    try:
        results = remove_backgrounds(
            source,
            args.output,
            model=args.model,
            recursive=args.recursive,
            background=args.background,
            crop=args.crop,
            crop_padding=args.crop_padding,
            only_mask=args.only_mask,
            alpha_matting=args.alpha_matting,
            post_process_mask=args.post_process_mask,
            decontaminate=args.decontaminate,
            suffix=args.suffix,
            progress=progress if source.is_dir() else None,
        )
    except CleanBgError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for result in results:
        if result.output is not None:
            print(result.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
