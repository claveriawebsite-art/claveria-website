import os
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src = os.path.join(ROOT, "raw", "brand", "logo.png")
out_dir = os.path.join(ROOT, "assets", "img", "brand")
os.makedirs(out_dir, exist_ok=True)

im = Image.open(src).convert("RGB")
# favicon: dark green tile with the full logo
for size in (64, 180, 512):
    tile = Image.new("RGB", (size, size), (2, 64, 35))
    lg = im.resize((int(size * 0.82), int(size * 0.82)), Image.LANCZOS)
    tile.paste(lg, ((size - lg.width) // 2, (size - lg.height) // 2))
    name = "favicon.png" if size == 64 else f"icon-{size}.png"
    tile.save(os.path.join(out_dir, name), "PNG", optimize=True)
    print("wrote", name)

# apple touch icon
tile = Image.new("RGB", (180, 180), (2, 64, 35))
lg = im.resize((148, 148), Image.LANCZOS)
tile.paste(lg, (16, 16))
tile.save(os.path.join(out_dir, "apple-touch-icon.png"), "PNG", optimize=True)
print("wrote apple-touch-icon.png")
