"""Backward-compatible entrypoint. Use scripts/run_analysis.py for new CLI."""

from pathlib import Path

from rdu_timeline_analysis.pipeline import PipelineConfig, run_pipeline


def main() -> None:
    # Keep historical default behavior with explicit paths.
    run_pipeline(
        PipelineConfig(
            data_path=Path("data/canonical/rdu_timeline_data.csv"),
            use_uscis_tail=True,
        )
    )


if __name__ == "__main__":
    main()
