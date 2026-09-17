import sys
from pathlib import Path

from cleanbg import BackgroundRemover

if len(sys.argv) < 2:
    raise SystemExit("usage: python examples/remove_folder.py shots/ [out/]")

src = Path(sys.argv[1])
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.parent / f"{src.name}_nobg"

remover = BackgroundRemover("u2net_human_seg")
results = remover.remove_many(
    src,
    dst,
    crop=True,
    progress=lambda i, total, path: print(f"{i}/{total} {path.name}"),
)
print(f"{len(results)} files -> {dst}")
