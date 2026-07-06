---
name: open-weights-fallback-registry
description: Maintain a config registry mapping every engine-layer model in production to a vetted open-weights fallback, with a scheduled smoke-prompt check confirming each mapping still resolves — prevents vendor cost lock-in at the model layer.
---

# Open-Weights Fallback Registry

Creates and maintains a YAML registry that maps each proprietary engine-layer model in active use to a vetted open-weights alternative, with a lightweight sentinel that confirms each fallback is reachable and returns sensible output on a regular schedule.

## Trigger

Use when the user:
- Says "open weights fallback", "vendor lock-in", "model fallback registry", "what if [provider] goes down", or "/open-weights-fallback-registry"
- Is auditing their model spend for vendor concentration risk
- Wants a portability plan before committing to a new proprietary model
- Needs to verify their open-weights fallbacks still exist after a provider's model catalog update

## Phase 1: Registry Bootstrap

Ask for (or read from context):
- **List of engine-layer models currently in use** (model IDs, provider, approximate monthly call volume)
- **Provider endpoints** for each model (base URL or SDK config)
- **A representative smoke prompt** for each model class (or use a universal default: "Reply with the single word: ready")
- **Output path** for the registry file (default: `./open-weights-fallback-registry.yaml` in the current project)

If the user has not separated "steering" from "engine" models, help them classify:
- **Engine-layer**: high-volume, cost-sensitive, used for extraction, classification, summarization, formatting
- **Steering-layer**: low-volume, frontier quality, used for planning, judgment, creative work

Only engine-layer models need fallback entries. Steering-layer models are lower-volume and typically do not need the same cost-portability protection.

## Phase 2: Generate Registry File

Produce a YAML file at the specified output path:

```yaml
# open-weights-fallback-registry.yaml
# Maps proprietary engine-layer models to open-weights alternatives.
# Run the sentinel (Phase 3) weekly to verify fallback health.

registry:
  - id: entry-001
    production:
      model_id: "<proprietary-model-id>"
      provider: "<provider-name>"
      endpoint: "<base-url-or-sdk-default>"
      monthly_calls_approx: 0
    fallback:
      model_id: "<open-weights-model-id>"
      provider: "<fallback-provider-or-self-hosted>"
      endpoint: "<fallback-base-url>"
      notes: "<why this fallback was chosen>"
    smoke_prompt: "Reply with the single word: ready"
    last_verified: null
    status: unverified   # unverified | healthy | degraded | broken

sentinel:
  schedule: "weekly"
  output_path: "./open-weights-fallback-report.md"
  alert_on: ["broken", "degraded"]
```

Write one entry per production model. If the user does not know a specific open-weights fallback, mark `fallback.model_id` as `"TBD"` and note it as a gap.

## Phase 3: Smoke Verification Pass

For each entry with `status: unverified` or `status: healthy` (re-verification), run:

1. Send the `smoke_prompt` to the fallback endpoint
2. Check that a non-empty response was returned within a reasonable timeout (default 30s)
3. Update the entry: `last_verified: <today's date>`, `status: healthy` or `broken`

Report the verification results as a table:

| Entry | Production Model | Fallback Model | Status | Notes |
|-------|-----------------|----------------|--------|-------|
| entry-001 | ... | ... | healthy / broken | ... |

For any `broken` or `TBD` entries, list as **gaps** that require remediation before the registry can be considered complete.

## Phase 4: Sentinel Schedule (Optional)

If the user wants automated weekly re-verification, produce a scheduled task definition following the No Orphan Loops convention:

```yaml
# owner, sink, and kill are required by the loop convention
owner: <who reviews the output>
sink: ./open-weights-fallback-report.md
kill: escalate to owner after 3 consecutive broken findings
schedule: weekly
action: run /open-weights-fallback-registry against ./open-weights-fallback-registry.yaml
```

Note: the scheduled task must declare `owner`, `sink`, and `kill` with real values before it can be scheduled. The template above is a starting point; fill in the owner before wiring it to a cron.

## Verification

The registry is sound when:
- [ ] Every production engine-layer model in active use has an entry
- [ ] No entry has `fallback.model_id: TBD` (all gaps have been resolved or explicitly accepted as risks)
- [ ] The smoke verification pass has run at least once and all entries are `healthy`
- [ ] The `sentinel.output_path` directory exists and is writable
- [ ] `owner`, `sink`, and `kill` are filled in if a scheduled sentinel is configured

## Source

Nate's Newsletter "Beyond Model Routing" (2026-07-05): "open-weights where you can so no vendor owns your costs." Extends the pattern established by the `token-burn-auditor` (session-level cost visibility) to the model-selection layer (portfolio-level vendor lock-in).
