"""Generate a small messy demo directory next to the project for manual demos."""

from __future__ import annotations

import os
import sys

import cv2
import numpy as np


def main(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    rng = np.random.default_rng(7)

    sharp = rng.integers(0, 256, size=(256, 256, 3), dtype=np.uint8)
    cv2.rectangle(sharp, (30, 30), (220, 220), (255, 255, 255), 4)
    cv2.imwrite(os.path.join(out_dir, "01_sharp.png"), sharp)

    blurry = cv2.GaussianBlur(sharp, (51, 51), 30)
    cv2.imwrite(os.path.join(out_dir, "02_blurry.png"), blurry)

    dark = (sharp.astype(np.float32) * 0.05).astype(np.uint8)
    cv2.imwrite(os.path.join(out_dir, "03_dark.png"), dark)

    with open(os.path.join(out_dir, "04_broken.jpg"), "wb") as f:
        f.write(b"not actually a jpeg")

    print(f"Wrote demo files into {out_dir}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "demo_input"
    main(target)
