# Phase 1 - Agent SOPs + Personas (Shared Standard)

This file defines the **minimum, consistent** structure that Phase 1 scripts append to agent instruction files.

## Goals
- Ensure every agent has a clear **persona** (mission + constraints)
- Ensure every agent has a runnable **SOP checklist** (intake → execute → validate → handoff)
- Make updates **idempotent** using marker comments

## Markers
- Start: $markerStart
- End: $markerEnd

## Guidance
- Keep SOP items testable / observable (avoid vague language)
- Prefer checklists over prose
- Keep constraints explicit (what the agent must NOT do)
