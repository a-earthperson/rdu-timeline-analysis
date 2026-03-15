from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .models import (
    build_tte_interview_to_i485_days,
    build_tte_total_days,
    calibrate_tail_mixture_from_uscis,
    ecdf,
    fit_lognormal_censored_mle,
    kaplan_meier,
    mixture_sf,
)


def density_plot_with_rug(
    *,
    df: pd.DataFrame,
    value_col: str,
    title: str,
    xlabel: str,
    outpath: Path,
    hue_col: str | None = None,
    censor_mask: pd.Series | None = None,
    censor_value_col: str | None = None,
    xlim: tuple[float, float] | None = None,
) -> None:
    plt.figure(figsize=(10, 5))
    data = df[value_col].dropna().astype(float)
    if hue_col is None:
        sns.histplot(data, bins=18, stat="density", alpha=0.25, color="#1f77b4", edgecolor="white")
        if len(data) >= 2 and float(np.std(data)) > 0.0:
            sns.kdeplot(data, color="#1f77b4", linewidth=2)
        sns.rugplot(data, color="#1f77b4", height=0.05, alpha=0.55)
    else:
        for grp, g in df.dropna(subset=[value_col, hue_col]).groupby(hue_col):
            vals = g[value_col].astype(float).dropna()
            if len(vals) < 1:
                continue
            if len(vals) >= 2 and float(np.std(vals)) > 0.0:
                sns.kdeplot(vals, linewidth=2, label=str(grp))
            sns.rugplot(vals, height=0.05, alpha=0.55)
        plt.legend(title=hue_col)

    if censor_mask is not None and censor_value_col is not None:
        cens = df.loc[censor_mask, censor_value_col].dropna().astype(float)
        for x in cens:
            plt.axvline(x, color="crimson", linestyle="--", linewidth=1.5, alpha=0.85)
        if len(cens):
            plt.text(
                0.99,
                0.95,
                f"right-censored n={len(cens)} (red dashed)",
                transform=plt.gca().transAxes,
                ha="right",
                va="top",
                color="crimson",
                fontsize=10,
            )

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("density")
    if xlim is not None:
        plt.xlim(*xlim)
    plt.tight_layout()
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outpath, dpi=170)
    plt.close()


def plot_ecdf_overlay(
    *,
    df: pd.DataFrame,
    value_col: str,
    group_col: str | None,
    title: str,
    xlabel: str,
    outpath: Path,
    xlim: tuple[float, float] | None = None,
) -> None:
    plt.figure(figsize=(10, 5))
    if group_col is None:
        xs, ps = ecdf(df[value_col])
        plt.step(xs, ps, where="post", linewidth=2)
    else:
        for grp, g in df.dropna(subset=[value_col, group_col]).groupby(group_col):
            xs, ps = ecdf(g[value_col])
            if len(xs) == 0:
                continue
            plt.step(xs, ps, where="post", linewidth=2, label=str(grp))
        plt.legend(title=group_col)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("ECDF")
    plt.ylim(0, 1.01)
    if xlim is not None:
        plt.xlim(*xlim)
    plt.tight_layout()
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outpath, dpi=170)
    plt.close()


def plot_total_survival_and_cdf(
    *,
    df: pd.DataFrame,
    today: pd.Timestamp,
    cohort_slug: str,
    cohort_title: str,
    output_dir: Path,
    use_uscis_tail: bool,
) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    tte = build_tte_total_days(df, today=today).dropna()
    if tte.empty:
        return []

    events = tte.loc[tte["event"] == 1, "t"].astype(float).to_numpy()
    cens = tte.loc[tte["event"] == 0, "t"].astype(float).to_numpy()
    km_curve = kaplan_meier(tte, time_col="t", event_col="event")
    params = fit_lognormal_censored_mle(events, cens)
    dist_fast = params.frozen()

    mix = None
    if use_uscis_tail:
        mix = calibrate_tail_mixture_from_uscis(
            dist_fast, q80=300.0, q93=629.0, p80=0.80, p93=0.93, t_anchor=300.0
        )

    x_max = max(800.0, float(np.nanmax(tte["t"])) + 30.0)
    xs = np.linspace(0.01, x_max, 1200)

    surv_name = f"survival_total_{cohort_slug}_km_lognorm_mix.png"
    cdf_name = f"cdf_total_{cohort_slug}_km_lognorm_mix.png"
    fit_name = f"fit_lognormal_fast_{cohort_slug}.png"

    plt.figure(figsize=(10, 5))
    plt.step(km_curve["t"], km_curve["survival"], where="post", color="black", linewidth=2, label="KM survival")
    plt.plot(
        xs,
        dist_fast.sf(xs),
        color="#1f77b4",
        linewidth=2,
        label=f"lognormal (mu={params.mu:.3f}, sigma={params.sigma:.3f})",
    )
    if mix is not None:
        s_mix = np.array([mixture_sf(mix, dist_fast, float(t)) for t in xs], dtype=float)
        plt.plot(xs, s_mix, color="crimson", linewidth=2, label=f"USCIS-tail mixture (p_slow={mix.p_slow:.3f})")
    y0 = -0.02
    plt.scatter(events, np.full_like(events, y0), marker="|", s=180, color="#1f77b4", alpha=0.85, label="events")
    plt.scatter(cens, np.full_like(cens, y0), marker="x", s=60, color="crimson", alpha=0.9, label="censored")
    plt.axvline(300, color="gray", linestyle=":", linewidth=1.5)
    plt.axvline(629, color="gray", linestyle=":", linewidth=1.5)
    plt.title(f"Total time survival: receipt->I-485 approval ({cohort_title})")
    plt.xlabel("days from receipt")
    plt.ylabel("S(t)")
    plt.ylim(-0.05, 1.02)
    plt.xlim(0, x_max)
    plt.legend(loc="upper right", fontsize=9, ncol=2)
    plt.tight_layout()
    plt.savefig(output_dir / surv_name, dpi=170)
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.step(km_curve["t"], 1.0 - km_curve["survival"], where="post", color="black", linewidth=2, label="KM CDF")
    plt.plot(xs, dist_fast.cdf(xs), color="#1f77b4", linewidth=2, label="lognormal CDF")
    if mix is not None:
        f_mix = np.array([mix.f_mix(dist_fast, float(t)) for t in xs], dtype=float)
        plt.plot(xs, f_mix, color="crimson", linewidth=2, label="USCIS-tail mixture CDF")
        plt.axhline(0.80, color="gray", linestyle="--", linewidth=1.2)
        plt.axhline(0.93, color="gray", linestyle="--", linewidth=1.2)
    plt.axvline(300, color="gray", linestyle=":", linewidth=1.5)
    plt.axvline(629, color="gray", linestyle=":", linewidth=1.5)
    plt.title(f"Total time CDF: receipt->I-485 approval ({cohort_title})")
    plt.xlabel("days from receipt")
    plt.ylabel("F(t)")
    plt.ylim(0, 1.02)
    plt.xlim(0, x_max)
    plt.legend(loc="lower right", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_dir / cdf_name, dpi=170)
    plt.close()

    plt.figure(figsize=(10, 5))
    sns.histplot(events, bins=14, stat="density", alpha=0.25, color="#1f77b4", edgecolor="white", label="closed")
    xs2 = np.linspace(0.01, max(320.0, float(np.max(events)) + 30.0), 700)
    plt.plot(xs2, dist_fast.pdf(xs2), color="black", linewidth=2, label="lognormal PDF (fast)")
    sns.rugplot(events, color="#1f77b4", height=0.05, alpha=0.6)
    for x in cens.astype(float):
        plt.axvline(x, color="crimson", linestyle="--", linewidth=1.5, alpha=0.85)
    plt.title(f"Baseline censored-lognormal fit (fast) - {cohort_title}")
    plt.xlabel("days from receipt to approval")
    plt.ylabel("density")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / fit_name, dpi=170)
    plt.close()

    return [surv_name, cdf_name, fit_name]


def plot_interview_to_i485_survival_and_cdf(
    *, df: pd.DataFrame, today: pd.Timestamp, output_dir: Path
) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    tte = build_tte_interview_to_i485_days(df, today=today).dropna()
    if tte.empty:
        return []

    events = tte.loc[tte["event"] == 1, "t"].astype(float).to_numpy()
    cens = tte.loc[tte["event"] == 0, "t"].astype(float).to_numpy()
    km_curve = kaplan_meier(tte, time_col="t", event_col="event")
    shift = 0.5 if (np.min(np.concatenate([events, cens])) <= 0.0) else 0.0
    params = fit_lognormal_censored_mle(events + shift, cens + shift)
    dist = params.frozen()
    x_max = max(200.0, float(np.nanmax(tte["t"])) + 20.0)
    xs = np.linspace(0.01, x_max, 1000)

    surv_name = "survival_interview_to_i485_km_lognorm.png"
    cdf_name = "cdf_interview_to_i485_km_lognorm.png"

    plt.figure(figsize=(10, 5))
    plt.step(km_curve["t"], km_curve["survival"], where="post", color="black", linewidth=2, label="KM survival")
    plt.plot(xs, dist.sf(xs + shift), color="#1f77b4", linewidth=2, label=f"lognormal on (t+{shift})")
    y0 = -0.02
    plt.scatter(events, np.full_like(events, y0), marker="|", s=180, color="#1f77b4", alpha=0.85, label="events")
    plt.scatter(cens, np.full_like(cens, y0), marker="x", s=60, color="crimson", alpha=0.9, label="censored")
    plt.title("Interview->I-485 survival (KM + shifted-lognormal)")
    plt.xlabel("days since interview")
    plt.ylabel("S(t)")
    plt.ylim(-0.05, 1.02)
    plt.xlim(0, x_max)
    plt.legend(loc="upper right", fontsize=9, ncol=2)
    plt.tight_layout()
    plt.savefig(output_dir / surv_name, dpi=170)
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.step(km_curve["t"], 1.0 - km_curve["survival"], where="post", color="black", linewidth=2, label="KM CDF")
    plt.plot(xs, dist.cdf(xs + shift), color="#1f77b4", linewidth=2, label="shifted-lognormal CDF")
    plt.title("Interview->I-485 CDF (KM + shifted-lognormal)")
    plt.xlabel("days since interview")
    plt.ylabel("F(t)")
    plt.ylim(0, 1.02)
    plt.xlim(0, x_max)
    plt.legend(loc="lower right", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_dir / cdf_name, dpi=170)
    plt.close()

    return [surv_name, cdf_name]
