## Change Type

- [ ] Data update
- [ ] Method/model update
- [ ] Pipeline/tooling update
- [ ] Documentation only

## Checklist

- [ ] Updated `data/canonical/rdu_timeline_data.csv` (if data change)
- [ ] Updated `data/provenance.csv` (if data change)
- [ ] Ran `uv run python scripts/validate_data.py --csv data/canonical/rdu_timeline_data.csv`
- [ ] Ran `uv run python scripts/run_analysis.py --data-path data/canonical/rdu_timeline_data.csv`
- [ ] Updated docs if assumptions/methods changed
