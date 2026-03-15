# Contributing

## Data updates (canonical ingestion path)

This project uses **reviewed pull requests** as the ingestion mechanism.

1. Update `data/canonical/rdu_timeline_data.csv`.
2. Add/update provenance entries in `data/provenance.csv`.
3. Run locally:
   - `uv run python scripts/validate_data.py --csv data/canonical/rdu_timeline_data.csv`
   - `uv run python scripts/run_analysis.py --data-path data/canonical/rdu_timeline_data.csv`
4. Commit resulting updates to `results/latest/` and `docs/results/latest/`.

## Validation requirements

PRs are expected to pass:

- schema and semantic checks
- unit tests
- deterministic pipeline execution in CI

## Data policy

- Row-level usernames and timelines are intentionally public in this repository.
- Do not submit private/secret source material.
- Keep `field_office` explicit; current published analysis defaults to `Raleigh/Durham`.

## Method changes

If you change model assumptions, update:

- `docs/methods.md`
- `docs/assumptions.md`
- manifest expectations in tests
