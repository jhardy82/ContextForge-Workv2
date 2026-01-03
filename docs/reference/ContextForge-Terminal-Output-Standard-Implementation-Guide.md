# ContextForge Terminal Output Standard - Implementation Guide

**Version**: 1.0.0
**Date**: September 29, 2025
**Status**: Production Ready
**Authority**: Based on proven patterns from core tool compliance validation

## Overview

This guide documents the proven implementation patterns for achieving ContextForge Terminal Output Standard compliance. After systematic testing of 4 core tools, we have identified two distinct patterns that ensure clean Rich console output with zero JSON pollution.

## Executive Summary

**Implementation Results**: 4/4 core tools now compliant
- ✅ `docs_coherence.py` - Pattern A applied
- ✅ `cf_constitutional_quality_gates.py` - Pattern B (already compliant)
- ✅ `pytest_visual_enhanced.py` - Pattern B (already compliant)
- ✅ `python/run_rich_harness.py` - Pattern B (already compliant)

## Two Proven Compliance Patterns

### Pattern A: Environment Variable Coordination
**For tools using ulog() structured logging**

#### When to Use
- Tool uses `ulog()` function for structured logging
- Console output shows JSON pollution mixed with Rich formatting
- Tool needs to maintain structured logging capability while providing clean console output

#### Implementation Steps
1. **Identify ulog() function** in the tool
2. **Add environment variable coordination** to suppress JSON output when Rich console is active
3. **Test with environment variables** to verify clean output

#### Code Pattern
```python
def ulog(
    action: str,
    target: str | None = None,
    result: str = "success",
    severity: str = "INFO",
    **kwargs,
):
    import json
    import os

    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "action": action,
        "target": target,
        "result": result,
        "severity": severity,
        "ok": result == "success",
        **kwargs,
    }

    # Environment variable coordination for clean Rich console output
    # Suppress JSON output when UNIFIED_LOG_SUPPRESS_JSON=true (for Rich console compatibility)
    if not (os.getenv("UNIFIED_LOG_SUPPRESS_JSON", "").lower() == "true"):
        print(json.dumps(record))
```

#### Testing Command
```powershell
$env:UNIFIED_LOG_SUPPRESS_JSON="true"; $env:UNIFIED_LOG_RICH_MIRROR="0"; python tool_name.py [args]
```

#### Success Criteria
- Clean Rich console output with progress bars, tables, and colored text
- Zero JSON pollution in terminal
- Tool functionality preserved
- Structured logging available when environment variables not set

#### Applied To
- ✅ `docs_coherence.py` - SUCCESS

### Pattern B: Rich-Only Architecture
**For tools already using Rich console exclusively**

#### When to Use
- Tool already uses Rich console for all user-facing output
- No JSON pollution or mixed output streams present
- Clean, formatted console output already achieved

#### Implementation Steps
1. **Test current output** to confirm clean Rich formatting
2. **Verify no JSON pollution** in console output
3. **Mark as compliant** - no modifications needed

#### Characteristics
- Uses `console.print()`, Rich panels, tables, and progress bars
- Structured data saved to files, not printed to console
- Clean separation between user interface and data persistence
- Optional logging configured but not emitting to console

#### Success Criteria
- Beautiful Rich console output with proper formatting
- Zero JSON or unformatted text pollution
- Structured information displayed in organized panels and tables
- Progress indicators for long-running operations

#### Applied To
- ✅ `cf_constitutional_quality_gates.py` - REFERENCE IMPLEMENTATION
- ✅ `pytest_visual_enhanced.py` - Already compliant
- ✅ `python/run_rich_harness.py` - Already compliant

## Reference Implementation

**`cf_constitutional_quality_gates.py`** serves as the gold standard implementation featuring:

### Exemplary Features
- **Multi-panel Rich display** with executive summary, analysis tables, and recommendations
- **Color-coded status indicators** (green/yellow/red based on thresholds)
- **Progress bars with spinners** for multi-phase operations
- **Structured evidence preservation** (data goes to files, not console)
- **Clean error handling** with proper exit codes
- **Zero console pollution** - all user output through Rich console

### Output Structure
1. **Progress Phases**: Multi-step progress bars with contextual status
2. **Executive Summary**: Key metrics table with color-coded values
3. **Detailed Analysis**: Comprehensive results in structured tables
4. **Critical Issues**: Tree-structured problem identification
5. **Recommendations**: Numbered action items for improvement
6. **Evidence Summary**: Validation status and artifact references
7. **Final Status**: Clear success/failure indication with exit codes

## Systematic Testing Protocol

### Pre-Implementation Assessment
1. **Architecture Analysis**: Identify logging pattern (ulog vs Rich-only)
2. **Current Output Test**: Run tool to assess existing console output
3. **Pattern Classification**: Determine which compliance pattern applies
4. **Baseline Documentation**: Record current behavior and issues

### Implementation Validation
1. **Apply Appropriate Pattern**: Use Pattern A or confirm Pattern B compliance
2. **Environment Variable Testing**: Verify clean output with coordination flags
3. **Functionality Verification**: Ensure all tool features still work correctly
4. **Edge Case Testing**: Test error conditions and unusual inputs
5. **Documentation Update**: Record compliance status and any modifications

### Success Validation Checklist
- [ ] Clean Rich console output (no JSON pollution)
- [ ] Proper color coding and formatting preserved
- [ ] Progress indicators working for long operations
- [ ] Structured data properly separated (files vs console)
- [ ] Error handling maintains clean output
- [ ] Exit codes appropriate for success/failure states
- [ ] Environment variable coordination working (Pattern A only)

## Rollout Guidelines

### Phase 1: Core Tools (COMPLETE)
- [x] High-impact user-facing tools
- [x] Development and testing harnesses
- [x] Quality and compliance validation tools

### Phase 2: Extended Ecosystem (PENDING)
- [ ] Inventory remaining tools with terminal output
- [ ] Categorize by architecture pattern
- [ ] Apply systematic testing protocol
- [ ] Document compliance status and modifications

### Phase 3: Integration and Validation
- [ ] Verify ecosystem-wide compliance
- [ ] Update development guidelines
- [ ] Create automated compliance testing
- [ ] Establish maintenance procedures

## Troubleshooting Guide

### Common Issues

**Issue**: JSON still appearing in console output
**Solution**: Verify environment variables are set correctly and ulog() modification applied

**Issue**: Rich formatting broken after modification
**Solution**: Check that Rich console initialization is preserved and not conflicting with logging

**Issue**: Tool functionality degraded
**Solution**: Ensure structured logging logic is only suppressed for console, not disabled entirely

### Diagnostic Commands

```powershell
# Test Pattern A compliance
$env:UNIFIED_LOG_SUPPRESS_JSON="true"; python tool_name.py [args]

# Test Pattern B compliance
python tool_name.py [args]

# Verify structured logging still available
python tool_name.py [args]  # Without environment variables
```

## Maintenance and Updates

### Version Control
- Document all modifications with clear commit messages
- Maintain separate branches for testing compliance changes
- Tag releases after compliance validation

### Continuous Validation
- Include terminal output tests in CI/CD pipelines
- Regular regression testing of compliance patterns
- Monitor for new tools requiring compliance implementation

### Documentation Lifecycle
- Update this guide when new patterns are discovered
- Maintain examples and code snippets as tools evolve
- Track compliance status across the ecosystem

---

**Implementation Status**: 4/4 core tools compliant
**Next Phase**: Extended ecosystem rollout
**Contacts**: ContextForge development team
**Last Updated**: September 29, 2025
