#!/usr/bin/env python3
"""Sync newly-built skills from skill-forge into the public m2ai-skills-pack.

The pack is a curated, public, client-facing distribution. Per the
/publish-skill rule it is NEVER auto-published: every skill needs a per-match
sanitization review before it ships. So this script does the toil (find what's
missing, copy it, draft README updates, scan for leaks) and opens ONE pull
request on the pack — a human reviews, genericizes if needed, and merges.

Default is --report (just list what's missing). Use --apply to open a PR.
Start with --only <name> to prove one skill end-to-end before syncing the batch.

Examples:
    python scripts/sync_to_pack.py                      # report missing skills
    python scripts/sync_to_pack.py --apply --only foo   # one skill -> draft PR
    python scripts/sync_to_pack.py --apply --limit 5    # first 5 -> draft PR
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

FORGE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PACK = Path.home() / "projects" / "m2ai-skills-pack"
PACK_REPO = "m2ai-portfolio/m2ai-skills-pack"

# Secret shapes — a hit is surfaced loudly in the PR body for the human.
SECRET_PATTERNS = [
    r"sk-ant-[A-Za-z0-9_\-]{20,}",
    r"ghp_[A-Za-z0-9]{36}",
    r"AKIA[0-9A-Z]{16}",
    r"AIza[0-9A-Za-z\-_]{35}",
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
]

# Client / agent-internal / infra names that must not propagate to a public,
# client-facing repo without a human deciding they're fine. Flag, don't block.
NAME_DENYLIST = [
    "Ravage", "Scout", "RepMan", "Soundwave", "Galvatron", "Wheeljack", "Kup",
    "ClaudeClaw", "claudeclaw", "Snow-Town", "ST Metro", "apexaipc",
    "Ayman", "Matthew Snow", "10.0.0.", "Portainer",
]


def run(cmd: list[str], cwd: Path | None = None) -> str:
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, check=True
    ).stdout.strip()


def skill_names(root: Path) -> set[str]:
    skills = root / "skills"
    return {p.name for p in skills.iterdir() if (p / "SKILL.md").is_file()} if skills.is_dir() else set()


def frontmatter(skill_dir: Path) -> dict:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def scan(skill_dir: Path) -> list[str]:
    flags: list[str] = []
    for f in skill_dir.rglob("*"):
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        for pat in SECRET_PATTERNS:
            if re.search(pat, text):
                flags.append(f"`{f.relative_to(skill_dir)}`: secret-shaped match `{pat}`")
        for name in NAME_DENYLIST:
            if name in text:
                flags.append(f"`{f.relative_to(skill_dir)}`: contains denylisted name `{name}`")
    return flags


def catalog_row(name: str, fm: dict) -> str:
    desc = (fm.get("description") or "").replace("\n", " ").strip()
    what = (desc[:110] + "…") if len(desc) > 110 else (desc or "(no description)")
    return f"| [{name}](skills/{name}/) | {what} | _refile + verify before merge_ |"


def update_readme(pack: Path, added: list[str], fms: dict[str, dict]) -> None:
    readme = pack / "README.md"
    text = readme.read_text(encoding="utf-8")
    n = len(added)

    # Bump the grand total and add a holding row in the "What's inside" table.
    total_row = re.search(r"\| \| \*\*(\d+)\*\* \| \|", text)
    if total_row:
        new_total = int(total_row.group(1)) + n
        holding = (
            "| 🆕 [Recently synced](#-recently-synced-pending-categorization) "
            f"| {n} | Pending categorization — refile before merge. |\n"
        )
        text = text.replace(
            total_row.group(0), holding + f"| | **{new_total}** | |"
        )

    # Append a holding catalog section just before "## Configuration".
    rows = "\n".join(catalog_row(name, fms[name]) for name in added)
    section = (
        "### 🆕 Recently synced (pending categorization)\n\n"
        f"*Added by sync_to_pack on {datetime.now():%Y-%m-%d}. Refile each skill "
        "into the correct division above and adjust counts before merging.*\n\n"
        "| Skill | What it does | When to use |\n|---|---|---|\n"
        f"{rows}\n\n"
    )
    text = text.replace("## Configuration", section + "## Configuration", 1)
    readme.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pack", type=Path, default=DEFAULT_PACK)
    ap.add_argument("--base", default="master")
    ap.add_argument("--apply", action="store_true", help="open a PR (default: report only)")
    ap.add_argument("--only", action="append", default=[], help="sync only this skill (repeatable)")
    ap.add_argument("--limit", type=int, default=0, help="cap number of skills synced")
    ap.add_argument("--no-pr", action="store_true", help="stage a branch but don't open the PR")
    args = ap.parse_args()

    pack: Path = args.pack
    if not (pack / "skills").is_dir():
        print(f"error: pack repo not found at {pack}", file=sys.stderr)
        return 1

    missing = sorted(skill_names(FORGE_ROOT) - skill_names(pack))
    if args.only:
        missing = [s for s in missing if s in args.only]
    if args.limit:
        missing = missing[: args.limit]

    if not missing:
        print("Nothing to sync — pack already has every forge skill (or filter matched none).")
        return 0

    if not args.apply:
        print(f"{len(missing)} skill(s) in forge but not in pack:")
        for s in missing:
            print(f"  - {s}")
        print("\nRe-run with --apply (start with --only <name>) to open a draft PR.")
        return 0

    if run(["git", "-C", str(pack), "status", "--porcelain"]):
        print(f"error: {pack} has uncommitted changes — commit or stash first.", file=sys.stderr)
        return 1

    run(["git", "-C", str(pack), "checkout", args.base])
    run(["git", "-C", str(pack), "pull", "--ff-only", "origin", args.base])
    branch = f"sync/forge-{datetime.now():%Y%m%d-%H%M%S}"
    run(["git", "-C", str(pack), "checkout", "-b", branch])

    fms: dict[str, dict] = {}
    flag_report: list[str] = []
    for name in missing:
        src, dst = FORGE_ROOT / "skills" / name, pack / "skills" / name
        shutil.copytree(src, dst)
        fms[name] = frontmatter(src)
        for flag in scan(dst):
            flag_report.append(f"- **{name}** — {flag}")

    update_readme(pack, missing, fms)

    run(["git", "-C", str(pack), "add", "-A"])
    run(["git", "-C", str(pack), "commit", "-m",
         f"sync: add {len(missing)} skill(s) from skill-forge [pending review]"])

    if args.no_pr:
        print(f"Staged branch {branch} (not pushed). Review, then push + open PR manually.")
        return 0

    run(["git", "-C", str(pack), "push", "-u", "origin", branch])

    added_md = "\n".join(f"- `{s}`" for s in missing)
    flags_md = "\n".join(flag_report) if flag_report else "_None detected._"
    body = (
        "Automated sync from **skill-forge**. **Do not merge without a "
        "per-skill sanitization review** — this is a public, client-facing repo.\n\n"
        f"### Skills added ({len(missing)})\n{added_md}\n\n"
        "### Sanitization scan (secret + denylisted-name flags)\n"
        f"{flags_md}\n\n"
        "### Before merging\n"
        "- [ ] Review each skill for client / agent-internal names and secrets\n"
        "- [ ] Genericize as needed (run `/publish-skill` per skill if heavier rewrite is wanted)\n"
        "- [ ] Refile the **Recently synced** README rows into the correct division and fix counts\n\n"
        "🤖 Generated with [Claude Code](https://claude.com/claude-code)"
    )
    body_file = pack / ".sync-pr-body.md"
    body_file.write_text(body, encoding="utf-8")
    url = run(["gh", "pr", "create", "-R", PACK_REPO, "--base", args.base,
               "--head", branch, "--title",
               f"sync: {len(missing)} skill(s) from skill-forge [needs review]",
               "--body-file", str(body_file)])
    body_file.unlink(missing_ok=True)
    print(f"Opened PR: {url}")
    print(f"Sanitization flags: {len(flag_report)} (see PR body).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
