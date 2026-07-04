---
name: behavioral-contract-extractor
description: Walk a codebase and draft a behavioral contract document — the invariants, allowed states, forbidden states, and input/output guarantees that define what the system is "allowed to mean." Produces a machine-readable + human-readable contract that feeds into automated adversarial review tools, specification validators, or security audits. Use when the user says "behavioral contract", "extract invariants", "what is this system allowed to do", "define system contracts", "spec the invariants", or needs to make implicit system behavior explicit before an automated review.
---

# Behavioral Contract Extractor

Walks a codebase and drafts the behavioral contract that should govern it — the invariants, allowed states, forbidden states, and boundary guarantees that define what the system is *allowed to mean*. This is the upstream document that adversarial review tools, fuzz harnesses, and formal verification tools need in order to distinguish a bug from a feature.

The core insight: a vulnerability-research tool can only find bugs relative to a specification of correct behavior. A codebase without an explicit behavioral contract is one where "bug" and "feature" are indistinguishable to an automated scanner.

## Trigger

Use when the user says "behavioral contract", "extract invariants", "what is this code allowed to do", "define system contracts", "spec the invariants", "document what this system guarantees", or wants to make implicit codebase behavior explicit before running security or adversarial tooling.

## Prerequisites

- A codebase or module directory to analyze
- Optional: existing documentation, API specs, or README files
- Optional: known failure cases or historical bugs to anchor the contract

## Phase 1: Intake

Ask the user for:
1. **Target path** — directory or specific module(s) to analyze
2. **System description** — one sentence: what does this system do? (e.g., "payment processing pipeline", "user authentication service", "data transformation worker")
3. **Known invariants** (optional) — anything the user already knows must always be true

If the user can't describe the system in one sentence, the contract extraction will surface that ambiguity — which is itself valuable.

## Phase 2: Boundary Mapping

Identify every entry point and exit point of the system:

### Entry Points (inputs the system accepts)
For each public function, route handler, CLI entrypoint, or message consumer:
- Name and location (`file:function`)
- Input parameters and types
- Preconditions (what must be true about inputs)
- Who calls it (internal vs external callers)

### Exit Points (outputs the system produces)
For each return value, response, side effect, or event emission:
- Output type and shape
- Postconditions (what is guaranteed about the output)
- Side effects (database writes, external API calls, file modifications)

Format as a table:

```markdown
| Entry Point | Inputs | Preconditions | Exit Point | Postconditions | Side Effects |
|-------------|--------|---------------|------------|----------------|--------------|
| `POST /payments` | `{amount: number, userId: string}` | amount > 0, userId valid | `PaymentResult` | idempotent, exactly-once | writes to `payments` table |
```

## Phase 3: State Space Analysis

Identify the system's states and the transitions between them:

### Allowed States
List every distinct state the system or its core entities can be in:
- State name
- Description
- How the system enters this state
- Which operations are valid in this state

### Forbidden States
List states that must never occur:
- State name
- Why it must not occur
- What invariant would be violated

### Valid Transitions
Which state transitions are permitted:

```
State A → State B: allowed when <condition>
State A → State C: forbidden (would violate <invariant>)
```

If the codebase uses explicit state machines (enums, status fields, FSMs), extract directly. If state is implicit, infer from conditionals and guards.

## Phase 4: Invariant Extraction

Walk the source code and extract invariants — conditions that must be true at all times, or at specific points in execution.

### Global Invariants (always true)
Conditions that hold across all operations:
- "User IDs are always non-empty strings"
- "Account balance is never negative after any committed transaction"
- "No external API is called without a timeout"

### Pre/Post Invariants (per function)
For each significant function:
```
FUNCTION: processPayment(amount, userId)
  PRE:  amount > 0
  PRE:  userId exists in user store
  POST: payment record written to DB
  POST: user balance reduced by amount
  POST: event emitted to billing stream
  FORBIDDEN: partial write (payment written but balance not reduced)
```

### Data Invariants (per data type/schema)
For each significant data structure:
```
TYPE: Order
  INVARIANT: status ∈ {pending, confirmed, shipped, cancelled}
  INVARIANT: total_cents > 0
  INVARIANT: items is non-empty list
  INVARIANT: cancelled_at IS NULL when status ≠ 'cancelled'
  FORBIDDEN: status = 'shipped' when shipped_at IS NULL
```

## Phase 5: Boundary Violation Catalog

List the conditions that would constitute a contract violation — these are the inputs that an adversarial tool should try:

```markdown
## Boundary Violations to Test

### Input Violations
- `amount = 0` → should reject, not silently process
- `amount = -1` → should reject with specific error
- `userId = ""` → should reject before any DB write
- `userId = null` → should not trigger NullPointerException internally

### State Violations
- Call `confirmOrder` when order is already `cancelled` → should reject, not double-confirm
- Call `shipOrder` before `confirmOrder` → invalid transition, must be rejected

### Concurrency Violations
- Two concurrent calls to `debitAccount(userId, 100)` → balance must not go negative
- Two calls to `createUser(sameEmail)` → exactly one should succeed
```

## Phase 6: Draft Contract Document

Produce the behavioral contract as a structured markdown document:

```markdown
# Behavioral Contract: <System Name>
**Version**: 1.0 (extracted <date>)
**Source**: <path>
**Description**: <one-sentence system description>

---

## 1. System Boundaries

### Inputs This System Accepts
<boundary table from Phase 2>

### Outputs This System Produces
<exit points from Phase 2>

---

## 2. State Space

### Allowed States
<state list>

### Forbidden States
<forbidden state list>

### Valid Transitions
<transition table>

---

## 3. Invariants

### Global Invariants
<list>

### Per-Function Contracts
<pre/post per function>

### Data Invariants
<per type>

---

## 4. Boundary Violations (Adversarial Test Cases)
<violation catalog>

---

## 5. Ambiguities and Open Questions

List anything the code implies but does not make explicit — these are the gaps where bugs hide:

- [ ] Is `amount = 0` a valid no-op or an error? Code does not specify.
- [ ] What happens if the billing event fails after the DB write? Code has no rollback.
- [ ] Is `userId` validated against active users only, or all users including deleted?
```

## Phase 7: Machine-Readable Export (Optional)

If the user wants a format consumable by spec validators or fuzz harnesses, produce a JSON schema:

```json
{
  "system": "<name>",
  "version": "1.0",
  "entry_points": [
    {
      "id": "processPayment",
      "preconditions": ["amount > 0", "userId is non-empty"],
      "postconditions": ["payment record exists", "balance decremented"],
      "forbidden_states": ["partial write"]
    }
  ],
  "global_invariants": ["no external API call without timeout"],
  "data_contracts": {
    "Order": {
      "status": {"enum": ["pending", "confirmed", "shipped", "cancelled"]}
    }
  }
}
```

## Verification

The contract is complete when:
1. Every public entry point has documented preconditions and postconditions
2. Every entity with a status/state field has an explicit state machine
3. The ambiguities section has at least 3 entries (if none exist, the analysis was too shallow)
4. The boundary violations section has at least 5 adversarial test cases

## Source Attribution

Extracted from Nate Kadlac's newsletter (2026-05-08): "271 bugs found in Firefox, zero written by a human attacker." The newsletter's highest-leverage insight: humans hold a new role — defining what the system is *allowed to mean* — while machines verify and attack. This skill operationalizes that human role as a concrete artifact: a behavioral contract that makes implicit system behavior explicit and machine-readable.
