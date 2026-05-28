"""Command-line entry point for the validation pipeline."""

from __future__ import annotations

import argparse
import json
import sys

from .pipeline import process_directory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and pre-process a directory of images for CNN training.",
    )
    parser.add_argument("input_dir", help="Directory of raw input images.")
    parser.add_argument("output_dir", help="Where standardized images are written.")
    parser.add_argument(
        "--quarantine",
        default=None,
        help="Where rejected images are copied. Defaults to <output>/_quarantine.",
    )
    args = parser.parse_args(argv)

    quarantine = args.quarantine or f"{args.output_dir.rstrip('/')}/_quarantine"
    summary = process_directory(args.input_dir, args.output_dir, quarantine)
    json.dump(summary, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
