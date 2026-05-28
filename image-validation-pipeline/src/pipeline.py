"""Automated Image Data Validation & Pre-processing Pipeline.

Core module: ingest a directory of images, run quality checks, and
standardize the survivors so they are ready for CNN training.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np


BLUR_THRESHOLD = 100.0
EXPOSURE_LOW = 40.0
EXPOSURE_HIGH = 215.0
DEFAULT_SIZE = (224, 224)


@dataclass
class QualityResult:
    status: str
    blur_score: Optional[float] = None
    brightness: Optional[float] = None


def calculate_variance(image: np.ndarray) -> float:
    """Variance of the Laplacian — a standard blur metric.

    Low variance means few sharp edges, i.e. the image is blurry.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def calculate_brightness(image: np.ndarray) -> float:
    """Mean V channel in HSV space — a simple exposure proxy."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return float(hsv[:, :, 2].mean())


def check_image_quality(image_path: str) -> QualityResult:
    """Gatekeeper function exercised by the white-box path tests.

    Independent paths:
      Path 1: load fails -> "Corrupted"
      Path 2: load ok, blur below threshold -> "Blurry"
      Path 3: load ok, blur ok, exposure out of range -> "Poorly Exposed"
      Path 4: load ok, blur ok, exposure ok -> "Ready for Training"
    """
    # Node 1
    image = cv2.imread(image_path)
    if image is None:
        return QualityResult(status="Corrupted")  # Node 2

    # Node 3
    blur_score = calculate_variance(image)
    if blur_score < BLUR_THRESHOLD:
        return QualityResult(status="Blurry", blur_score=blur_score)  # Node 4

    # Node 5
    brightness = calculate_brightness(image)
    if brightness < EXPOSURE_LOW or brightness > EXPOSURE_HIGH:
        return QualityResult(  # Node 6
            status="Poorly Exposed",
            blur_score=blur_score,
            brightness=brightness,
        )

    # Node 7
    return QualityResult(
        status="Ready for Training",
        blur_score=blur_score,
        brightness=brightness,
    )


def standardize(image: np.ndarray, size: Tuple[int, int] = DEFAULT_SIZE) -> np.ndarray:
    """Resize, normalize in HSV space, and stack a Canny edge channel.

    Returns a 4-channel uint8 array: B, G, R, edges.
    """
    resized = cv2.resize(image, size, interpolation=cv2.INTER_AREA)

    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    v = hsv[:, :, 2]
    v_norm = cv2.normalize(v, None, 0, 255, cv2.NORM_MINMAX)
    hsv[:, :, 2] = v_norm
    color_norm = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    gray = cv2.cvtColor(color_norm, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    return np.dstack([color_norm, edges])


def process_directory(
    input_dir: str,
    output_dir: str,
    quarantine_dir: str,
) -> dict:
    """Walk input_dir, gate each image, and write standardized survivors.

    Returns a summary dict of counts per status.
    """
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(quarantine_dir, exist_ok=True)

    summary = {
        "Ready for Training": 0,
        "Blurry": 0,
        "Poorly Exposed": 0,
        "Corrupted": 0,
    }

    for name in sorted(os.listdir(input_dir)):
        path = os.path.join(input_dir, name)
        if not os.path.isfile(path):
            continue

        result = check_image_quality(path)
        summary[result.status] = summary.get(result.status, 0) + 1

        if result.status == "Ready for Training":
            image = cv2.imread(path)
            processed = standardize(image)
            stem, _ = os.path.splitext(name)
            cv2.imwrite(os.path.join(output_dir, f"{stem}.png"), processed[:, :, :3])
            cv2.imwrite(os.path.join(output_dir, f"{stem}_edges.png"), processed[:, :, 3])
        else:
            try:
                with open(path, "rb") as src:
                    data = src.read()
                with open(os.path.join(quarantine_dir, name), "wb") as dst:
                    dst.write(data)
            except OSError:
                pass

    return summary
