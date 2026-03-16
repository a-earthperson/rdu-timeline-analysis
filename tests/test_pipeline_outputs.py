from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from rdu_timeline_analysis.pipeline import PipelineConfig, run_pipeline


def test_pipeline_writes_manifest_and_predictions(tmp_path: Path) -> None:
    data_path = Path("data/canonical/rdu_timeline_data.csv")
    docs_root = tmp_path / "docs"
    cfg = PipelineConfig(
        data_path=data_path,
        output_root=tmp_path / "results",
        docs_root=docs_root,
        today="2026-02-04T00:00:00Z",
        snapshot_tag="test-snapshot",
    )
    out = run_pipeline(cfg)
    manifest = Path(out["manifest_path"])
    assert manifest.exists()
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["snapshot_tag"] == "test-snapshot"
    assert Path(out["predictions_path"]).exists()
    assert (docs_root / "results" / "latest" / "manifest.json").exists()


def test_pipeline_predictions_include_all_pending_receipt_years_and_clear_stale_outputs(
    tmp_path: Path,
) -> None:
    csv_text = """user,field_office,i-485 receipt date,interview date,i-130 approval date,i-485 approval date,receipt to interview,interview to i130,interview to i485,i130 to i485,days since interview,days total,case closed
closed_case,Raleigh/Durham,01-01-2025,02-01-2025,02-02-2025,02-10-2025,31,1,9,8,9,40,YES
pending_2025,Raleigh/Durham,10-01-2025,12-15-2025,?,FUTURE,75,?,?,?,20,171,NO
pending_2026,Raleigh/Durham,01-05-2026,02-10-2026,?,FUTURE,36,?,?,?,19,55,NO
"""
    data_path = tmp_path / "mini.csv"
    data_path.write_text(csv_text, encoding="utf-8")

    stale_plot = tmp_path / "results" / "latest" / "plots" / "stale.png"
    stale_plot.parent.mkdir(parents=True, exist_ok=True)
    stale_plot.write_text("stale", encoding="utf-8")

    cfg = PipelineConfig(
        data_path=data_path,
        output_root=tmp_path / "results",
        docs_root=tmp_path / "docs",
        today="2026-03-01T00:00:00Z",
        snapshot_tag="mini-snapshot",
    )
    out = run_pipeline(cfg)

    pred = pd.read_csv(out["predictions_path"])
    assert set(pred["user"]) == {"pending_2025", "pending_2026"}
    assert set(pred["receipt_year"]) == {2025, 2026}
    assert not stale_plot.exists()
