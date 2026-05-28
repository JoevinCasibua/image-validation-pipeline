"""Pytest fixtures: synthetic images for white-box path testing."""

from __future__ import annotations

import cv2
import numpy as np
import pytest


def _sharp_image(size: int = 256) -> np.ndarray:
    img = np.full((size, size, 3), 128, dtype=np.uint8)
    rng = np.random.default_rng(42)
    noise = rng.integers(0, 256, size=(size, size, 3), dtype=np.uint8)
    img = noise
    cv2.rectangle(img, (20, 20), (200, 200), (255, 255, 255), 3)
    cv2.line(img, (0, 0), (size - 1, size - 1), (0, 0, 0), 2)
    return img


def _blurry_image(size: int = 256) -> np.ndarray:
    img = _sharp_image(size)
    return cv2.GaussianBlur(img, (51, 51), 30)


def _dark_image(size: int = 256) -> np.ndarray:
    img = _sharp_image(size)
    return (img.astype(np.float32) * 0.05).astype(np.uint8)


@pytest.fixture
def sharp_image_path(tmp_path):
    path = tmp_path / "sharp.png"
    cv2.imwrite(str(path), _sharp_image())
    return str(path)


@pytest.fixture
def blurry_image_path(tmp_path):
    path = tmp_path / "blurry.png"
    cv2.imwrite(str(path), _blurry_image())
    return str(path)


@pytest.fixture
def dark_image_path(tmp_path):
    path = tmp_path / "dark.png"
    cv2.imwrite(str(path), _dark_image())
    return str(path)


@pytest.fixture
def corrupted_image_path(tmp_path):
    path = tmp_path / "broken.jpg"
    path.write_bytes(b"this is not an image, it is a text file in disguise")
    return str(path)


@pytest.fixture
def messy_input_dir(tmp_path, sharp_image_path, blurry_image_path, dark_image_path, corrupted_image_path):
    """A directory mixing all four categories — used by the integration test."""
    input_dir = tmp_path / "raw"
    input_dir.mkdir()

    import shutil

    shutil.copy(sharp_image_path, input_dir / "good.png")
    shutil.copy(blurry_image_path, input_dir / "blurry.png")
    shutil.copy(dark_image_path, input_dir / "dark.png")
    shutil.copy(corrupted_image_path, input_dir / "broken.jpg")

    return str(input_dir)
