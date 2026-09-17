# Usage

Install the package first (`pip install -e .`). The first call downloads the `u2net` weights (~176 MB).

Put a photo next to these snippets, or change the paths.

## One file

```bash
cleanbg photo.jpg
```

Writes `photo_nobg.png` next to the input (transparent background).

```python
from cleanbg import remove_background

image = remove_background("photo.jpg", "photo.png")
print(image.size, image.mode)  # e.g. (1920, 1080) RGBA
```

Skip the second argument if you only want the `PIL.Image` in memory.

## Folder

```bash
cleanbg shots/ -o out/
```

```python
from cleanbg import BackgroundRemover

remover = BackgroundRemover()
for item in remover.remove_many("shots/", "out/"):
    print(item.source, "->", item.output)
```

Reuse `BackgroundRemover` for more than one image so the model is loaded once.

## People

```bash
cleanbg portrait.jpg --model u2net_human_seg --crop -o portrait.png
```

```python
from cleanbg import remove_background

remove_background(
    "portrait.jpg",
    "portrait.png",
    model="u2net_human_seg",
    crop=True,
)
```

## Solid or image background

Transparent PNG is the default. Pass a color or another photo instead:

```bash
cleanbg product.jpg --bg "#FFFFFF" --crop -o product.png
cleanbg subject.jpg --bg studio.jpg -o composite.png
```

```python
from cleanbg import remove_background

remove_background("product.jpg", "product.png", background="#FFFFFF", crop=True)
remove_background("subject.jpg", "composite.png", background="studio.jpg")
```

JPEG output drops transparency and composites on white.

## Mask only

```bash
cleanbg photo.jpg --only-mask -o mask.png
```

```python
from cleanbg import remove_background

mask = remove_background("photo.jpg", "mask.png", only_mask=True)
```

## Softer edges

Hair and fur:

```bash
cleanbg portrait.jpg --alpha-matting --decontaminate -o portrait.png
```

```python
from cleanbg import remove_background

remove_background(
    "portrait.jpg",
    "portrait.png",
    alpha_matting=True,
    decontaminate=True,
)
```

## From a PIL image

```python
from PIL import Image
from cleanbg import remove_background

src = Image.open("photo.jpg")
cutout = remove_background(src)
cutout.save("photo.png")
```

## Scripts in this repo

```bash
python examples/remove_one.py photo.jpg
python examples/remove_folder.py shots/ out/
python examples/replace_background.py photo.jpg "#FFFFFF"
```

`cleanbg --list-models` prints every available checkpoint. See the README for which one to pick.
