#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from rdu_timeline_analysis.pipeline import PipelineConfig, run_pipeline


def main() -> None:
    ap = argparse.ArgumentParser(description="Run RDU timeline analysis pipeline.")
    ap.add_argument("--data-path", default="data/canonical/rdu_timeline_data.csv")
    ap.add_argument(
        "--today", default=None, help="Analysis date in YYYY-MM-DD; defaults to UTC current date."
    )
    ap.add_argument("--office-filter", default="Raleigh/Durham")
    ap.add_argument("--output-root", default="results")
    ap.add_argument("--docs-root", default="docs")
    ap.add_argument(
        "--snapshot-tag", default=None, help="Optional snapshot tag (default: YYYY-MM-DD)."
    )
    ap.add_argument(
        "--no-uscis-tail", action="store_true", help="Disable USCIS-tail mixture outputs."
    )
    args = ap.parse_args()

    cfg = PipelineConfig(
        data_path=Path(args.data_path),
        today=args.today,
        office_filter=args.office_filter,
        use_uscis_tail=not args.no_uscis_tail,
        output_root=Path(args.output_root),
        docs_root=Path(args.docs_root),
        snapshot_tag=args.snapshot_tag,
    )
    out = run_pipeline(cfg)
    for k, v in out.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
