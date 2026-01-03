# ContextForge Extensible Hub Project Plan

## 1. Vision
Unified governance + automation + analytics hub orchestrating PowerShell & Python tasks, enforcing rules, emitting structured events, enabling pluggable domain extensions, and producing actionable metrics/evidence with minimal overhead.

Non-Goals (initial): Full UI dashboard, distributed clustering, complex RBAC.

## 2. Scope (Capabilities)
In-Scope: Task execution, event bus, governance validation, plugin system, scheduler (interval/cron-lite), metrics & alerting, evidence bundles, Python enrichment, secrets abstraction, health diagnostics.
Out-of-Scope early: Multi-tenant isolation, rich UI, external queue integrations.

## 3. Functional Requirements
FR1 Event emission (task_start/exit, compliance events, plugin_load, metric_emit, alert_fire).
FR2 Descriptor-driven task execution with host selection (pwsh/Windows PS).
FR3 Plugin discovery via manifest and lifecycle hooks.
FR4 CLI functions: Invoke-HubTask, Get-HubEvents, Get-HubMetrics, Register-HubPlugin, Test-HubHealth.
FR5 Python enrichment producing derived_metric events.
FR6 Metrics: latency, success_rate, rule_coverage, variety_index.
FR7 Scheduler for interval & cron subset with schedule_trigger events.
FR8 Evidence bundles on triggers (public_api_change, governance_fail).
FR9 Exit code contract (0 success,1 fail,2 warnings escalated, >90 infra errors).
FR10 Analytics flag on governance suite (-RunAnalytics).
FR11 schema_version in all events.
FR12 Plugin schema compatibility negotiation.
FR13 Governance parity event always logged.
FR14 Secret access logging (redacted) & undeclared secret denial.
FR15 Plugin hooks: onLoad,onEvent,onSchedule,onShutdown.

## 4. Non-Functional Requirements
NFR1 Append-only event storage; no destructive mutation.
NFR2 Instrumentation overhead <5% for short tasks.
NFR3 Core + plugin scan startup <3s.
NFR4 Event write failure non-fatal (unless compliance-critical).
NFR5 PSScriptAnalyzer (errors) & Ruff/Mypy (strict) clean.
NFR6 Deterministic exit codes.
NFR7 Backward-compatible schema within major version.

## 5. Architecture Layers
Core Services: EventService, ExecutionService, PluginService, SchedulerService, MetricsService, EvidenceService.
Plugins: Governance, AnalyticsBridge, Secrets, MetricsEnhancers.
Data: JSONL events, optional SQLite index, artifacts/, evidence/, cache/.
Cross-Cutting: Host Guard, Config Loader, Correlation Manager.

## 6. Core Schemas (Draft)
Event v1.0 keys: schema_version, ts, event_type, level, component, task_id?, run_id?, correlation_id?, payload, metrics?, artifacts[], host{ps_version,os}.
Plugin Manifest: id, version, capabilities[], entry, supported_schema[], dependencies[], hooks{}, config_schema_version.
Task Descriptor: id, command, host, params, capabilities_required[], secrets_required[], schedule.

## 7. Documentation Set (/docs/hub)
01-Overview, 02-Architecture, 03-Event-Schema, 04-Plugin-Spec, 05-Task-Execution, 06-Metrics-Alerts, 07-Scheduling, 08-Security-Secrets, 09-Evidence-Auditing, 10-Python-Extending, CHANGELOG-HUB.
Templates: decision log, AAR, plugin manifest, task descriptor.

## 8. Phased Roadmap
Phase 0 (Hardening, 1w): schema_version, parity stabilization, Ensure-DevModules.
Phase 1 (MVH, 2w): ExecutionService, task descriptors, minimal PluginService, governance plugin wrapper, docs 01–05.
Phase 2 (Metrics & Analytics, 2w): MetricsService, Python enrichment, coverage & variety plugins, docs 06 & Python guide.
Phase 3 (Scheduler & Evidence, 2w): SchedulerService, EvidenceService triggers, docs 07 & 09.
Phase 4 (Index & Alerts, 2w): SQLite index/compaction, alert rules, docs update.
Phase 5 (Secrets & Hardening, 2w): Secret provider plugin, policy enforcement, security docs.
Phase 6 (Extended / Optional REST): REST adapter, plugin health, advanced extensibility docs.

## 9. Workstreams
Core Engineering, Governance Integration, Analytics/Data, Dev Experience, Security & Secrets, QA/Validation, Release & Versioning.

## 10. Success Metrics
Governance runtime overhead <5%, event loss <0.01%, plugin load success >99%, new plugin onboarding <2h, coverage ≥98%, variety index warnings downward trend, parity MTTR <1d, evidence accuracy 100% spot checks.

## 11. Risks & Mitigations
Scope creep → phase gates; performance regression → baseline benchmarks; schema churn → versioning policy; plugin security → trust model + sandbox; secret leakage → strict redaction; SQLite contention → degrade to JSONL.

## 12. Governance & Decision Logging
Decision logs stored /docs/decisions (context, options, decision, impact). AAR on failures/alerts.

## 13. Initial Backlog (Epics)
Event Foundation, Execution Engine, Plugin Framework, Metrics & Analytics, Scheduler, Evidence, Secrets.
Representative stories: schema_version injection, Invoke-HubTask, plugin manifest schema, metrics emission, coverage calc, schedule parser, evidence bundler, secret_access enforcement.

## 14. Tooling & Automation
Add tasks.json (hub:governance, hub:run-task TASK_ID, hub:analytics, hub:lint). Pester suites (unit / integration / perf). Python lint / test pipeline. Pre-commit hooks (schema validation).

## 15. Exit Criteria
MVH: task descriptor executed with events + governance_parity.
Metrics phase: derived_metric events & coverage % reported.
Scheduler phase: scheduled_run events emitted.
Index & Alerts: query speedup + alert_fire events.
Secrets phase: secret_access enforced.
Final: plugin health disables failing plugin.

## 16. Versioning & Maintenance
Semantic versioning (core + schema). Deprecation: warn for 2 minors. Compatibility matrix documented.

## 17. Immediate Priorities (Next 2 Days)
1. Add schema_version & host metadata to event writer.
2. Draft plugin manifest JSON schema & example.
3. Implement Invoke-HubTask skeleton + sample task descriptor.

## 18. Follow-Up (3–7 Days)
- Plugin loader & governance plugin wrapper
- Metrics emission (latency, coverage)
- Python enrichment CLI integration

## 19. Deferred Enhancements
- REST API / UI
- OpenTelemetry exporter
- Distributed task queue
- Anomaly detection metrics

---
Generated: $(Get-Date -Format 'u')
