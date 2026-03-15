from __future__ import annotations

import json
from pathlib import Path

from rdu_timeline_analysis.pipeline import PipelineConfig, run_pipeline


def test_pipeline_writes_manifest_and_predictions(tmp_path: Path) -> None:
    data_path = Path("data/canonical/rdu_timeline_data.csv")
    docs_root = tmp_path / "docs"
    cfg = PipelineConfig(
        data_path=data_path,
        output_root=tmp_path / "results",
        docs_root=docs_root,
        today="2026-02-04",
        snapshot_tag="test-snapshot",
    )
    out = run_pipeline(cfg)
    manifest = Path(out["manifest_path"])
    assert manifest.exists()
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["snapshot_tag"] == "test-snapshot"
    assert Path(out["predictions_path"]).exists()
    assert (docs_root / "results" / "latest" / "manifest.json").exists()
