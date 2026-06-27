---
name: corrections-to-evals
description: Pipeline for converting captured agent corrections (user_correction_submitted events) into structured eval cases — input/expected-output pairs that form a growing regression suite. Use when you have a correction log and want to turn human overrides into replayable test cases.
---

# Corrections to Evals

Turns captured agent corrections into structured eval cases — the highest-quality training and regression signal the system will ever produce. Each correction contains the original prompt, the agent's failed output, and the human's correction: exactly the triplet an eval case needs.

Works downstream of a correction-capture layer (see `agent-correction-capture` for how to instrument the capture side). The output is a `.jsonl` file of eval cases that any evaluation harness can replay.

## When to Invoke

- You have a `corrections.jsonl` or SQLite log of `user_correction_submitted` events and want to build a regression suite
- You want to verify that after a prompt change, the agent still handles past failure modes correctly
- You want to use past corrections as few-shot examples in the agent's system prompt
- You need to compute an acceptance rate from correction data
- User says "corrections to evals", "build eval cases from corrections", "convert corrections to eval", "corrections-to-evals", "/corrections-to-evals"

## Phase 1: Load and Triage Corrections

Read the correction log. Filter to corrections suitable for eval cases:

```typescript
interface UserCorrectionSubmitted {
  event_type: "user_correction_submitted";
  agent_run_id: string;
  task_id?: string;
  correction_surface: "chat" | "inline_edit" | "cli" | "hil_gate" | "async_review";
  correction_text?: string;
  original_output_ref?: string;
  severity?: "minor" | "major" | "reject";
  timestamp: string;
}
```

**Triage rules:**
- **Include**: `severity: "major"` or `"reject"` — high-signal failures
- **Include**: `correction_surface: "hil_gate"` — human stopped the agent before execution; always high-quality
- **Defer**: `severity: "minor"` — style/preference corrections; useful later but not for regression
- **Exclude**: corrections where `correction_text` is null — can't reconstruct expected output

## Phase 2: Reconstruct the Triplet

For each included correction, reconstruct the eval triplet:

| Field | Source |
|-------|--------|
| `input` | The original prompt/task that triggered the run (fetch from run log via `agent_run_id`) |
| `agent_output` | The output that was corrected (fetch via `original_output_ref` or run log) |
| `expected_output` | The human's correction (`correction_text` or the modified artifact) |

If `input` or `agent_output` can't be recovered from the run log, mark the case as `incomplete` and skip — a partial triplet produces misleading results.

```typescript
interface EvalCase {
  id: string;            // e.g. agent_run_id + "_" + task_id
  input: string;         // the original prompt/task
  agent_output: string;  // what the agent produced
  expected_output: string; // the human correction
  correction_surface: string;
  severity: string;
  captured_at: string;   // timestamp of the correction event
  tags: string[];        // e.g. ["hil_gate", "factual", "reject"]
}
```

## Phase 3: Write the Eval Case File

Append each case to a `.jsonl` file (one JSON object per line):

```
corrections-eval-cases.jsonl
```

JSONL is append-friendly — new corrections can be added without rewriting prior cases.

Example entry:
```json
{"id":"run_abc123_task_1","input":"Summarize the Q2 contract terms in 3 bullets","agent_output":"• Revenue share 20%\n• 90-day notice\n• Auto-renew on expiry","expected_output":"• Revenue share 15% (not 20%) — see §4.2\n• 60-day notice period\n• Manual renewal required","correction_surface":"chat","severity":"major","captured_at":"2026-05-28T14:22:00Z","tags":["factual","major"]}
```

## Phase 4: Replay Eval Cases

To verify the agent after a change, replay cases from the eval file:

```
For each case in corrections-eval-cases.jsonl:
1. Send `input` to the agent (same parameters as the original run)
2. Compare the output against `expected_output` using the eval rubric
3. Flag as REGRESSION if the new output contains the same error as `agent_output`
4. Flag as PASS if the new output matches or improves on `expected_output`
```

Replay stub (TypeScript):

```typescript
import { readFileSync } from "fs";

const cases = readFileSync("corrections-eval-cases.jsonl", "utf8")
  .trim()
  .split("\n")
  .map((l) => JSON.parse(l));

for (const c of cases) {
  const newOutput = await runAgent(c.input); // your agent runner
  const passed = !similarToAgentOutput(newOutput, c.agent_output);
  console.log(`[${passed ? "PASS" : "REGRESSION"}] ${c.id}`);
}
```

## Phase 5: Few-Shot Injection (Optional)

High-quality eval cases (`severity: "reject"`, `correction_surface: "hil_gate"`) can be injected into the agent's system prompt as few-shot failure examples:

```
# Known Failure Patterns — do not repeat

Example 1 (factual error):
Input: [input]
Wrong: [agent_output]
Correct: [expected_output]
```

This is the fastest path from a captured correction to a behavior change — faster than fine-tuning, faster than prompt engineering from scratch.

## Output Files

| File | Contents |
|------|----------|
| `corrections-eval-cases.jsonl` | Structured eval cases, one per line |
| `corrections-eval-report.md` | (Optional) Summary: case count, severity breakdown, surface breakdown |

Default output location: current directory unless configured otherwise.

## Verification

- [ ] Every eval case has a recoverable `input` — no partial triplets stored
- [ ] `hil_gate` corrections are included regardless of whether `severity` is explicitly set
- [ ] The eval file is append-only — new corrections added without rewriting prior cases
- [ ] At least one replay run has been executed before treating the file as a regression suite

## Source

Nate's Newsletter (natesnewsletter@substack.com), 2026-05-28:
"Agent Run Analytics Dashboard + Event Schema — a 'corrections → eval cases' prompt that turns human overrides into a growing regression suite."
Idea #7 from intake 2026-06-04. Downstream of the `user_correction_submitted` event shape defined in `agent-run-schema`.
