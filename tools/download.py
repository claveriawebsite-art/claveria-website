import concurrent.futures as cf
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from manifest import all_images

RAW = os.path.join(os.path.dirname(__file__), "..", "raw")


def fetch(item):
    fid, dest = item
    out = os.path.abspath(os.path.join(RAW, dest))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return ("skip", dest, os.path.getsize(out))
    url = f"https://drive.google.com/uc?export=download&id={fid}"
    r = subprocess.run(
        ["curl", "-sL", "--fail", "--max-time", "120", "-o", out, url, "-w", "%{http_code}"],
        capture_output=True, text=True,
    )
    size = os.path.getsize(out) if os.path.exists(out) else 0
    ok = r.stdout.strip() == "200" and size > 1000
    # verify it's an image via PIL later; here just record
    return ("ok" if ok else "FAIL", dest, size)


def main():
    imgs = all_images()
    results = []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for res in ex.map(fetch, imgs):
            results.append(res)
            if res[0] != "skip":
                print(res[0], res[2], res[1], flush=True)
    fails = [r for r in results if r[0] == "FAIL"]
    print(f"\nDone: {len(results)} total, {len(fails)} failed")
    for f in fails:
        print("FAILED:", f)


if __name__ == "__main__":
    main()
