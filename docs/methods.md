---
title: Methods
---

## Data model and censoring

- Each case contributes to time-to-event analysis with:
  - `event=1`: approved (closed)
  - `event=0`: pending (right-censored at analysis date)
- Two endpoints are modeled:
  - total time: receipt -> I-485 approval
  - interview lag: interview -> I-485 approval
- Primary model fits use all office-filtered rows with valid timing information; they are not restricted to a fixed receipt-year cohort.
- When the site shows temporal comparisons for `receipt -> interview`, it stratifies by interview timing so early-2026 office activity is visible even when those cases have 2025 receipt dates.

## Non-parametric baseline

- Kaplan-Meier estimator is computed over unique event/censor times.
- Published curves include event and censor rug markers.

## Parametric baseline

- Total-time distribution is fit with censored lognormal MLE:
  - likelihood uses log-PDF for events and log-survival for right-censored rows.
  - optimization uses Nelder-Mead on `(mu, log_sigma)`.
- Interview->approval uses shifted lognormal (`t + 0.5`) to handle zero-day approvals.

## USCIS-tail mixture (optional)

- Fast regime: censored-lognormal baseline.
- Slow regime: delayed exponential tail beginning at day 300.
- Calibration anchors:
  - `F(300)=0.80`
  - `F(629)=0.93`
- If the fitted baseline is already slower than the day-300 anchor, the calibration falls back to `p_slow = 0` rather than forcing an infeasible negative slow mass.
- Conditional pending-case probabilities are computed under both baseline and updated mixture model for all pending office-filtered cases with a known receipt date.
