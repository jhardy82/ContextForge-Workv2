# Conflict Resolution (v1.3.0)

Order of precedence (highest → lowest):
1. Hotfix override (timeboxed)
2. Command-line switches
3. Environment variables
4. thresholds.local.yaml
5. thresholds.yaml (base)
6. copilot-instructions.md rules
7. conflict_resolution.md clarifications
8. Archived legacy documents (reference only)

Resolution Algorithm:
- First applicable layer wins; lower layers ignored for that key.
- Log an event "precedence_override" when a higher layer masks a lower-layer value.
- Experimental rules must not override Mandatory rules; if detected, demote experimental rule (log event).

Tie Handling:
- If two same-layer sources define the same key (e.g., duplicate in thresholds.local.yaml), the later parsed wins and a warning event "duplicate_key" is emitted.

Escalation:
- On 3+ duplicate_key warnings in a single run, emit governance alert.

Experimental Rule Expiry:
- At expiry_date + grace_days, rule auto-demoted to advisory; emit event "experimental_auto_demote".
