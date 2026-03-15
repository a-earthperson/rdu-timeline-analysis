---
title: Data Contract
---

## Canonical ingestion model

- Canonical source of truth: `data/canonical/rdu_timeline_data.csv`
- Ingestion mechanism: reviewed pull requests only.
- Provenance ledger: `data/provenance.csv`

## Required columns

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

## Validation gates

CI fails on:

- missing required columns
- malformed dates
- status/date inconsistency (`case closed` vs approval date)
- impossible time direction (approval before receipt/interview)
- derived duration mismatch beyond tolerance
- duplicate `user + receipt_date` rows

## Office scope

Analysis pipeline defaults to `field_office == Raleigh/Durham`.
