---
applyTo: "optimize*, performance*, slow*, speed*, latency*, throughput*, bottleneck*"
description: "Performance optimization quick reference"
---

# Performance Optimization Quick Reference

## Profiling First (Always Measure)

| Tool | Use Case | Command |
|------|----------|---------|
| **cProfile** | CPU hotspots | `python -m cProfile -o profile.stats script.py` |
| **line_profiler** | Line-by-line | `kernprof -l -v script.py` |
| **memory_profiler** | Memory usage | `python -m memory_profiler script.py` |
| **py-spy** | Production profiling | `py-spy top --pid PID` |

## Performance Targets

| Metric | Target |
|--------|--------|
| API p95 | <200ms |
| DB query (indexed) | <20ms |
| CLI cold start | <500ms |

## Quick Wins Checklist

- [ ] Add database indexes for filtered columns
- [ ] Use connection pooling
- [ ] Enable query caching
- [ ] Lazy load heavy imports
- [ ] Use async for I/O operations

## Golden Ratio Rule

Focus on **20% of code paths** that cause **80% of performance issues**.

```bash
# Find the top 20% by cumulative time
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumtime').print_stats(0.20)"
```

## pytest-benchmark

```python
def test_performance(benchmark):
    result = benchmark(my_function, arg1, arg2)
    assert benchmark.stats['mean'] < 0.150  # <150ms
```

## Full Reference
See `.github/instructions/archive/performance-optimization-full.md` for comprehensive guide.
