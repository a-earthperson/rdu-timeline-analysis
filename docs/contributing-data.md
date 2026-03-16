---
title: Contributing Data
---

## Why additional rows matter

This project is most sensitive where the sample is thinnest: the post-interview tail, recent interview cohorts, and slow approvals that remain open well past the common 0-14 day window. A small number of new rows can materially change the interpretation of whether RDU is speeding up, whether a given interview month looks anomalous, and how aggressive the pending-case probabilities should be.

## Canonical contribution path

The repository itself is the canonical public dataset. New rows should be submitted through reviewed pull requests, not ad hoc edits to generated artifacts.

Primary files:

- `data/canonical/rdu_timeline_data.csv`
- `data/provenance.csv`
- `CONTRIBUTING.md`

## Minimum row needed for analysis

The canonical data contract requires the following fields:

- `user`
- `field_office`
- `i-485 receipt date`
- `interview date`
- `i-130 approval date`
- `i-485 approval date`
- `receipt to interview`
- `interview to i130`
- `interview to i485`
- `i130 to i485`
- `days since interview`
- `days total`
- `case closed`

If a row is added manually, the derived duration and status fields must remain internally consistent so that validation passes. The exact validation gates are documented in [Data Contract](data.md).

## Highest-value additions right now

- post-interview cases still pending beyond 30 days
- approvals that closed after an unusually long post-interview lag
- recent 2026 interviews, which help distinguish transient clustering from a persistent slowdown
- older open cases with verified receipt and interview dates, which stabilize the tail fit

## Metadata the current schema does not yet preserve

The current canonical table does not include a formal `case type` field or a free-text narrative field. If that metadata matters for interpretation, record it in `data/provenance.csv` or propose a schema change explicitly rather than silently overloading existing columns.

## Data policy

Row-level usernames and timelines in this repository are intentionally public. Do not submit private material or off-platform personal data without consent. Keep `field_office` explicit; the published site currently filters to `Raleigh/Durham`.
