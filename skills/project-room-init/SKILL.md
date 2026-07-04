---
name: project-room-init
description: Scaffold a canonical 7-folder "project room" from a source directory — copies originals into a structured layout, generates a 12-field source inventory, and prepares the workspace for AI-assisted drafting. Never moves or deletes source files.
---

# Project Room Init

Turns a messy source directory into an inspectable, AI-ready workspace by building a canonical folder layout and inventory before any drafting begins. The room is the source of truth; drafts are downstream artifacts from it.

Requires Claude Code (or another agent with filesystem access). Does not work in upload-only chat interfaces.

## Trigger

Use when the user says "set up a project room", "organize my sources for drafting", "project-room-init", "prepare the room", "scaffold my sources", or points at a directory and says "I want to draft from this."

## Phase 1: Intake

Ask the user for:
1. **Source directory path** — the folder containing the raw source files (absolute path)
2. **Output room path** — where to create the project room (default: `./project-room/` in the current working directory)
3. **Project name** — one phrase used in the inventory header (e.g., "Q2 Board Report", "Vendor RFP")
4. **File types to include** — by default, include `.pdf`, `.docx`, `.doc`, `.txt`, `.md`, `.csv`, `.xlsx`, `.pptx`. Ask if they want to add or exclude types.

Confirm inputs before creating anything.

## Phase 2: Folder Scaffolding

Create the 7-folder layout under the output room path:

```
project-room/
├── 00_originals/        ← copies of source files (never moved, never deleted)
├── 01_inbox/            ← drop zone for new files that arrive mid-project
├── 02_inventory/        ← inventory.csv and audit notes
├── 03_source_summaries/ ← per-file summaries (generated in Phase 4)
├── 04_working_brief/    ← the artifact brief / project scope document
├── 05_outputs/          ← final and draft deliverables
└── 99_review/           ← items flagged for human review
```

Do not create any other top-level folders. Do not modify the source directory.

## Phase 3: Copy Originals

For each file in the source directory matching the included file types:
- Copy (do not move) to `00_originals/`
- Preserve the original filename
- Write a `provenance.txt` entry:
  ```
  <filename> | copied from: <absolute source path> | date: <YYYY-MM-DD>
  ```

If any file cannot be read (permissions, corruption), log it in `99_review/copy-errors.txt` and continue — do not abort.

## Phase 4: Generate Inventory

Create `02_inventory/inventory.csv` with one row per file. The 12-field schema:

| Field | Description |
|-------|-------------|
| `source_id` | Sequential `SRC-N` identifier |
| `filename` | Name as copied into `00_originals/` |
| `source_type` | Inferred: report, transcript, plan, deck, contract, email, other |
| `date` | Date extracted from filename or file metadata; `UNKNOWN` if not determinable |
| `owner` | Author/org if determinable from filename or content; `UNKNOWN` otherwise |
| `relevance` | `HIGH / MEDIUM / LOW` — based on filename match to project name |
| `authority_level` | `PRIMARY / SUPPORTING / BACKGROUND` — default SUPPORTING; flag `PRIMARY` only if file appears to be the authoritative source |
| `status` | `CURRENT / SUPERSEDED / UNKNOWN` — default UNKNOWN |
| `supported_claims` | Leave blank — to be filled by source summarizer |
| `limitations` | Leave blank — to be filled by source summarizer |
| `intended_use` | Leave blank — to be filled by source summarizer |
| `review_notes` | Any flag raised during copy (e.g., "possible duplicate", "date unclear") |

Populate `date`, `owner`, `relevance`, `authority_level`, and `status` from filename and any content you can read. Mark fields `UNKNOWN` rather than guessing.

## Phase 5: Duplicate Detection (lightweight)

Before closing, scan `00_originals/` for probable duplicates:
- **Exact name match**: two files with identical names (case-insensitive) from different source subdirectories
- **Probable duplicate**: files with very similar names differing only in date suffix, version number, or "FINAL" / "v2" etc.

For each probable duplicate, add a row to `99_review/duplicate-candidates.txt`:
```
PROBABLE DUPLICATE: report-q3.pdf vs report-q3-FINAL.pdf
  → Recommend: review both; keep the authoritative version as SRC-N PRIMARY
  → Action required: human decision — do NOT auto-delete
```

Do not delete, move, or rename any files. Only report.

## Phase 6: Output

After scaffolding, report:

```
## Project Room Ready

Room: <output path>
Project: <project name>
Sources copied: N files → 00_originals/
Inventory: 02_inventory/inventory.csv (N rows)
Duplicate candidates: M flagged → 99_review/duplicate-candidates.txt
Copy errors: K (if any) → 99_review/copy-errors.txt

Next steps:
1. Add your working brief to 04_working_brief/
2. Run /missing-context with the inventory + brief to find gaps before drafting
3. Run /grounded-draft once gaps are resolved
```

## Verification

A correct project-room-init:
- Source directory is unchanged (no files moved or deleted)
- `00_originals/` contains exactly the files from the source directory (matching included types)
- `provenance.txt` has one entry per copied file
- `inventory.csv` has exactly 12 columns and one data row per file
- No invented field values — `UNKNOWN` for anything genuinely indeterminate
- Duplicate candidates listed but not acted on

## Source

Extracted from Nate's Newsletter 2026-05-22 — "AI: Organize Files Before Writing" — idea #1: Project Room Builder (file-system variant).
