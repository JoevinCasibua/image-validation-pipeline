"""White-box path testing for check_image_quality.

Flow graph nodes (see docs/flow_graph.md):
  1 -> imread
  2 -> "Corrupted"
  3 -> blur check
  4 -> "Blurry"
  5 -> exposure check
  6 -> "Poorly Exposed"
  7 -> "Ready for Training"

Independent paths exercised:
  Path 1: 1 -> 2
  Path 2: 1 -> 3 -> 4
  Path 3: 1 -> 3 -> 5 -> 6
  Path 4: 1 -> 3 -> 5 -> 7
"""

from src.pipeline import BLUR_THRESHOLD, check_image_quality


def test_path_1_corrupted_file_is_flagged(corrupted_image_path):
    result = check_image_quality(corrupted_image_path)
    assert result.status == "Corrupted"
    assert result.blur_score is None


def test_path_1_missing_file_is_flagged(tmp_path):
    result = check_image_quality(str(tmp_path / "does_not_exist.png"))
    assert result.status == "Corrupted"


def test_path_2_blurry_image_is_flagged(blurry_image_path):
    result = check_image_quality(blurry_image_path)
    assert result.status == "Blurry"
    assert result.blur_score is not None
    assert result.blur_score < BLUR_THRESHOLD


def test_path_3_dark_image_is_flagged(dark_image_path):
    result = check_image_quality(dark_image_path)
    assert result.status == "Poorly Exposed"
    assert result.brightness is not None


def test_path_4_sharp_image_passes(sharp_image_path):
    result = check_image_quality(sharp_image_path)
    assert result.status == "Ready for Training"
    assert result.blur_score is not None
    assert result.blur_score >= BLUR_THRESHOLD
