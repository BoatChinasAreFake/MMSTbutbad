"""
One-time utility: recompute province center points that fall outside their own
area. The original centers are plain pixel-average centroids, which land outside
the province for non-convex, C-shaped, or wrapping shapes (~3.5% of provinces).

For each affected province we compute the "pole of inaccessibility": the interior
pixel farthest from the province boundary (via a distance transform on the
province's bounding-box mask). That point is guaranteed to be inside the province
and is visually well-centered, which improves label anchoring and the selection
highlight dots.

Only centers that are currently outside their province are rewritten, keeping the
change to provinces_meta.json minimal and reviewable. "count" and "index" are
preserved; only "x"/"y" change.
"""
import json
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

META_PATH = "provinces_meta.json"
INDEX_PATH = "provinces_index.png"


def decode_ids(index_img):
    arr = np.asarray(index_img, dtype=np.uint32)
    ids = arr[:, :, 0] + arr[:, :, 1] * 256 + arr[:, :, 2] * 65536
    white = (arr[:, :, 0] == 255) & (arr[:, :, 1] == 255) & (arr[:, :, 2] == 255)
    ids[white] = 0
    return ids


def main():
    meta = json.load(open(META_PATH, "r", encoding="utf-8"))
    centers = meta["centers"]

    idx_img = Image.open(INDEX_PATH).convert("RGB")
    w, h = idx_img.size
    ids = decode_ids(idx_img)

    # Which provinces have a centroid that lands outside their own pixels?
    outside_ids = []
    for pid_str, c in centers.items():
        pid = int(pid_str)
        if pid == 0:
            continue
        x = int(round(c["x"]))
        y = int(round(c["y"]))
        inside = (0 <= x < w and 0 <= y < h and int(ids[y, x]) == pid)
        if not inside:
            outside_ids.append(pid)

    print(f"Provinces with centroid outside their area: {len(outside_ids)}")

    # Build a bounding box per affected province in a single pass over the image.
    targets = set(outside_ids)
    # min_x, min_y, max_x, max_y
    bbox = {pid: [w, h, -1, -1] for pid in targets}
    ys, xs = np.nonzero(np.isin(ids, list(targets)))
    for x, y in zip(xs.tolist(), ys.tolist()):
        pid = int(ids[y, x])
        b = bbox[pid]
        if x < b[0]:
            b[0] = x
        if y < b[1]:
            b[1] = y
        if x > b[2]:
            b[2] = x
        if y > b[3]:
            b[3] = y

    updated = 0
    skipped = 0
    for pid in outside_ids:
        b = bbox[pid]
        if b[2] < 0:
            # Province id not present in the index image (shouldn't happen); leave as-is.
            skipped += 1
            continue
        x0, y0, x1, y1 = b
        sub = ids[y0:y1 + 1, x0:x1 + 1]
        mask = (sub == pid)
        if not mask.any():
            skipped += 1
            continue
        # Pole of inaccessibility: interior point farthest from the boundary.
        dt = distance_transform_edt(mask)
        my, mx = np.unravel_index(int(np.argmax(dt)), dt.shape)
        new_x = float(x0 + mx)
        new_y = float(y0 + my)
        centers[str(pid)]["x"] = round(new_x, 1)
        centers[str(pid)]["y"] = round(new_y, 1)
        updated += 1

    print(f"Recomputed centers: {updated} (skipped {skipped})")

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("Saved", META_PATH)


if __name__ == "__main__":
    sys.exit(main())
