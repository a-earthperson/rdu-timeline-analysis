# RDU Timeline Analysis

Public, reproducible analysis for the Raleigh/Durham USCIS AOS crowdsourced timeline sample.

## What this repo does

- Maintains a PR-reviewed canonical dataset in `data/canonical/rdu_timeline_data.csv`.
- Validates data contract consistency (schema, date semantics, status consistency, duration checks).
- Runs a deterministic analysis pipeline that emits:
  - density and ECDF plots
  - right-censored KM and parametric survival/CDF overlays
  - pending-case conditional predictions
  - run metadata manifest with input hash and git SHA
- Publishes current artifacts into `docs/results/latest/` for GitHub Pages.

## Quickstart (uv)

```bash
uv sync --all-groups
uv run python scripts/validate_data.py --csv data/canonical/rdu_timeline_data.csv
uv run python scripts/run_analysis.py --data-path data/canonical/rdu_timeline_data.csv
```

Outputs are written to:

- `results/latest/`
- `results/snapshots/YYYY-MM-DD/`
- `docs/results/latest/` (for site publishing)

## Repository layout

- `src/rdu_timeline_analysis/`: package implementation (`io`, `validation`, `models`, `plots`, `pipeline`)
- `scripts/`: thin CLIs for validation and analysis pipeline execution
- `data/canonical/`: source of truth dataset (PR-updated)
- `data/provenance.csv`: source traceability ledger for row-level records
- `results/`: generated artifacts and manifests
- `docs/`: GitHub Pages content
- `tests/`: unit and pipeline-level tests

## Data and privacy posture

- Row-level data is intentionally public in this repository.
- This is observational crowdsourced data and should not be interpreted as legal advice.

## Reproducibility contract

- Every run emits `results/latest/manifest.json` with:
  - analysis date
  - input file hash
  - git commit SHA
  - selected model switches
  - generated outputs

## Legacy files

- `rdu_timeline_methods.py` and `rdu_timeline_run_analysis.py` are retained as compatibility wrappers.
- The package + scripts under `src/` and `scripts/` are the supported path moving forward.
