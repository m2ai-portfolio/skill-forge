#!/usr/bin/env python3
"""Haiku-powered review gate for automated skill PRs.

Reviews the skills added/modified in a forge/* pull request and decides whether
the PR is safe to auto-merge. The bar is deliberately narrow: structural
validity of the skill, no leaked secrets, no obvious garbage. Anything the
reviewer is unsure about is left for a human (decision = "request_changes").

Outputs (consumed by the workflow):
  - writes a Markdown review to review_body.md
  - sets `decision=approve|request_changes` on $GITHUB_OUTPUT

Required env:
  ANTHROPIC_API_KEY   Anthropic API key (repo secret)
  BASE_REF            base branch name, e.g. "main"
  GITHUB_OUTPUT       path GitHub Actions exposes for step outputs
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import anthropic

# Haiku 4.5 — verified via the claude-api reference. Do not append a date suffix.
MODEL = "claude-haiku-4-5"

# Only files under these prefixes are considered skill content worth reviewing.
SKILL_PREFIXES = ("skills/",)

# Cap how much skill text we send so a huge PR can't blow the token budget.
MAX_CONTENT_CHARS = 50_000

# Obvious secret shapes. A hit here is an automatic hold, independent of Haiku —
# defense in depth alongside the workspace gitleaks layers.
SECRET_PATTERNS = [
    r"sk-ant-[A-Za-z0-9_\-]{20,}",          # Anthropic
    r"sk-[A-Za-z0-9]{32,}",                  # OpenAI-style
    r"ghp_[A-Za-z0-9]{36}",                  # GitHub PAT
    r"github_pat_[A-Za-z0-9_]{50,}",         # GitHub fine-grained PAT
    r"AKIA[0-9A-Z]{16}",                     # AWS access key id
    r"AIza[0-9A-Za-z\-_]{35}",               # Google API key
    r"xox[baprs]-[A-Za-z0-9-]{10,}",         # Slack
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
]

REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {"type": "string", "enum": ["approve", "request_changes"]},
        "summary": {"type": "string"},
        "blocking_issues": {"type": "array", "items": {"type": "string"}},
        "secrets_found": {"type": "boolean"},
    },
    "required": ["decision", "summary", "blocking_issues", "secrets_found"],
    "additionalProperties": False,
}

SYSTEM = """You are an automated reviewer for a public skills library (skill-forge).
Each pull request adds or edits one or more skills under skills/<name>/.

Approve ONLY when ALL of these hold:
- Every added skill has a SKILL.md with non-empty YAML frontmatter containing at
  least `name` and `description`.
- The skill content is coherent and non-empty (not a stub, not placeholder text,
  not obviously truncated or corrupted).
- No secrets, API keys, tokens, private keys, or credentials appear anywhere.
- No personal/client-identifying data that does not belong in a public repo.

If anything is missing, malformed, ambiguous, or you are unsure, choose
"request_changes" and explain why. A human will handle those. Be strict: this
auto-merges to a public repository.

Return your verdict via the structured output schema. `blocking_issues` must be
empty when decision is "approve"."""


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def changed_skill_files(base_ref: str) -> list[str]:
    """Added/modified files under skills/ between base and HEAD."""
    run(["git", "fetch", "--depth=1", "origin", base_ref])
    diff = run(["git", "diff", "--name-status", f"origin/{base_ref}...HEAD"])
    files: list[str] = []
    for line in diff.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, path = parts[0], parts[-1]
        if status.startswith("D"):  # deletions carry no content to review
            continue
        if path.startswith(SKILL_PREFIXES):
            files.append(path)
    return files


def gather_content(files: list[str]) -> str:
    chunks: list[str] = []
    total = 0
    for path in files:
        p = Path(path)
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        block = f"\n===== FILE: {path} =====\n{text}\n"
        if total + len(block) > MAX_CONTENT_CHARS:
            chunks.append(f"\n[Remaining files truncated at {MAX_CONTENT_CHARS} chars]\n")
            break
        chunks.append(block)
        total += len(block)
    return "".join(chunks)


def missing_sidecars(files: list[str]) -> list[str]:
    """Skill dirs in this PR that add/edit a SKILL.md but carry no sidecar.

    A skill without skill-registry.yaml is skipped by src/build_registry.py, so
    it never reaches registry.yaml and is invisible to every registry consumer.
    49 skills accumulated this way before anyone noticed (MAI-28), so this is a
    deterministic hold like the secret scan: the model does not get a vote.
    """
    dirs = {Path(p).parent for p in files if Path(p).name == "SKILL.md"}
    return sorted(str(d) for d in dirs if not (d / "skill-registry.yaml").is_file())


def scan_secrets(content: str) -> list[str]:
    hits = []
    for pat in SECRET_PATTERNS:
        if re.search(pat, content):
            hits.append(pat)
    return hits


def write_output(decision: str, body: str) -> None:
    Path("review_body.md").write_text(body, encoding="utf-8")
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as fh:
            fh.write(f"decision={decision}\n")


def main() -> int:
    base_ref = os.environ.get("BASE_REF", "main")
    files = changed_skill_files(base_ref)

    if not files:
        write_output(
            "request_changes",
            "🤖 **Haiku review:** no skill files changed under `skills/`. "
            "Leaving this for a human to look at.",
        )
        return 0

    content = gather_content(files)
    regex_hits = scan_secrets(content)
    sidecar_gaps = missing_sidecars(files)

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM,
        messages=[
            {
                "role": "user",
                "content": (
                    "Review the following skill files for this PR.\n\n"
                    f"Changed files: {', '.join(files)}\n"
                    f"{content}"
                ),
            }
        ],
        output_config={"format": {"type": "json_schema", "schema": REVIEW_SCHEMA}},
    )
    text = next((b.text for b in response.content if b.type == "text"), "{}")
    verdict = json.loads(text)

    decision = verdict.get("decision", "request_changes")
    issues = list(verdict.get("blocking_issues", []))
    summary = verdict.get("summary", "")

    # Regex secret hits override the model — always hold.
    if regex_hits or verdict.get("secrets_found"):
        decision = "request_changes"
        issues.append(
            "Potential secret detected (regex pre-scan or model flag). "
            "A human must verify before this can merge."
        )

    # A skill with no sidecar never reaches registry.yaml. Deterministic hold.
    if sidecar_gaps:
        decision = "request_changes"
        for skill_dir in sidecar_gaps:
            issues.append(
                f"`{skill_dir}` has a SKILL.md but no `skill-registry.yaml`. "
                "Without a sidecar the skill is skipped by `src/build_registry.py` "
                "and will not appear in `registry.yaml`."
            )

    if decision == "approve":
        body = (
            "🤖 **Haiku review: APPROVE** — auto-merging.\n\n"
            f"{summary}\n\n"
            f"_Reviewed {len(files)} file(s) under `skills/` with {MODEL}._"
        )
    else:
        issue_md = "\n".join(f"- {i}" for i in issues) or "- (see summary above)"
        body = (
            "🤖 **Haiku review: NEEDS HUMAN** — not auto-merging.\n\n"
            f"{summary}\n\n"
            f"**Blocking issues:**\n{issue_md}\n\n"
            f"_Reviewed {len(files)} file(s) under `skills/` with {MODEL}._"
        )

    write_output(decision, body)
    print(
        f"decision={decision}; files={len(files)}; "
        f"regex_hits={len(regex_hits)}; sidecar_gaps={len(sidecar_gaps)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
