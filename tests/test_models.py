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
