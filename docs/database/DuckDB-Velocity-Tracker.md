# DuckDB Velocity Tracker Documentation

**Version**: 1.0.0
**Created**: 2025-08-27
**Purpose**: Data-driven project planning using proven velocity metrics

## Overview

The DuckDB Velocity Tracker provides realistic time estimates for project planning by analyzing actual completion data. It maintains a high-performance DuckDB database of work sessions and task completions to calculate proven velocity metrics.

## Proven Performance Baseline

**As of 2025-11-10 (CORRECTED):**
- **Velocity Rate**: 0.23 hours per story point
- **Data Source**: 14 story points completed in 3.25 actual hours (3 completed tasks)
- **Confidence Level**: Medium (60-90%) - limited data set, pending additional task completions
- **Sacred Geometry Integration**: Feeds burst planning and shape transition timing
- **Note**: Previous baseline of 0.44 hrs/point (21 points, 11 hours) was documented but source data not found in database. Corrected to match verified database records per TASK-P0-004 investigation (2025-11-10).

## Architecture

```text
┌─────────────────────────────────────────────────┐
│              CLI Interface                      │
│   cli/Invoke-VelocityTracker.ps1               │
├─────────────────────────────────────────────────┤
│              Python Core Engine                │
│   python/velocity/velocity_tracker.py          │
├─────────────────────────────────────────────────┤
│              DuckDB Database                    │
│   db/velocity.duckdb                           │
│   - work_sessions table                        │
│   - tasks table                                │
│   - velocity_metrics table                     │
└─────────────────────────────────────────────────┘
```

## Core Tables

### work_sessions
- `session_id` (VARCHAR, PK): Unique session identifier
- `task_id` (VARCHAR): Associated task identifier
- `start_time` (TIMESTAMP): Session start time
- `end_time` (TIMESTAMP): Session end time
- `duration_minutes` (INTEGER): Session duration
- `lines_changed` (INTEGER): Code lines modified
- `files_modified` (INTEGER): Files touched
- `complexity_score` (INTEGER): Complexity rating (1-5)

### tasks
- `task_id` (VARCHAR, PK): Unique task identifier
- `title` (VARCHAR): Task description
- `story_points` (INTEGER): Story point estimate
- `estimated_hours` (DECIMAL): Original time estimate
- `actual_hours` (DECIMAL): Actual completion time
- `complexity_category` (VARCHAR): Simple/Medium/Complex
- `status` (VARCHAR): Task status

### velocity_metrics
- Aggregated velocity calculations
- Sprint-level performance data
- Historical trend analysis

## API Reference

### CLI Actions

#### Record Work Session

```powershell
.\cli\Invoke-VelocityTracker.ps1 -Action Record -TaskId "T-20250827-001" -Hours 2.1 -StoryPoints 5 -LinesChanged 150 -FilesModified 3
```

#### Predict Completion Time

```powershell
.\cli\Invoke-VelocityTracker.ps1 -Action Predict -StoryPoints 8 -Complexity 1.2
```

**Output:**

```json
{
  "estimated_hours": 2.2,
  "estimated_days": 0.3,
  "confidence_percentage": 65,
  "base_hours_per_point": 0.23,
  "complexity_multiplier": 1.2
}
```

#### Generate Velocity Report

```powershell
.\cli\Invoke-VelocityTracker.ps1 -Action Report
```

**Output includes:**
- Current velocity summary (hours/point, points/day)
- Recent task completion data
- Estimation accuracy trends
- Data quality metrics

### Python API

#### Initialize Tracker

```python
from velocity.velocity_tracker import VelocityTracker

tracker = VelocityTracker("db/velocity.duckdb")
```

#### Record Session

```python
from datetime import datetime, timedelta

start_time = datetime.now() - timedelta(hours=2)
end_time = datetime.now()

session_id = tracker.record_session(
    task_id="T-20250827-001",
    start_time=start_time,
    end_time=end_time,
    lines_changed=150,
    files_modified=3,
    complexity_score=2
)
```

#### Calculate Velocity

```python
velocity = tracker.calculate_velocity(days_back=30)

print(f"Completed Tasks: {velocity['completed_tasks']}")
print(f"Hours per Point: {velocity['avg_hours_per_point']:.2f}")
print(f"Points per Day: {velocity['points_per_day']:.2f}")
```

#### Predict Completion

```python
prediction = tracker.predict_completion(
    story_points=8,
    complexity_multiplier=1.2
)

print(f"Estimated Hours: {prediction['estimated_hours']}")
print(f"Confidence: {prediction['confidence_percentage']}%")
```

## Sacred Geometry Integration

### Triangle (Stable Foundation)
- Use velocity data for realistic foundation timing
- Apply proven 0.23 hours/point rate for baseline work

### Spiral (Iterative Enhancement)
- Apply complexity multipliers for iterative phases
- Track velocity improvements over sprint cycles

### Fractal (Modular Reuse)
- Factor reuse complexity into velocity calculations
- Adjust estimates based on component extraction patterns

### Pentagon (Harmony Integration)
- Integrate velocity forecasting with milestone planning
- Balance story point distribution across geometry phases

## Data Quality & Confidence

### High Confidence (90%+)
- Tasks within established complexity patterns
- Sufficient historical data (10+ completed tasks)
- Consistent team composition and tooling

### Medium Confidence (60-90%)
- New complexity categories
- Limited historical data (3-10 tasks)
- Minor tooling or process changes

### Low Confidence (<60%)
- Novel work types or technologies
- Insufficient data (<3 tasks)
- Major team or process changes

## Best Practices

### Recording Sessions
1. Record sessions immediately after completion
2. Include accurate lines changed and files modified counts
3. Use consistent complexity scoring (1=Simple, 3=Medium, 5=Complex)
4. Break large sessions into logical work units

### Story Point Estimation
1. Use Fibonacci sequence (1, 2, 3, 5, 8, 13)
2. Estimate relative complexity, not absolute time
3. Include testing and documentation in estimates
4. Review and calibrate estimates against actuals

### Velocity Analysis
1. Use 30-day rolling windows for current velocity
2. Analyze trends over multiple sprints
3. Account for team changes and learning curves
4. Separate different work types (features vs bugs vs tech debt)

## Troubleshooting

### Common Issues

**Low Prediction Confidence**
- Increase historical data by recording more sessions
- Ensure consistent complexity scoring
- Verify story point calibration

**Velocity Drift**
- Check for team composition changes
- Review tooling or process modifications
- Analyze task complexity distribution

**Data Inconsistencies**
- Validate session recording accuracy
- Check for missing or duplicate entries
- Verify time tracking practices

### Diagnostic Commands

```powershell
# Check data quality
.\cli\Invoke-VelocityTracker.ps1 -Action Report | ConvertFrom-Json | Select-Object velocity_summary

# Validate recent sessions
python -c "from velocity.velocity_tracker import VelocityTracker; t=VelocityTracker(); print(t.generate_report())"
```

## Files and Dependencies

### Core Files
- `cli/Invoke-VelocityTracker.ps1` - PowerShell CLI wrapper
- `python/velocity/velocity_tracker.py` - Core DuckDB analytics engine
- `python/velocity/generate_roadmap.py` - Data-driven roadmap generation
- `db/velocity.duckdb` - DuckDB database file

### Dependencies
- Python 3.11+ with DuckDB package
- PowerShell 7+ for CLI interface
- Write access to `db/` directory

### Environment Setup

```powershell
# Install Python dependencies
pip install duckdb

# Verify CLI access
.\cli\Invoke-VelocityTracker.ps1 -Action Velocity
```

## Future Enhancements

### Planned Features
- Sprint velocity tracking and burndown charts
- Team velocity comparison and benchmarking
- Integration with task management systems
- Advanced predictive modeling with ML
- Real-time velocity dashboards

### Integration Opportunities
- GitHub issue tracking integration
- Azure DevOps work item sync
- Slack notifications for velocity alerts
- JIRA time tracking import
