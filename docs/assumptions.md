# Assumptions and Caveats

## Statistical assumptions

- Right censoring is assumed non-informative conditional on observed covariates.
- Row-level records are treated as independent observations.
- Parametric baseline assumes lognormal latent completion times.
- Tail-mixture update assumes external anchor fidelity at days 300 and 629.

## Data quality assumptions

- Canonical row fields are publicly shareable and intentionally public.
- Missing-value sentinels (`?`, `FUTURE`, `N/A`, `#VALUE!`) are interpreted as unknown.
- Duration columns are considered derived mirrors and validated against date arithmetic.

## Interpretation limits

- This is a crowdsourced observational sample, not a complete population frame.
- Outputs are descriptive/probabilistic and not legal advice.
- Small sample size implies high variance, especially in tail behavior.
