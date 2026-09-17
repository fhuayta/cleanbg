import sys
from pathlib import Path

from cleanbg import remove_background

if len(sys.argv) < 2:
    raise SystemExit("usage: python examples/remove_one.py photo.jpg [out.png]")

src = Path(sys.argv[1])
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(f"{src.stem}_nobg.png")
image = remove_background(src, dst)
print(f"{dst} ({image.width}x{image.height})")
