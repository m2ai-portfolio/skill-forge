#!/usr/bin/env python3
"""Compute and compare SHA256 hashes between repo SKILL.md and deployed copies.

Usage:
    python src/sync_hash.py                  # Check all skills
    python src/sync_hash.py context-hygiene  # Check one skill
    python src/sync_hash.py --update         # Update all skill-registry.yaml sync_hash fields
"""
import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
DEPLOYED_DIR = Path.home() / ".claude" / "skills"


def sha256_file(path: Path) -> str | None:
    """Return SHA256 hex digest of a file, or None if it doesn't exist."""
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_skill(skill_name: str) -> dict:
    """Compare repo vs deployed hash for a single skill."""
    repo_path = SKILLS_DIR / skill_name / "SKILL.md"
    deployed_path = DEPLOYED_DIR / skill_name / "SKILL.md"

    repo_hash = sha256_file(repo_path)
    deployed_hash = sha256_file(deployed_path)

    return {
        "name": skill_name,
        "repo_hash": repo_hash,
        "deployed_hash": deployed_hash,
        "in_sync": repo_hash == deployed_hash if (repo_hash and deployed_hash) else None,
        "deployed": deployed_hash is not None,
    }


def update_registry_hash(skill_name: str, hash_value: str | None) -> bool:
    """Update sync_hash in a skill's skill-registry.yaml. Returns True if updated."""
    registry_path = SKILLS_DIR / skill_name / "skill-registry.yaml"
    if not registry_path.is_file():
        return False

    content = registry_path.read_text()
    lines = content.splitlines()
    new_lines = []
    updated = False

    for line in lines:
        if line.startswith("sync_hash:"):
            new_value = f"sync_hash: {hash_value}" if hash_value else "sync_hash: null"
            if line != new_value:
                new_lines.append(new_value)
                updated = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    if updated:
        registry_path.write_text("\n".join(new_lines) + "\n")

    return updated


def main():
    args = sys.argv[1:]
    do_update = "--update" in args
    skill_filter = [a for a in args if not a.startswith("--")]

    if skill_filter:
        skill_dirs = [SKILLS_DIR / name for name in skill_filter if (SKILLS_DIR / name).is_dir()]
    else:
        skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())

    results = []
    for skill_dir in skill_dirs:
        result = check_skill(skill_dir.name)
        results.append(result)

        if do_update and result["deployed_hash"]:
            if update_registry_hash(skill_dir.name, result["deployed_hash"]):
                print(f"  Updated sync_hash for {skill_dir.name}")

    # Print summary
    print(f"\n{'Skill':<35} {'Deployed':<10} {'In Sync':<10} {'Hash (deployed)'}")
    print("-" * 90)
    for r in results:
        deployed = "yes" if r["deployed"] else "no"
        in_sync = "yes" if r["in_sync"] else ("no" if r["in_sync"] is False else "-")
        hash_short = r["deployed_hash"][:16] + "..." if r["deployed_hash"] else "-"
        print(f"{r['name']:<35} {deployed:<10} {in_sync:<10} {hash_short}")

    # Exit code: 1 if any skill is out of sync
    out_of_sync = [r for r in results if r["in_sync"] is False]
    if out_of_sync:
        print(f"\n{len(out_of_sync)} skill(s) out of sync.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
