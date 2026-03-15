# RDU Timeline Analysis

This site presents the latest reproducible Raleigh/Durham AOS crowdsourced snapshot as a research-style report rather than a flat artifact index. The motivating question is narrow: given the current public sample, what appears to drive total processing time in RDU, and what should be inferred from cases that remain pending after interview?

As of analysis date `2026-03-15`, the filtered RDU snapshot contains 47 cases: 29 closed and 18 pending (right-censored). The primary endpoint is `receipt -> I-485 approval`; the secondary endpoint is `interview -> I-485 approval`.

At a high level, the current snapshot points to three conclusions:

- 2025 receipt cohorts appear materially faster than 2024 receipt cohorts.
- Most observed total wait is still concentrated in `receipt -> interview`.
- Post-interview approval is often very fast, but the remaining open tail is non-trivial and needs explicit censoring-aware interpretation.

## Recommended Reading Order

1. [Research Question and Scope](research-question.md)
2. [Key Findings](key-findings.md)
3. [Pending Cases and Forecasts](pending-cases.md)
4. [Contributing Data](contributing-data.md)

## Technical Reference

- [Artifact Index](results.md)
- [Methods](methods.md)
- [Data Contract](data.md)
- [Assumptions and Caveats](assumptions.md)
- [Updates](updates.md)

## Machine-readable Artifacts

- [Manifest](results/latest/manifest.json)
- [Filtered analysis dataset](results/latest/processed/dataset_filtered.csv)
- [Pending predictions](results/latest/tables/pending_predictions.csv)
