# st-records persona-template subsystem (cold archive)

Archived 2026-05-28 from `projects/st-records` on branch `chore/retire-persona-templates`.

This is the DEAD persona-template machinery removed after a liveness audit confirmed
no live consumer. Kept here for reference/library value per the never-pure-delete rule.

## What this was
The "Academy -> Ultra Magnus" persona-upgrade-patch flow, plus the FastAPI
visualization API (Snow-Town dashboard backend).

STEP-0 verdict at removal time: the st-records FastAPI app was confirmed DEAD
(no uvicorn process, no systemd unit, no cron entry, no external HTTP consumer;
the only Next.js dashboard frontend was not running). The whole `api/` layer was
removed as a unit. The contract DB (`persona_metrics.db`) and the live contract-store
methods for outcomes / recommendations / research_signals were NOT touched — those
remain load-bearing for metroplex, sky-lynx, and research-agents.

## Contents
- `persona_upgrader.py`, `review_patch.py` — manual-only scripts (no cron/service caller)
- `persona_upgrade_patch.py` — the PersonaUpgradePatch / PersonaFieldPatch contract
- `persona_upgrade_patch.v1.json` — its JSON Schema export
- `academy_reader.py` — reads st-agent-registry personas (top-level copy + inside api/)
- `api/` — the full dead FastAPI app (activity, agents, ecosystem, nodes, pipeline, research)
