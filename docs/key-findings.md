---
title: Key Findings
---

## 1. The dominant queue is still `receipt -> interview`

Among closed cases with both timestamps known, the median share of total wait spent before interview is 98.96%. That makes the pre-interview stage the main determinant of total time in the observed sample.

The all-case survival/CDF views keep the right-censored tail in frame and therefore provide the least assumption-heavy top-level picture of total processing time.

![Total survival all years](results/latest/plots/survival_total_all_km_lognorm_mix.png)
![Total CDF all years](results/latest/plots/cdf_total_all_km_lognorm_mix.png)

The core structural interpretation is unchanged: most cases spend the overwhelming majority of their lifecycle waiting to reach interview, not waiting after interview.

## 2. More recent interview periods, including early 2026, appear faster

To avoid anchoring the story to `receipt_year`, the main temporal comparison now keys `receipt -> interview` to interview timing. That makes current office activity visible even when the underlying receipts are still from 2025.

| Interview year | Cases with known `receipt -> interview` | Median `receipt -> interview` | IQR |
| --- | ---: | ---: | --- |
| 2025 | 36 | 154 days | 108-212 days |
| 2026 | 7 | 71 days | 61-100 days |

The 2026 group is still immature: only 1 of the 7 interviewed-in-2026 cases is closed, and 6 remain pending after interview. So the current signal should be read as an early acceleration in the pre-interview stage, not a stable estimate of full end-to-end completion time for 2026-era processing.

![Receipt to interview density by interview year](results/latest/plots/density_receipt_to_interview_by_interview_year.png)
![Receipt to interview ECDF by interview year](results/latest/plots/ecdf_receipt_to_interview_by_interview_year.png)

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
