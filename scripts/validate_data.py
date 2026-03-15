#!/usr/bin/env python3
from __future__ import annotations

import argparse

import pandas as pd

from rdu_timeline_analysis.validation import assert_valid_canonical_dataset


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate canonical RDU timeline dataset.")
    ap.add_argument("--csv", default="data/canonical/rdu_timeline_data.csv")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    assert_valid_canonical_dataset(df)
    print("Dataset validation passed.")


if __name__ == "__main__":
    main()
