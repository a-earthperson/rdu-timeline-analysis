# Key Findings

## 1. 2025 receipt cohorts look materially faster than 2024 receipt cohorts

Among closed cases with known `receipt -> I-485 approval`, the 2025 receipt cohort has median total time 140 days (IQR 109-156, `n=17`) versus 224 days (IQR 217-255, `n=10`) for 2024 receipts. Because many recent cases are still open, the right-censored survival/CDF views are the more faithful comparison; they point in the same direction.

| Receipt year | Closed cases with known total time | Median `receipt -> I-485` | IQR |
| --- | ---: | ---: | --- |
| 2024 | 10 | 224 days | 217-255 days |
| 2025 | 17 | 140 days | 109-156 days |

![Total survival 2025](results/latest/plots/survival_total_2025_km_lognorm_mix.png)
![Total CDF 2025](results/latest/plots/cdf_total_2025_km_lognorm_mix.png)

The 2025 cohort fit keeps most probability mass well before day 300, with only a small modeled slow-tail component. In practical terms, the central part of the RDU sample is faster than the prior-year cohort even after keeping pending cases in view.

## 2. The dominant queue is still `receipt -> interview`

For cases with known interview timing, median `receipt -> interview` is 217 days for 2024 receipts (IQR 212-307, `n=11`) and 112 days for 2025 receipts (IQR 76-154, `n=32`). Among closed cases with both timestamps known, the median share of total wait spent before interview is 98.96%.

| Receipt year | Cases with known `receipt -> interview` | Median `receipt -> interview` | IQR |
| --- | ---: | ---: | --- |
| 2024 | 11 | 217 days | 212-307 days |
| 2025 | 32 | 112 days | 76-154 days |

Late-2025 receipts (`2025-10` through `2025-12`) are faster again in the current sample: median `receipt -> interview` is 63 days (`n=9`, IQR 58-71). That is still a small subsample, but it is directionally important.

![Receipt to interview density](results/latest/plots/density_receipt_to_interview_by_year.png)
![Receipt to interview ECDF](results/latest/plots/ecdf_receipt_to_interview_by_year.png)

This is the clearest structural result in the dataset: total processing time mostly behaves like interview scheduling time plus a comparatively smaller post-interview component.

## 3. After interview, approval is often near-immediate, but the long tail is real

For closed cases with known `interview -> I-485`:

- median delay is 1 day (`n=29`, IQR 1-10)
- 16/29 (55%) were approved within 1 day
- 23/29 (79%) were approved within 14 days
- 25/29 (86%) were approved within 30 days

For `interview -> I-130` when known:

- median delay is 1 day (`n=21`)
- 17/21 (81%) were approved within 1 day
- 21/21 (100%) were approved within 7 days

When both post-interview approval dates are known, 12/21 (57%) were approved on the same day.

![Interview survival](results/latest/plots/survival_interview_to_i485_km_lognorm.png)
![Interview to I-485 density](results/latest/plots/density_interview_to_i485.png)

The central mass is heavily concentrated at day 0-14, but the observed sample also includes completed waits of 45, 63, and 190 days, plus current pending cases well beyond 30 days. The correct reading is therefore: the interview often ends the main queue, but it does not eliminate tail risk.

For the full artifact inventory, including raw plots and CSV outputs, continue to [Results](results.md).
