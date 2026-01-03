# Performance Gate Reseed - Quick Reference

## Commands

### Check Stability Status
```bash
python python/tools/stability_aggregator.py
```

### Preview Reseed (Safe)
```bash
python python/tools/perf_gate_lazy_typer.py --dry-run-reseed
```

### Execute Reseed
```bash
python python/tools/perf_gate_lazy_typer.py --reseed-baseline \
    --reseed-note "Your descriptive note here"
```

## Thresholds

| Metric | Threshold | Purpose |
|--------|-----------|---------|
| `lazy_median_us` CV | ≤ 15% | Startup consistency |
| `improvement_pct` CV | ≤ 25% | Improvement variance |
| `baseline_drift` | ≥ 5% | Significant change |

## Conditions for Reseed

✅ **All must be true:**
- Stability summary exists
- Variance acceptable (CV within thresholds)
- Baseline outdated (≥5% drift)
- No concerning trends

## File Locations

- **Stability Summary**: `build/artifacts/perf/stability/stability_summary.json`
- **Baseline**: `build/artifacts/perf/baseline_stats.json`
- **Batch Artifacts**: `build/artifacts/perf/stability/batch_*/`

## Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| "No stability summary" | Run aggregator script |
| "Variance not acceptable" | Collect more batches or investigate performance |
| "Conditions not met" | Review drift percentage and trends |
| Atomic write errors | Close file handles, check permissions |

## Safety Features

- ✅ Dry-run mode for safe preview
- ✅ Atomic file operations (no corruption risk)
- ✅ Complete audit trail in `reseed_events`
- ✅ Variance guards prevent bad reseeds
- ✅ Original baseline preserved on failure
