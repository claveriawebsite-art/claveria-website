import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from manifest import all_images

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "raw")
OUT = os.path.join(ROOT, "assets", "img")

IMG_MAGIC = (b"\x89PNG", b"\xff\xd8\xff", b"GIF8", b"RIFF")


def is_image(p):
    try:
        with open(p, "rb") as f:
            head = f.read(8)
        return any(head.startswith(m) for m in IMG_MAGIC)
    except OSError:
        return False


def save_jpg(im, dest, max_side=1600, q=85):
    im = im.convert("RGB")
    if max(im.size) > max_side:
        im.thumbnail((max_side, max_side), Image.LANCZOS)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    im.save(dest, "JPEG", quality=q, optimize=True, progressive=True)
    return os.path.getsize(dest)


def make_logo_transparent(src, dest, size=1024):
    im = Image.open(src).convert("RGBA")
    # flood fill from all corners with the bg color tolerance
    bg = im.getpixel((2, 2))
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.floodfill(im, (0, 0), (0, 0, 0, 0), thresh=28, new_image=None) if False else None
    # use point-based approach: mark pixels close to bg as transparent
    px = im.load()
    mpx = mask.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if abs(r - bg[0]) < 30 and abs(g - bg[1]) < 30 and abs(b - bg[2]) < 30:
                mpx[x, y] = 0
            else:
                mpx[x, y] = 255
    im.putalpha(mask)
    im = im.resize((size, size), Image.LANCZOS)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    im.save(dest, "PNG", optimize=True)
    return os.path.getsize(dest)


def main():
    total_in = total_out = 0
    skipped = []
    for fid, dest in all_images():
        src = os.path.join(RAW, dest)
        if not is_image(src):
            skipped.append(dest)
            continue
        out = os.path.join(OUT, dest)
        im = Image.open(src)
        if dest.startswith("brand/logo"):
            make_logo_transparent(src, out, 1024)
            # favicon
            fav = Image.open(out).resize((64, 64), Image.LANCZOS)
            fav.save(os.path.join(OUT, "brand", "favicon.png"), "PNG", optimize=True)
            # og image (dark bg tile)
            tile = Image.new("RGB", (1200, 630), (2, 64, 35))
            lg = Image.open(out)
            lg.thumbnail((520, 520), Image.LANCZOS)
            tile.paste(lg, ((1200 - lg.width) // 2, (630 - lg.height) // 2), lg)
            tile.save(os.path.join(OUT, "brand", "og.jpg"), "JPEG", quality=88)
        elif dest.startswith("brand/hero"):
            save_jpg(im, out, max_side=1920, q=82)
        else:
            save_jpg(im, out, max_side=1600, q=85)
        total_in += os.path.getsize(src)
        total_out += os.path.getsize(out)
        print("ok", dest, os.path.getsize(out))
    print(f"\n{len(skipped)} skipped (inaccessible): {skipped}")
    print(f"raw {total_in/1e6:.1f} MB -> out {total_out/1e6:.1f} MB")


if __name__ == "__main__":
    main()
