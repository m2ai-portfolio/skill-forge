---
name: agentic-os-layer-model
description: Map any agentic OS to a 5-layer mental model (Identity → Rules/Hooks → Skills → Agents → Tools/MCPs/CLIs), assess each layer's rot rate, and generate a rot file — a maintenance artifact that tracks when each layer was last updated and when it needs attention. Use when building, auditing, or maintaining an AI operating system, or when saying "my agent system is going stale", "what layers does my AI OS need", "how do I structure my agentic setup", "my skills are out of date", "design my AI OS", "what is a soul file".
---

# Agentic OS Layer Model

Produces a structured map of any agentic OS across five layers with rot rate assessments and a rot file — the maintenance artifact most builders never create. Works for personal setups, business setups, or domain-specific command centers (one per domain).

## Trigger

Use when:
- Starting a new agentic OS from scratch and wanting a blueprint
- An existing AI system is drifting or going stale and you need to know which layer to fix first
- You want to audit what you have against what you need
- You're explaining an AI OS to someone new and need a clear mental model
- You want to build a rot file for long-term maintenance

Do NOT use for:
- Optimizing existing skills — use `goal-os-optimize` for that
- Designing agent orchestration patterns — use `dynamic-workflow-pattern-selector` for that
- Building a specific agent from scratch — use `agentic-harness-designer` for that

## The 5 Layers

Think of the layers like the Earth: the core (identity) is stable and rarely touched; the surface (tools) is subject to fast-moving weather. Each layer sits on the one below it. Break the inner layers and the outer ones fail.

### Layer 1 — Identity (Soul File)

**What it is:** The agent's personality, working style, and pointer index. A short file (50–100 lines max) that defines who the system is and where its rules, skills, and references live.

**Common form:** `CLAUDE.md`, `agents.md`, or `soul.md` depending on the agent framework.

**Pattern — pointer layer:** Rather than embedding all rules and skills directly in the identity file, reference them by path. The identity file becomes a lean index: "when doing X, see rules/X.md." This keeps the boot context small and the references composable.

**Rot rate:** Slowest. High upfront cost; low maintenance cost. Expect minor updates every 30–90 days, not weekly.

**Staleness signals:**
- Identity references files that no longer exist
- Personality instructions contradict current rules files
- The file has grown beyond 200 lines (pointer rot — embed creep)

---

### Layer 2 — Rules and Hooks

**What it is:** Guardrails and deterministic event handlers.

- **Rules:** Strong suggestions — things the agent should or should not do in specific scenarios. Written as policy; enforced by the model.
- **Hooks:** Deterministic code that fires on specific events (PreToolUse, PostToolUse, SessionStart, Stop). The only deterministic parts of an agentic OS.

**When they emerge:** Rules and hooks should NOT be designed upfront. They emerge from real usage failures. When the agent does something wrong repeatedly, that is the signal to write a rule or hook. Premature rules create noise.

**Rot rate:** Slow-to-moderate. Rules that describe desired behaviors become stale when the underlying workflow changes. Hooks tied to external tools rot when those tools change their interface.

**Staleness signals:**
- Rules reference workflows or files that were retired
- Hooks fire on tool names that have been renamed or removed
- Rules contradict each other (policy drift)

---

### Layer 3 — Skills

**What it is:** Repeatable workflows with human-in-the-loop elements. A skill is a named, documented procedure for a task that happens 5–15 times in slightly different ways.

**Two types:**
- **Process-oriented skills:** Structured procedures with judgment points and HIL gates. Examples: research workflow, content review, planning session.
- **Functional skills:** Connect to an external API or tool with little nuance. Examples: pull the latest meeting transcript from a transcription service, sync a calendar.

**Rot rate:** Fastest of all five layers. Expect weekly updates for active skills. Rot sources: smarter models need less instruction to achieve the same result; provider APIs change; personal workflows evolve.

**Expert tip:** Run `/goal optimize [skill name] according to best practices as of today` on a weekly cadence to keep active skills current without manual review. Keep a log of what changed.

**When a skill has "graduated" to an agent:** When a set of skills collectively represents a distinct role that runs on a regular cadence without you triggering each step, crystallize them into an agent.

**Staleness signals:**
- Skill references a model by name that has been deprecated or renamed
- Skill has a high rate of mid-run corrections (the procedure no longer matches your workflow)
- Two skills in your library do the same thing with slight wording differences (skill drift)

---

### Layer 4 — Agents

**What it is:** Crystallized roles. An agent is an identity (Layer 1) + rules/hooks (Layer 2) + skills (Layer 3) bundled into a persistent entity with its own cadence and area of responsibility. Agents are adjacent to roles; skills are adjacent to verbs.

**When to promote to an agent:** When a skill cluster has accumulated enough responsibility that it makes more sense to hire a role than to keep running individual skills manually.

**Rot rate:** Moderate. Agents rot when their role definition drifts from their actual task load, or when the skills they rely on update without the agent definition updating.

**Staleness signals:**
- Agent's `agents.md` or system prompt references skills that no longer exist
- The agent's role overlaps with another agent (responsibility drift)
- The agent is never invoked — its responsibilities were absorbed elsewhere

---

### Layer 5 — Tools, MCPs, and CLIs

**What it is:** External integrations. REST APIs, MCP servers, CLI tools. These give the system its reach: reading files, querying databases, running code, browsing the web, calling external services.

**Rot rate:** Varies entirely by provider. A CLI tool maintained by a major vendor may be stable for years. An MCP server from a startup may change weekly.

**Staleness signals:**
- Tool calls return 404 or auth errors (endpoint changed)
- An MCP server that used to be available is no longer listed in the registry
- A CLI tool's flags changed and old invocations fail silently

---

## Rot Rate Summary

| Layer | Rot Rate | Update Cadence |
|-------|----------|----------------|
| 1 — Identity | Very slow | Every 30–90 days |
| 2 — Rules & Hooks | Slow–moderate | When failures occur; quarterly sweep |
| 3 — Skills | Fast | Weekly for active skills |
| 4 — Agents | Moderate | When role or skill set changes |
| 5 — Tools/MCPs/CLIs | Provider-dependent | When provider releases updates |

---

## The Rot File

The rot file is the artifact most builders never create. It is a simple markdown file (one per OS or domain command center) that tracks expiration state across all five layers.

**Create it at:** `./<your-os-name>-rot.md` or `./rot.md` in your agent's config directory.

**Template:**

```markdown
# [OS Name] Rot File
Last audited: YYYY-MM-DD

## Layer 1 — Identity
- File: [path]
- Last updated: YYYY-MM-DD
- Review trigger: Next time identity file grows past 200 lines, or a rules/skills file it points to is removed
- Status: GREEN / YELLOW / RED

## Layer 2 — Rules and Hooks
- Rules files: [list]
- Hooks: [list with event types]
- Last updated: YYYY-MM-DD
- Review trigger: Any new recurring failure mode from the agent
- Status: GREEN / YELLOW / RED

## Layer 3 — Skills
- Active skills: [list]
- Last optimized: YYYY-MM-DD (per skill)
- Stale threshold: 30 days without a run = candidate for archive
- Status: GREEN / YELLOW / RED

## Layer 4 — Agents
- Agents: [list with role descriptions]
- Last role review: YYYY-MM-DD
- Status: GREEN / YELLOW / RED

## Layer 5 — Tools and MCPs
- Tools: [list]
- Last checked: YYYY-MM-DD
- Review trigger: Any auth error or unexpected behavior in a tool call
- Status: GREEN / YELLOW / RED
```

Set each layer to RED when it has known staleness issues, YELLOW when it is due for review, GREEN when recently audited.

---

## Domain Isolation

Build one OS per domain rather than one OS for everything. Each domain (personal, business, health, specific client project) gets its own command center with its own five layers. Benefits:
- Smaller, more focused identity files
- Rules don't bleed across domains
- Skills optimized for domain-specific workflows
- Cleaner rot tracking (domain X is GREEN; domain Y is RED)

Domains that share infrastructure (same tools, same hooks) can reference shared layers by pointer from their individual identity files.

---

## Audit Protocol

When asked to audit an existing agentic OS:

1. **List what exists** — ask the user to describe or provide their current setup: what CLAUDE.md/soul file looks like, which rules files exist, which skills are active, which agents (if any) are running, which tools/MCPs are wired in.

2. **Map to the 5 layers** — assign each piece to its layer. Flag anything that doesn't fit cleanly (it may indicate a layering violation).

3. **Assess rot per layer** — for each layer, ask: "When was this last updated? Has anything upstream of it changed?" Assign GREEN/YELLOW/RED.

4. **Generate a rot file** — produce the rot file template filled in with the actual current state.

5. **Prioritize** — red layers first; skills nearly always need attention; identity rarely does.

---

## Source Attribution

Technique: 5-Layer Agentic OS Mental Model with Rot Rates
Source: Mark Kashef YouTube
URL: https://www.youtube.com/watch?v=YjkteijEyzQ
Published: 2026-06-30
Title: "Master All 5 Layers of Every Agentic OS"
