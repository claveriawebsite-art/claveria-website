import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from manifest import all_images

RAW = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "raw"))

IMG_MAGIC = (b"\x89PNG", b"\xff\xd8\xff", b"GIF8", b"RIFF")


def is_image(p):
    if not os.path.exists(p) or os.path.getsize(p) < 1000:
        return False
    with open(p, "rb") as f:
        return f.read(4)[:3] in IMG_MAGIC or f.read(4)[:4] in IMG_MAGIC


def try_urls(fid, out):
    urls = [
        f"https://drive.usercontent.google.com/download?id={fid}&export=download",
        f"https://www.googleapis.com/drive/v3/files/{fid}?alt=media",
        f"https://drive.google.com/uc?export=download&confirm=t&id={fid}",
    ]
    for url in urls:
        r = subprocess.run(
            ["curl", "-sL", "--max-time", "180", "-o", out, url, "-w", "%{http_code}"],
            capture_output=True, text=True,
        )
        if is_image(out):
            return url
        time.sleep(1)
    return None


def main():
    bad = []
    for fid, dest in all_images():
        p = os.path.join(RAW, dest)
        if not is_image(p):
            bad.append((fid, dest, p))
    print(len(bad), "invalid files")
    for fid, dest, p in bad:
        got = try_urls(fid, p)
        size = os.path.getsize(p) if os.path.exists(p) else 0
        print(("FIXED" if got else "STILL BAD"), size, dest, got or "", flush=True)
        time.sleep(1)


if __name__ == "__main__":
    main()
