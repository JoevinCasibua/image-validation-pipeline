# Automated Image Data Validation & Pre-processing Pipeline

A CLI tool that ingests a messy directory of images, gates them on quality
(corrupted / blurry / poorly exposed), and writes standardized survivors that
are ready for CNN training (resize → HSV normalization → Canny edge channel).

The headline feature is the **white-box test suite**: the gatekeeper's control-flow
graph is documented in [`docs/flow_graph.md`](docs/flow_graph.md) and every
independent path is exercised by `pytest`.

## Install

```bash
pip install opencv-python numpy pytest
```

## Run the CLI

```bash
python -m src.cli path/to/raw_images path/to/clean_output
```

The summary prints as JSON:

```json
{
  "Ready for Training": 1,
  "Blurry": 1,
  "Poorly Exposed": 1,
  "Corrupted": 1
}
```

Survivors land in the output directory as `<name>.png` plus a companion
`<name>_edges.png`. Rejects are copied into `<output>/_quarantine/`.

## Run the tests

```bash
pytest -v
```

All four independent paths through `check_image_quality` are covered, plus the
standardization step and a full end-to-end run through `process_directory`.

## Layout

```
src/
  pipeline.py   # check_image_quality, standardize, process_directory
  cli.py        # python -m src.cli
tests/
  conftest.py                    # synthetic sharp/blurry/dark/corrupted fixtures
  test_quality_paths.py          # white-box path tests P1–P4
  test_standardize.py            # resize + edge-channel unit tests
  test_pipeline_integration.py   # end-to-end routing test
docs/
  flow_graph.md   # control-flow graph + path coverage matrix
```
