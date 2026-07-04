---
name: codebase-legibility-auditor
description: Audit a codebase for machine-legibility readiness — scores how well each module can be parsed, analyzed, and reviewed by automated adversarial scanning tools. Produces a legibility-readiness score and a ranked list of opaque modules. Use when the user says "legibility audit", "machine-legibility check", "adversarial review readiness", "codebase legibility score", "is my code ready for automated security scanning", or wants to know which parts of a codebase would defeat automated vulnerability-research tools.
---

# Codebase Legibility Auditor

Scores a codebase for *machine legibility* — not human readability. As automated adversarial review tools (purpose-built vulnerability-research models) become standard, code that is structurally opaque to machines creates a security blind spot. This skill surfaces the modules most likely to be skipped or misanalyzed by automated scanners, so you can prioritize them for refactoring before the tools that would protect them run out of context.

## Trigger

Use when the user says "legibility audit", "machine-legibility check", "adversarial review readiness", "codebase legibility score", "how legible is my code to automated scanners", or wants to know which modules would defeat automated vulnerability tools.

## Prerequisites

- A codebase directory to analyze (local path or git repo)
- Read access to source files

## Phase 1: Intake

Ask the user for:
1. **Target path** — the directory or repo to analyze
2. **Language(s)** — primary language(s) in the codebase
3. **Scope** — full repo, specific module, or changed files only

If the user provides a git diff or PR number instead of a directory, focus only on the changed files.

## Phase 2: Module Inventory

Walk the target directory and build a module list. For each module (file or logical grouping):

```bash
# List all source files by language
find <path> -name "*.ts" -o -name "*.py" -o -name "*.js" -o -name "*.go" | sort
```

For each file, record:
- File path and line count
- Approximate function/class count (via grep for `def `, `function `, `class `)
- Whether docstrings or inline comments exist (grep for `"""`, `/**`, `//`)

## Phase 3: Legibility Scoring

Score each module across 5 dimensions (1-5 each):

### D1: Naming Clarity (1-5)
Does the code use names that convey intent without external context?

| Score | Criteria |
|-------|----------|
| 1 | Single-letter variables, `tmp`, `data`, `x`, `foo` as production names |
| 2 | Abbreviated names requiring domain knowledge (`accrec`, `pdRt`, `usr_mgr_v2`) |
| 3 | Descriptive but generic (`manager`, `handler`, `processor`) |
| 4 | Intent-clear names (`invoicePaymentHandler`, `retryWithBackoff`) |
| 5 | Names that convey invariants and preconditions (`validatedUserEmail`, `idempotentEventPublisher`) |

### D2: Control Flow Linearization (1-5)
Can a tool follow the execution path without resolving deep indirection?

| Score | Criteria |
|-------|----------|
| 1 | 5+ levels of nesting, dynamic dispatch everywhere, heavy metaprogramming |
| 2 | 4 levels nesting or 3+ layers of decorator/middleware wrapping |
| 3 | 3 levels nesting, some dynamic dispatch |
| 4 | 2 levels max nesting, predictable dispatch |
| 5 | Linear flow, no dynamic dispatch, functions < 30 lines |

### D3: Implicit State Visibility (1-5)
Is mutable state explicit and traceable, or hidden in closures/globals?

| Score | Criteria |
|-------|----------|
| 1 | Global mutable state, module-level singletons, thread-locals used as implicit channels |
| 2 | Class-level state mutated from multiple methods without coordination |
| 3 | State isolated to class but mutation paths are non-obvious |
| 4 | State explicit, mutation gated through clear methods |
| 5 | Immutable-first, all state changes visible at the call site |

### D4: Dependency Explicitness (1-5)
Are all inputs and side effects declared at the function boundary?

| Score | Criteria |
|-------|----------|
| 1 | Functions reach into globals, os.environ, or module-level config mid-execution |
| 2 | Side effects hidden in called functions with no indication at call site |
| 3 | Most dependencies injected but some implicit |
| 4 | Dependencies injected via parameters or constructor |
| 5 | Full dependency injection, pure functions preferred, side effects at boundary |

### D5: Error Surface Clarity (1-5)
Is the error handling explicit and traceable?

| Score | Criteria |
|-------|----------|
| 1 | Bare `except`, `catch (e) {}`, errors silently swallowed |
| 2 | Logged but not re-raised; callers assume success |
| 3 | Re-raised with some loss of context |
| 4 | Typed exceptions or result types, callers handle explicitly |
| 5 | Error types declared in signatures, exhaustive handling, no silent paths |

## Phase 4: Module Scorecard

For each module, compute:

```
Legibility Score = (D1 + D2 + D3 + D4 + D5) / 25 * 100
```

Classify:
- **80-100**: Machine-legible — automated scanners can analyze effectively
- **60-79**: Partially legible — scanners will miss some paths
- **40-59**: Opaque — automated tools will produce false negatives
- **0-39**: Blind spot — effectively unanalyzable by current adversarial review tools

## Phase 5: Report

Output a ranked report, worst-first:

```markdown
# Codebase Legibility Audit
**Target**: <path>
**Date**: <date>
**Files analyzed**: <N>

## Summary

Overall legibility score: <X>/100
- Machine-legible (80+): <N> modules
- Partially legible (60-79): <N> modules
- Opaque (40-59): <N> modules
- Blind spots (<40): <N> modules

## Blind Spots — Prioritize First

| Module | Score | Worst Dimension | Primary Issue |
|--------|-------|-----------------|---------------|
| <path> | <N>   | D2 (Control Flow) | 6+ nesting levels, dynamic dispatch |
| ...    | ...   | ...             | ...           |

## Top 5 Quick Wins

For each, one targeted fix that would raise legibility by 10+ points:

1. **<module>**: Extract inline lambdas to named functions → D2 improves from 2→4
2. ...

## Recommended Refactor Order

Prioritize blind spots that touch:
1. Authentication and authorization paths
2. Data ingestion and validation boundaries
3. External API call sites
4. Error handling and retry logic
```

## Phase 6: Action Checklist

Produce a concrete per-module checklist for the 3 lowest-scoring modules:

```markdown
## <module-name> — Legibility Remediation

- [ ] Rename <N> single-letter variables (D1)
- [ ] Extract nested conditionals into named predicate functions (D2)
- [ ] Move config reads to module boundary; pass as parameters (D4)
- [ ] Replace bare except with typed exception handling (D5)
```

## Verification

The audit is complete when:
1. Every source file has a score
2. All blind spots have at least one "quick win" remediation
3. The recommended refactor order prioritizes security-critical paths

## Source Attribution

Extracted from Nate Kadlac's newsletter (2026-05-08): "271 bugs found in Firefox, zero written by a human attacker." The Mythos experiment (271 bugs vs 22 from a general-purpose predecessor) demonstrated that code legibility is a security property — machines cannot find vulnerabilities in code they cannot parse. This skill operationalizes the "Prompt #1" from that issue as a structured audit framework.
