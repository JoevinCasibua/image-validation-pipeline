"""End-to-end test for process_directory.

Confirms that a messy directory containing one of each category is split
correctly between the standardized output folder and the quarantine folder.
"""

import os

from src.pipeline import process_directory


def test_process_directory_routes_each_category(messy_input_dir, tmp_path):
    output_dir = tmp_path / "clean"
    quarantine_dir = tmp_path / "quarantine"

    summary = process_directory(messy_input_dir, str(output_dir), str(quarantine_dir))

    assert summary["Ready for Training"] == 1
    assert summary["Blurry"] == 1
    assert summary["Poorly Exposed"] == 1
    assert summary["Corrupted"] == 1

    outputs = os.listdir(output_dir)
    assert any(name.endswith("_edges.png") for name in outputs)
    assert any(name == "good.png" for name in outputs)

    quarantined = os.listdir(quarantine_dir)
    assert "blurry.png" in quarantined
    assert "dark.png" in quarantined
    assert "broken.jpg" in quarantined
