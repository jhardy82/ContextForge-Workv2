# PyTest Configuration Cleanup Plan
## Prioritize Rich Outputs & Comprehensive Logging

### Current State Analysis
**Total pytest configurations found:** 28+ files
**Configuration types identified:**
- **pytest-visual.ini** ✅ - Rich-optimized (KEEP - Primary)
- **pyproject.toml** ✅ - Professional comprehensive (ENHANCE with Rich)
- **Multiple legacy configs** ❌ - Non-Rich, conflicting settings (REMOVE/CONSOLIDATE)

### Cleanup Strategy

#### 1. Primary Configuration Hierarchy
```
Priority 1: pytest-visual.ini (Rich-optimized)
Priority 2: pyproject.toml (Enhanced with Rich integration)
Priority 3: Minimal project-specific overrides only
```

#### 2. Files to Remove (Non-Rich/Conflicting)
```
pytest-performance.ini     # Explicitly disables Rich (-p no:pytest_rich -p no:rich)
pytest-optimal.ini         # Uses -q (quiet mode) - anti-Rich
pytest-fast.ini           # Uses -q (quiet mode) - anti-Rich
pytest-minimal.ini        # Uses -q (quiet mode) - anti-Rich
pytest-monokai-enhanced.ini    # Duplicate/competing config
pytest-monokai-enhanced-working.ini  # Duplicate/competing config
pytest-unit.ini           # Legacy config without Rich integration
pytest-rich.ini           # Redundant with pytest-visual.ini
pytest-clean.ini          # Generic config without Rich optimization
pytest-working.ini        # Legacy/testing config
```

#### 3. Files to Update (Rich Integration)
```
python/api/tests/pytest.ini  # Add Rich integration
projects/unified_logger/pytest.ini  # Add Rich integration (currently minimal)
pyproject.toml  # Add Rich-specific addopts and environment
```

#### 4. Configuration Standards (Rich + Comprehensive Logging)
**Required Rich Integration:**
- `--rich` flag for pytest-rich-plugin
- Rich color scheme: monokai/enhanced
- Visual parsing optimizations
- Comprehensive progress tracking

**Required Logging Standards:**
- Structured JSONL output
- Correlation ID tracking
- Session summary artifacts
- Evidence-based traceability

### Implementation Actions

#### Phase 1: Remove Conflicting Configurations
- Delete all non-Rich/anti-Rich pytest configs
- Remove quiet mode (-q) configurations
- Eliminate Rich-disabled configs (-p no:pytest_rich)

#### Phase 2: Enhance Primary Configurations
- Update pyproject.toml with Rich addopts
- Integrate comprehensive logging with Rich outputs
- Standardize color schemes and visual formatting

#### Phase 3: Update Project-Specific Configs
- Align API tests with Rich standards
- Update unified_logger project config
- Ensure all configs support comprehensive logging

#### Phase 4: VS Code Integration
- Update task configurations to use primary Rich config
- Remove references to deleted config files
- Standardize on pytest-visual.ini for all Rich operations

### Expected Outcomes
✅ Single source of truth for Rich pytest configuration
✅ Elimination of conflicting/competing configs
✅ Comprehensive logging integrated with Rich visual outputs
✅ Faster human parsing through optimized visual formatting
✅ Consistent experience across all test execution contexts

### Configuration Consolidation Rules
1. **Rich First**: All configurations must prioritize Rich outputs
2. **Comprehensive Logging**: Structured JSONL + visual summaries
3. **Visual Optimization**: Enhanced color schemes and formatting
4. **Human Parsing**: Optimized for rapid human comprehension
5. **No Conflicts**: Single authoritative configuration chain
