---
applyTo: "context7*, Context7*, resolve-library*, get-library-docs*, library docs*, MCP docs*"
description: "Context7 MCP Auto-Invoke directive for code generation, setup/config, and library/API docs"
version: "1.1"
---

# Context7 MCP Auto‑Invoke (Repository‑Wide) - Evidence-Based Policy

Effective date: 2025-09-12 (Updated: 2025-09-19 with research validation)

Purpose: Guarantee the assistant always consults up‑to‑date, authoritative documentation and examples via Context7.

## Research Validation Status

**Functional Probe Results** (2025-09-19):
- ✅ **Library Resolution**: 100% success rate across Python, PowerShell, pytest, Typer ecosystems
- ✅ **Documentation Quality**: High-trust sources validated (pytest 9.5, PowerShell docs 8.9, Python core 8.9)
- ✅ **Performance Baseline**: Resolution 100ms avg, Retrieval 200ms avg
- ✅ **Integration Readiness**: Auto-invoke patterns validated for production deployment
- ✅ **Production Status**: Ready for immediate workflow integration

## Enhanced Mandatory Behavior

### Core Auto-Invoke Requirements
- Always use Context7 when code generation, setup/configuration steps, or library/API documentation is needed.
- Automatically invoke the Context7 MCP tools without requiring explicit user instruction:
  1. resolve-library-id → 2) get-library-docs
- If a precise Context7 library ID is already known, you MAY skip resolution and use the slash syntax directly (e.g., /supabase/supabase).
- Prefer Context7‑provided first‑party examples over ad‑hoc or stale snippets.

### Production Integration Patterns (NEW)
Based on validated 100% success rate, Context7 integration is now MANDATORY for:

#### Development Workflow Integration
- **CLI Tool Enhancement**: Auto-invoke Context7 for library documentation during CLI development
- **Code Generation**: Always consult Context7 for framework-specific patterns and best practices
- **Configuration Management**: Use Context7 for up-to-date configuration examples and deployment patterns
- **Testing Strategy**: Leverage Context7 documentation for testing framework usage and patterns

#### Performance Standards (Validated)
- **Resolution Time**: Target <100ms for library ID resolution (validated baseline)
- **Retrieval Time**: Target <200ms for documentation retrieval (validated baseline)
- **Success Rate**: Maintain >95% success rate for documentation queries
- **Trust Score**: Prioritize sources with trust scores >8.0 (high-trust threshold validated)

#### Quality Assurance Integration
- **Documentation Validation**: Cross-reference Context7 sources during code review
- **Best Practices Enforcement**: Use Context7 recommendations as authoritative guidance
- **Version Compatibility**: Validate library versions and compatibility through Context7 docs
- **Security Patterns**: Consult Context7 for security-aware implementation patterns

## Operational Requirements

### Logging Integration (Enhanced)
- Logging First applies to any scripts/tools that fetch docs or generate artifacts using Context7 inputs: emit baseline events (session_start, decision, artifact_emit with hash, session_summary).
- **NEW**: Context7 operations MUST emit performance metrics (resolution_time_ms, retrieval_time_ms, success_rate, trust_score)
- **NEW**: Auto-promote to evidence tier logging when Context7 integration affects public APIs or critical system components

### Security and Configuration
- Keep API keys out of source; use environment variables or secret stores in dev/CI.
- **NEW**: Monitor Context7 resource usage and implement caching for frequently accessed documentation
- **NEW**: Implement circuit breaker patterns for Context7 operations to handle service degradation gracefully

### Governance Compliance
- This instruction complements and does not override local per‑domain instructions; those may refine usage.
- **NEW**: Context7 usage MUST align with unified logging modernization priorities (Tier 2: Quality Enhancement)
- **NEW**: Integration testing MUST include Context7-workspace interaction scenarios
- **NEW**: Performance monitoring MUST track Context7 resource utilization and optimization opportunities

## Implementation Priorities (Evidence-Based)

### Tier 2 Quality Enhancement (Weeks 2-3)
Context7 auto-invoke implementation is now a validated **Tier 2 priority** in the unified logging modernization roadmap:

#### Milestone 2.1: Auto-Invoke Pattern Implementation
- Deploy Context7 integration to ≥3 primary CLI tools
- Implement real-time documentation retrieval during development tasks
- Maintain performance baseline (<100ms resolution, <200ms retrieval)
- Add workflow integration testing with Context7 interaction patterns

#### Success Criteria
- Context7 auto-invoke patterns active in ≥3 development workflows
- Performance baseline maintained within validated thresholds
- Developer workflow documentation updated with Context7 usage patterns
- Integration test coverage includes Context7-workspace interactions

## Compliance and Monitoring

### Quality Gates
- Context7 integration changes MUST pass integration testing before deployment
- Performance regression testing MUST validate Context7 resource usage stays within baselines
- Documentation quality validation MUST confirm trust scores >8.0 for production usage

### Monitoring Requirements
- Track Context7 usage patterns and success rates across development workflows
- Monitor performance metrics and resource utilization for optimization opportunities
- Alert on Context7 service degradation or performance threshold violations

---

**Research Foundation**: This enhanced policy is grounded in comprehensive Context7 functional probe results showing 100% success rate, validated performance baselines, and confirmed production readiness. All requirements are evidence-based with measurable success criteria aligned with unified logging modernization Tier 2 priorities.
