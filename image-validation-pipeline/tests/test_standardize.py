"""Unit tests for the standardization step."""

import cv2

from src.pipeline import DEFAULT_SIZE, standardize


def test_standardize_resizes_to_default(sharp_image_path):
    image = cv2.imread(sharp_image_path)
    out = standardize(image)
    assert out.shape[0] == DEFAULT_SIZE[1]
    assert out.shape[1] == DEFAULT_SIZE[0]


def test_standardize_emits_edge_channel(sharp_image_path):
    image = cv2.imread(sharp_image_path)
    out = standardize(image)
    assert out.shape[2] == 4
    edges = out[:, :, 3]
    assert edges.max() > 0


def test_standardize_custom_size(sharp_image_path):
    image = cv2.imread(sharp_image_path)
    out = standardize(image, size=(64, 32))
    assert out.shape[0] == 32
    assert out.shape[1] == 64
