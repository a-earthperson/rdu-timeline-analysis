# Pending Cases and Forecasts

## 1. Open cases are part of the analysis, not excluded from it

A pending row contributes the information `T > current_age`. In survival-analysis terms, that is right censoring, not missingness. Discarding these rows would bias the published curves toward faster cases and erase most of the visible signal about the slow tail. That is why this project publishes Kaplan-Meier curves, censored parametric fits, and a conditional prediction table for open cases.

## 2. The current open tail is broader than a single-month anomaly

As of `2026-03-15`, all 18 pending rows in the filtered dataset are post-interview cases. December 2025 remains the single largest pending cluster, but the current tail is not confined to December.

| Interview month | Pending cases | Days since interview in current snapshot |
| --- | ---: | --- |
| 2025-05 | 2 | 291, 314 |
| 2025-10 | 1 | 151 |
| 2025-11 | 2 | 122, 131 |
| 2025-12 | 7 | 87, 87, 90, 95, 95, 95, 95 |
| 2026-01 | 5 | 46, 52, 59, 59, 67 |
| 2026-02 | 1 | 24 |

This matters because an earlier community hypothesis could be summarized as "December 2025 may be unusually sticky after interview." The current repo snapshot still supports watching December closely, but it now also contains a small number of much older unresolved cases. The active question is no longer just whether one interview month slowed down; it is whether the post-interview tail has become structurally wider than the fast majority would suggest.

## 3. Why the site publishes both baseline and USCIS-updated total-time curves

The empirical KM curve is driven entirely by the observed sample. The optional USCIS-tail mixture adds external anchors at day 300 (80%) and day 629 (93%) so that far-tail predictions are not unrealistically optimistic when the crowdsourced sample is still small.

![Total survival all years](results/latest/plots/survival_total_all_km_lognorm_mix.png)
![Total CDF all years](results/latest/plots/cdf_total_all_km_lognorm_mix.png)

The all-years curve shows dense support in the 100-250 day region and much sparser support in the far tail. That sparse tail is exactly where small-sample overconfidence is most dangerous, so the updated mixture is best read as a conservative regularization of the long-delay regime rather than a claim that every pending case is "really" USCIS-average.

## 4. How to use `pending_predictions.csv`

The prediction table at [results/latest/tables/pending_predictions.csv](results/latest/tables/pending_predictions.csv) reports conditional probabilities for each pending 2025 case, including:

- approval within 30 days from the current age
- approval within 60 days from the current age
- approval by day 300 from receipt
- approval by day 629 from receipt
- posterior probability of belonging to the modeled slow regime

Read these as model-based conditional probabilities, not individual case promises. In the current snapshot, the oldest open 2025 receipt cases are already 314-326 days from receipt and still only sit around 0.78-0.80 updated probability of approval by day 629. That is the practical meaning of preserving a slow tail in the model.

For fitting details and parameterization, see [Methods](methods.md) and [Assumptions and Caveats](assumptions.md).
