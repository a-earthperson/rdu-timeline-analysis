from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd
import scipy.optimize as opt
import scipy.stats as st


def kaplan_meier(df: pd.DataFrame, time_col: str, event_col: str) -> pd.DataFrame:
    """Compute a Kaplan-Meier survival curve."""
    d = df[[time_col, event_col]].dropna().copy()
    d = d.sort_values(time_col)
    times = np.sort(d[time_col].unique())
    surv = 1.0
    out = []
    for t in times:
        at_risk = int((d[time_col] >= t).sum())
        events = int(((d[time_col] == t) & (d[event_col] == 1)).sum())
        cens = int(((d[time_col] == t) & (d[event_col] == 0)).sum())
        if at_risk > 0 and events > 0:
            surv *= 1.0 - (events / at_risk)
        out.append(
            {
                "t": float(t),
                "at_risk": at_risk,
                "events": events,
                "censored": cens,
                "survival": float(surv),
            }
        )
    return pd.DataFrame(out)


@dataclass(frozen=True)
class LognormalParams:
    mu: float
    sigma: float

    def frozen(self) -> st.rv_continuous:
        return st.lognorm(s=self.sigma, scale=math.exp(self.mu))


def fit_lognormal_censored_mle(
    events: np.ndarray,
    censored: np.ndarray,
    init_mu: float | None = None,
    init_sigma: float = 0.5,
) -> LognormalParams:
    """Fit lognormal time-to-event distribution under right censoring via MLE."""
    events = np.asarray(events, dtype=float)
    censored = np.asarray(censored, dtype=float)
    events = events[np.isfinite(events)]
    censored = censored[np.isfinite(censored)]

    if events.size == 0:
        raise ValueError("Cannot fit censored lognormal without at least one event.")

    if init_mu is None:
        init_mu = float(np.log(np.median(events)))

    def nll(theta: np.ndarray) -> float:
        mu, log_sigma = float(theta[0]), float(theta[1])
        sigma = float(np.exp(log_sigma))
        dist = st.lognorm(s=sigma, scale=math.exp(mu))
        ll = 0.0
        if events.size:
            ll += float(np.sum(dist.logpdf(events)))
        if censored.size:
            ll += float(np.sum(dist.logsf(censored)))
        return -ll

    res = opt.minimize(
        nll,
        x0=np.array([init_mu, math.log(init_sigma)], dtype=float),
        method="Nelder-Mead",
    )
    if not res.success:
        raise RuntimeError(f"MLE optimization failed: {res.message}")
    mu_hat, log_sigma_hat = float(res.x[0]), float(res.x[1])
    return LognormalParams(mu=mu_hat, sigma=float(np.exp(log_sigma_hat)))


def cond_prob_approve_within(dist: st.rv_continuous, t0: float, delta: float) -> float:
    """P(T <= t0 + delta | T > t0)."""
    if delta <= 0:
        return 0.0
    f0 = float(dist.cdf(t0))
    f1 = float(dist.cdf(t0 + delta))
    s0 = 1.0 - f0
    if s0 <= 0:
        return math.nan
    return (f1 - f0) / s0


def cond_prob_by(dist: st.rv_continuous, t0: float, t_target: float) -> float:
    """P(T <= t_target | T > t0)."""
    if t_target <= t0:
        return 0.0
    f0 = float(dist.cdf(t0))
    ft = float(dist.cdf(t_target))
    s0 = 1.0 - f0
    if s0 <= 0:
        return math.nan
    return (ft - f0) / s0


@dataclass(frozen=True)
class TailMixtureParams:
    p_slow: float
    lambda_tail: float
    t_anchor: float = 300.0
    q80: float = 300.0
    q93: float = 629.0

    def f_slow(self, t: float) -> float:
        if t <= self.t_anchor:
            return 0.0
        return 1.0 - math.exp(-self.lambda_tail * (t - self.t_anchor))

    def f_mix(self, fast_dist: st.rv_continuous, t: float) -> float:
        return (1.0 - self.p_slow) * float(fast_dist.cdf(t)) + self.p_slow * self.f_slow(t)

    def posterior_p_slow_given_pending(self, fast_dist: st.rv_continuous, t0: float) -> float:
        s_fast = 1.0 - float(fast_dist.cdf(t0))
        s_mix = self.p_slow + (1.0 - self.p_slow) * s_fast
        return self.p_slow / s_mix

    def cond_prob_by_mix(self, fast_dist: st.rv_continuous, t0: float, t_target: float) -> float:
        if t_target <= t0:
            return 0.0
        f0 = self.f_mix(fast_dist, t0)
        ft = self.f_mix(fast_dist, t_target)
        s0 = 1.0 - f0
        if s0 <= 0:
            return math.nan
        return (ft - f0) / s0


def calibrate_tail_mixture_from_uscis(
    fast_dist: st.rv_continuous,
    q80: float = 300.0,
    q93: float = 629.0,
    p80: float = 0.80,
    p93: float = 0.93,
    t_anchor: float = 300.0,
) -> TailMixtureParams:
    """Calibrate two-regime mixture to hit external CDF anchors.

    When the fitted fast distribution is already slower than the q80 anchor
    (F_fast(q80) <= p80), the original two-regime calibration is infeasible
    because it would require negative slow mass. In that regime, fall back to
    ``p_slow = 0`` (fast-only curve) instead of hard-failing the pipeline.
    """
    if abs(t_anchor - q80) > 1e-9:
        raise ValueError("Calibration assumes t_anchor == q80.")
    f_fast_80 = float(fast_dist.cdf(q80))
    f_fast_93 = float(fast_dist.cdf(q93))
    if f_fast_80 <= 0:
        raise ValueError("fast_dist CDF at q80 is zero; cannot calibrate mixture.")
    if f_fast_80 <= p80:
        return TailMixtureParams(
            p_slow=0.0,
            lambda_tail=float("inf"),
            t_anchor=float(t_anchor),
            q80=float(q80),
            q93=float(q93),
        )
    p_slow = 1.0 - (p80 / f_fast_80)
    delta = float(q93 - q80)
    if delta <= 0:
        raise ValueError("Calibration requires q93 > q80.")
    rhs = 1.0 - (p93 - (1.0 - p_slow) * f_fast_93) / p_slow
    if rhs <= 0.0:
        lambda_tail = float("inf")
    elif rhs >= 1.0:
        lambda_tail = 0.0
    else:
        lambda_tail = -math.log(rhs) / delta
    return TailMixtureParams(
        p_slow=float(p_slow),
        lambda_tail=float(lambda_tail),
        t_anchor=float(t_anchor),
        q80=float(q80),
        q93=float(q93),
    )


def duration_days(start: pd.Timestamp, end: pd.Timestamp) -> float:
    if pd.isna(start) or pd.isna(end):
        return np.nan
    return float((end - start).days)


def ecdf(x: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    s = pd.Series(x, dtype="float64").dropna().to_numpy()
    s = s[np.isfinite(s)]
    if s.size == 0:
        return np.array([]), np.array([])
    xs = np.sort(s)
    ps = np.arange(1, xs.size + 1, dtype=float) / xs.size
    return xs, ps


def build_tte_total_days(
    df: pd.DataFrame, *, today: pd.Timestamp, user_col: str = "user"
) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        user = r.get(user_col, None)
        closed = bool(r.get("closed", False))
        receipt = r.get("i-485 receipt date_dt", pd.NaT)
        approval = r.get("i-485 approval date_dt", pd.NaT)
        if closed:
            t = duration_days(receipt, approval)
            if not np.isfinite(t):
                t = float(r.get("days total_num", np.nan))
            if np.isfinite(t):
                rows.append({"user": user, "t": float(t), "event": 1})
        else:
            t = duration_days(receipt, today)
            if not np.isfinite(t):
                t = float(r.get("days total_num", np.nan))
            if np.isfinite(t):
                rows.append({"user": user, "t": float(t), "event": 0})
    return pd.DataFrame(rows)


def build_tte_interview_to_i485_days(
    df: pd.DataFrame, *, today: pd.Timestamp, user_col: str = "user"
) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        user = r.get(user_col, None)
        closed = bool(r.get("closed", False))
        interview = r.get("interview date_dt", pd.NaT)
        approval = r.get("i-485 approval date_dt", pd.NaT)
        if closed:
            t = duration_days(interview, approval)
            if not np.isfinite(t):
                t = float(r.get("interview to i485_num", np.nan))
            if np.isfinite(t):
                rows.append({"user": user, "t": float(t), "event": 1})
        else:
            t = duration_days(interview, today)
            if not np.isfinite(t):
                t = float(r.get("days since interview_num", np.nan))
            if np.isfinite(t):
                rows.append({"user": user, "t": float(t), "event": 0})
    return pd.DataFrame(rows)


def mixture_sf(mix: TailMixtureParams, fast_dist: st.rv_continuous, t: float) -> float:
    p = mix.p_slow
    s_fast = float(fast_dist.sf(t))
    if t <= mix.t_anchor:
        s_slow = 1.0
    else:
        s_slow = math.exp(-mix.lambda_tail * (t - mix.t_anchor))
    return (1.0 - p) * s_fast + p * s_slow
