from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from .io import load_canonical_dataset
from .models import (
    build_tte_total_days,
    calibrate_tail_mixture_from_uscis,
    cond_prob_approve_within,
    cond_prob_by,
    fit_lognormal_censored_mle,
)
from .plots import (
    density_plot_with_rug,
    plot_ecdf_overlay,
    plot_interview_to_i485_survival_and_cdf,
    plot_total_survival_and_cdf,
)
from .validation import assert_valid_canonical_dataset


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_sha() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        )
        return out.strip()
    except Exception:
        return "unknown"


def _coerce_naive_analysis_day(value: str | None) -> pd.Timestamp:
    """Normalize analysis timestamp to a tz-naive midnight Timestamp."""
    ts = pd.Timestamp(value) if value else pd.Timestamp.utcnow()
    if ts.tzinfo is not None:
        ts = ts.tz_convert(None)
    return ts.normalize()


@dataclass(frozen=True)
class PipelineConfig:
    data_path: Path = Path("data/canonical/rdu_timeline_data.csv")
    office_filter: str = "Raleigh/Durham"
    today: str | None = None
    use_uscis_tail: bool = True
    output_root: Path = Path("results")
    docs_root: Path = Path("docs")
    snapshot_tag: str | None = None


def _serialize_config(config: PipelineConfig) -> dict[str, object]:
    raw = asdict(config)
    out: dict[str, object] = {}
    for k, v in raw.items():
        out[k] = str(v) if isinstance(v, Path) else v
    return out


def _copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _pending_predictions(
    df_2025: pd.DataFrame, today: pd.Timestamp, use_uscis_tail: bool
) -> pd.DataFrame:
    tte_2025 = build_tte_total_days(df_2025, today=today)
    events = tte_2025.loc[tte_2025["event"] == 1, "t"].astype(float).to_numpy()
    cens = tte_2025.loc[tte_2025["event"] == 0, "t"].astype(float).to_numpy()
    params = fit_lognormal_censored_mle(events, cens)
    dist_fast = params.frozen()
    mix = None
    if use_uscis_tail:
        mix = calibrate_tail_mixture_from_uscis(
            dist_fast, q80=300.0, q93=629.0, p80=0.80, p93=0.93, t_anchor=300.0
        )

    pending = df_2025[~df_2025["closed"] & df_2025["i-485 receipt date_dt"].notna()].copy()
    pending["t0"] = (today - pending["i-485 receipt date_dt"]).dt.days.astype(float)
    rows: list[dict[str, float | str]] = []
    for _, r in pending.iterrows():
        t0 = float(r["t0"])
        out: dict[str, float | str] = {
            "user": r["user"],
            "t0_days_since_receipt": t0,
            "baseline_P_approve_within_30d": cond_prob_approve_within(dist_fast, t0, 30.0),
            "baseline_P_approve_within_60d": cond_prob_approve_within(dist_fast, t0, 60.0),
            "baseline_P_approve_by_300": cond_prob_by(dist_fast, t0, 300.0),
            "baseline_P_approve_by_629": cond_prob_by(dist_fast, t0, 629.0),
        }
        if mix is not None:
            out["updated_P_approve_by_300"] = mix.cond_prob_by_mix(dist_fast, t0, 300.0)
            out["updated_P_approve_by_629"] = mix.cond_prob_by_mix(dist_fast, t0, 629.0)
            out["updated_P_slow_mode_given_pending"] = mix.posterior_p_slow_given_pending(
                dist_fast, t0
            )
        rows.append(out)
    return pd.DataFrame(rows).sort_values("t0_days_since_receipt", ascending=False)


def run_pipeline(config: PipelineConfig) -> dict[str, object]:
    today = _coerce_naive_analysis_day(config.today)
    snapshot_tag = config.snapshot_tag or today.strftime("%Y-%m-%d")

    latest_root = config.output_root / "latest"
    plots_dir = latest_root / "plots"
    tables_dir = latest_root / "tables"
    processed_dir = latest_root / "processed"
    for p in (plots_dir, tables_dir, processed_dir):
        p.mkdir(parents=True, exist_ok=True)

    df = load_canonical_dataset(config.data_path)
    assert_valid_canonical_dataset(df)

    if config.office_filter:
        df = df[df["field_office"].astype(str).str.strip().eq(config.office_filter)].copy()
    if df.empty:
        raise ValueError(f"No rows left after office filter: {config.office_filter}")

    df["age_days_since_receipt"] = (today - df["i-485 receipt date_dt"]).dt.days
    df["age_days_since_interview"] = (today - df["interview date_dt"]).dt.days

    density_plot_with_rug(
        df=df,
        value_col="receipt to interview_num",
        hue_col="receipt_year",
        title="Receipt -> Interview (days) by receipt year (RDU sample)",
        xlabel="days from I-485 receipt to interview",
        outpath=plots_dir / "density_receipt_to_interview_by_year.png",
        xlim=(0, max(260, float(df["receipt to interview_num"].dropna().max()) + 10)),
    )
    plot_ecdf_overlay(
        df=df.dropna(subset=["receipt to interview_num", "receipt_year"]),
        value_col="receipt to interview_num",
        group_col="receipt_year",
        title="ECDF: Receipt -> Interview (days) by receipt year",
        xlabel="days from I-485 receipt to interview",
        outpath=plots_dir / "ecdf_receipt_to_interview_by_year.png",
        xlim=(0, max(260, float(df["receipt to interview_num"].dropna().max()) + 10)),
    )
    density_plot_with_rug(
        df=df,
        value_col="interview to i485_num",
        title="Interview -> I-485 approval (days), pending cases right-censored",
        xlabel="days from interview to I-485 approval",
        outpath=plots_dir / "density_interview_to_i485.png",
        censor_mask=~df["closed"],
        censor_value_col="age_days_since_interview",
        xlim=(0, 200),
    )
    density_plot_with_rug(
        df=df,
        value_col="days total_num",
        title="Total time: receipt -> I-485 approval (days), pending cases right-censored",
        xlabel="days from I-485 receipt to I-485 approval",
        outpath=plots_dir / "density_total_days.png",
        censor_mask=~df["closed"],
        censor_value_col="age_days_since_receipt",
        xlim=(0, max(320, float(df["days total_num"].dropna().max()) + 10)),
    )

    df_2025 = df[df["receipt_year"] == 2025].copy()
    plot_names = []
    plot_names.extend(
        plot_total_survival_and_cdf(
            df=df_2025,
            today=today,
            cohort_slug="2025",
            cohort_title="2025 receipt cohort",
            output_dir=plots_dir,
            use_uscis_tail=config.use_uscis_tail,
        )
    )
    plot_names.extend(
        plot_total_survival_and_cdf(
            df=df,
            today=today,
            cohort_slug="all",
            cohort_title="all receipt years",
            output_dir=plots_dir,
            use_uscis_tail=config.use_uscis_tail,
        )
    )
    plot_names.extend(
        plot_interview_to_i485_survival_and_cdf(df=df, today=today, output_dir=plots_dir)
    )

    pred = _pending_predictions(df_2025=df_2025, today=today, use_uscis_tail=config.use_uscis_tail)
    pred_path = tables_dir / "pending_predictions.csv"
    pred.to_csv(pred_path, index=False)

    processed_path = processed_dir / "dataset_filtered.csv"
    df.to_csv(processed_path, index=False)

    snapshot_dir = config.output_root / "snapshots" / snapshot_tag
    _copy_tree(latest_root, snapshot_dir)

    docs_latest = config.docs_root / "results" / "latest"
    _copy_tree(latest_root, docs_latest)

    manifest = {
        "run_timestamp_utc": datetime.now(UTC).isoformat(),
        "analysis_date": today.strftime("%Y-%m-%d"),
        "snapshot_tag": snapshot_tag,
        "git_sha": _git_sha(),
        "input_data_path": str(config.data_path),
        "input_data_sha256": _sha256_file(config.data_path),
        "office_filter": config.office_filter,
        "use_uscis_tail": config.use_uscis_tail,
        "plot_files": sorted(set([p.name for p in plots_dir.glob("*.png")] + plot_names)),
        "table_files": sorted([p.name for p in tables_dir.glob("*.csv")]),
        "config": _serialize_config(config),
    }
    manifest_path = latest_root / "manifest.json"
    snapshot_manifest_path = snapshot_dir / "manifest.json"
    docs_manifest_path = docs_latest / "manifest.json"
    for path in (manifest_path, snapshot_manifest_path, docs_manifest_path):
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    updates_path = config.docs_root / "updates.md"
    update_line = (
        f"- {today.strftime('%Y-%m-%d')}: snapshot `{snapshot_tag}`, "
        f"[manifest](results/latest/manifest.json), "
        f"[predictions](results/latest/tables/pending_predictions.csv)"
    )
    if updates_path.exists():
        existing = updates_path.read_text(encoding="utf-8")
        if update_line not in existing:
            updates_path.write_text(existing.rstrip() + "\n" + update_line + "\n", encoding="utf-8")

    return {
        "latest_root": str(latest_root),
        "snapshot_root": str(snapshot_dir),
        "docs_latest_root": str(docs_latest),
        "manifest_path": str(manifest_path),
        "predictions_path": str(pred_path),
    }
