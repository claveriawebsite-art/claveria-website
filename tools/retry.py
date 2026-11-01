import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from manifest import all_images

RAW = os.path.join(os.path.dirname(__file__), "..", "raw")

FAILED = [
    "staycation/hiraya-farm-escape/5.jpg",
    "staycation/payag-ni-kuya/1.jpg",
    "staycation/payag-ni-kuya/5.jpg",
    "staycation/p-brother-mountain/5.jpg",
    "staycation/cabinscape-ridge-resort/2.jpg",
    "staycation/aikeeko-farmview-resort/1.jpg",
    "staycation/aikeeko-farmview-resort/5.jpg",
    "falls/nasaad-falls/3.jpg",
    "cafes/jacos-stopover/4.jpg",
    "cafes/kasadya-cafe/5.jpg",
    "cafes/the-sibs-coffee/5.jpg",
    "cafes/sanctum-by-cnc/4.jpg",
    "cafes/julios-cafe-restaurant/2.jpg",
    "cafes/lone-wolf-cafe/5.jpg",
    "cafes/skye-88-cafe/5.jpg",
]

by_dest = {dest: fid for fid, dest in all_images()}

for dest in FAILED:
    fid = by_dest[dest]
    out = os.path.abspath(os.path.join(RAW, dest))
    url = f"https://drive.google.com/uc?export=download&id={fid}"
    for attempt in range(6):
        r = subprocess.run(
            ["curl", "-sL", "--max-time", "180", "-o", out, url, "-w", "%{http_code}"],
            capture_output=True, text=True,
        )
        size = os.path.getsize(out) if os.path.exists(out) else 0
        if r.stdout.strip() == "200" and size > 1000:
            # check it's not an HTML confirm page
            with open(out, "rb") as f:
                head = f.read(16)
            if head[:4] in (b"\x89PNG", b"\xff\xd8\xff\xe0", b"\xff\xd8\xff\xe1", b"\xff\xd8\xff\xdb") or head[:4] == b"\xff\xd8\xff\xe3":
                print("ok", size, dest, flush=True)
                break
            else:
                print("not-image", head[:8], dest, flush=True)
        else:
            print("retry", r.stdout.strip(), size, dest, flush=True)
        time.sleep(5)
    else:
        print("STILL FAILING", dest, flush=True)
    time.sleep(2)
print("done")
