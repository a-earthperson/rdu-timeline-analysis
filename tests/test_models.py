from __future__ import annotations

import numpy as np
import pandas as pd

from rdu_timeline_analysis.models import (
    calibrate_tail_mixture_from_uscis,
    fit_lognormal_censored_mle,
    kaplan_meier,
)


def test_km_monotonic() -> None:
    tte = pd.DataFrame(
        {
            "t": [10, 12, 13, 15, 18, 20],
            "event": [1, 0, 1, 1, 0, 1],
        }
    )
    km = kaplan_meier(tte, time_col="t", event_col="event")
    diffs = np.diff(km["survival"].to_numpy())
    assert (diffs <= 1e-12).all()


def test_lognormal_fit_and_tail_calibration() -> None:
    events = np.array([30.0, 45.0, 52.0, 60.0, 80.0, 100.0])
    cens = np.array([110.0, 130.0])
    params = fit_lognormal_censored_mle(events, cens)
    dist = params.frozen()
    mix = calibrate_tail_mixture_from_uscis(dist)
    assert 0.0 < mix.p_slow < 1.0


def test_tail_calibration_falls_back_when_fast_curve_is_slower_than_q80_anchor() -> None:
    events = np.array([280.0, 295.0, 320.0, 350.0, 400.0, 520.0])
    cens = np.array([560.0, 620.0, 700.0])
    params = fit_lognormal_censored_mle(events, cens)
    dist = params.frozen()

    mix = calibrate_tail_mixture_from_uscis(dist, q80=300.0, p80=0.80, q93=629.0, p93=0.93)

    assert mix.p_slow == 0.0
