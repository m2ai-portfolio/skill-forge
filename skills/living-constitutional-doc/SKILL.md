---
name: living-constitutional-doc
description: Generate a living team-standards document where each rule is linked to the incident that produced it and a machine-checkable eval test. Transforms informal lessons-learned into a constitutional spec an agent can reference, enforce, and extend over time. Use when the user says "living doc", "constitutional document", "team standards template", "encode our rules with incidents", "link rules to tests", "make CLAUDE.md incidents testable", or wants to formalize evolving team norms into a versioned artifact.
---

# Living Constitutional Document

Generate an evolving team-standards document structured as a three-column triad: **Rule → Incident → Eval**. Each rule explains the standard. Each incident explains why the rule exists (the specific failure that taught it). Each eval is a checkable assertion an agent can run or reference to catch violations before they ship.

## Source

Nate's Newsletter, 2026-05-16: Tibo interview — "The senior practitioner's primary artifact is an evolving constitutional doc: written rules + the incident that produced each rule + the test that would catch a violation."

## When to Use

- Starting a new project and want to encode lessons from previous work
- Team has recurring review comments that never stick
- Existing CLAUDE.md "Learned Mistakes" sections have grown large and unstructured
- Preparing a onboarding document for new contributors or agents

## Prerequisites

- At least one real incident or recurring failure pattern to seed the document
- Agreed-upon output path for the generated document
- Optional: existing CLAUDE.md or AGENTS.md to mine for implicit rules

## Phase 1: Seed Collection

Ask the user to provide raw material from one of three sources:

**Option A — Mine existing docs**
Read CLAUDE.md, AGENTS.md, and any "lessons learned" files in the project. Extract every sentence that describes a constraint, prohibition, or "always/never" pattern.

**Option B — Incident interview**
Ask: "Tell me about the last three times something went wrong in this project. What happened, what rule was violated, and how would you know if it happened again?"

**Option C — Review comment mining**
If the user has PR/MR history, collect recurring review comments. Each comment cluster = a candidate rule.

## Phase 2: Rule Extraction

For each candidate rule, extract:

```
rule_text: clear, imperative statement ("Never X", "Always Y before Z")
scope: file / function / module / system / agent-behavior
origin_incident: one-sentence description of what went wrong
incident_date: when it happened (approximate is fine)
detection_method: how a human or agent would notice a violation
```

Group rules into categories:
- **Code** — naming, structure, dependency choices
- **Operations** — deploy, infra, process management
- **Agent behavior** — what agents are / aren't allowed to do
- **Communication** — PR format, commit messages, handoffs
- **Security** — data handling, secret management, input validation

## Phase 3: Eval Writing

For each rule, generate an eval assertion in one of three forms:

### Form A — Grep pattern (machine-checkable)
```
eval_type: grep
pattern: <regex or literal string>
should_match: false   # or true
files: "**/*.ts"
description: "No hardcoded localhost URLs in TypeScript files"
```

### Form B — Structural assertion (requires a test runner)
```
eval_type: assertion
check: "all functions with >50 lines have a named constant explaining the invariant"
tooling: ruff / eslint / custom script
```

### Form C — Human judgment gate
```
eval_type: hil
question: "Does this PR touch the auth middleware without a second reviewer?"
escalate_if: yes
```

## Phase 4: Document Assembly

Generate the constitutional document in this structure:

```markdown
# Team Constitutional Document
version: <semver>
last_updated: <date>
owner: <team or person>

## How to Use This Document
- Rules are binding unless marked [ADVISORY]
- Each rule has an incident origin — read it to understand the *why*
- Evals are machine-runnable where marked [AUTO]; others are [HIL]
- To amend: add the new incident, update the rule, update the eval — in the same PR

## Rules

### [CATEGORY]

#### Rule: <rule_text>
**Scope:** <scope>
**Origin incident:** <one-line description> (<date>)
**Eval:** `<grep pattern or assertion>` [AUTO] / [HIL]

---
```

Repeat for each rule. Group by category. Sort by frequency of violation within each category (most-violated first).

## Phase 5: Maintenance Protocol

Append this block to the generated document:

```markdown
## Amendment Process

When a new incident occurs:
1. Write the rule in imperative form.
2. Write the incident origin in one sentence.
3. Write the eval (grep, assertion, or HIL).
4. Add to the relevant category section.
5. Increment the version patch number.
6. Notify the team in the PR description.

Do NOT add rules without incidents. "Best practice" rules without a real failure story rot faster than rule-incident pairs.
```

## Verification

- Every rule has a corresponding incident entry (no orphan rules)
- Every rule has at least one eval, even if it's a HIL gate
- No rule references internal agent names, product names, or hardcoded paths
- Document renders correctly as Markdown
- version field is present and follows semver

## Output

Default output path: `./CONSTITUTION.md` (project root) or `./docs/team-constitution.md`.

If CLAUDE.md already has a "Learned Mistakes" section, offer to merge the extracted rules into the constitutional doc format or keep them separate. Keeping them separate is usually better — CLAUDE.md is load-bearing for agent context injection and adding structural overhead there degrades prediction quality.
