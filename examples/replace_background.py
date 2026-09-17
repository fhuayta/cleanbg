import sys
from pathlib import Path

from cleanbg import remove_background

if len(sys.argv) < 2:
    raise SystemExit(
        "usage: python examples/replace_background.py photo.jpg [#FFFFFF|bg.jpg] [out.png]"
    )

src = Path(sys.argv[1])
background = sys.argv[2] if len(sys.argv) > 2 else "#FFFFFF"
dst = Path(sys.argv[3]) if len(sys.argv) > 3 else src.with_name(f"{src.stem}_on_bg.png")

remove_background(src, dst, background=background, crop=True)
print(dst)
