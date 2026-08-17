#!/usr/bin/env python3
"""Build aggregated registry.yaml from individual skill-registry.yaml sidecar files.

Usage:
    python src/build_registry.py            # write registry.yaml, warn on gaps
    python src/build_registry.py --strict   # ...and exit 1 if any gap remains
"""
import datetime
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
OUTPUT = REPO_ROOT / "registry.yaml"

# Preferred display order for the by_status summary. Any status found in the
# sidecars but absent here is still reported, appended in sorted order — a
# hardcoded list silently dropped 47 `cold` skills from the summary until 2026-08-15.
STATUS_ORDER = ("active", "draft", "under_review", "refined", "deprecated", "cold")


def load_sidecar(path: Path) -> dict | None:
    """Load a skill-registry.yaml file."""
    if not path.is_file():
        return None
    if yaml:
        return yaml.safe_load(path.read_text())
    # Fallback: parse the subset of fields we need without PyYAML
    data = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        for key in ("name", "version", "status"):
            if line.startswith(f"{key}:"):
                val = line.split(":", 1)[1].strip().strip('"')
                data[key] = val
    # Parse domain from taxonomy block
    in_taxonomy = False
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped == "taxonomy:":
            in_taxonomy = True
            continue
        if in_taxonomy and stripped.startswith("domain:"):
            data["domain"] = stripped.split(":", 1)[1].strip()
            break
        if in_taxonomy and not stripped.startswith(("domain:", "complexity:")) and ":" in stripped:
            in_taxonomy = False
    return data if data.get("name") else None


def find_unregistered() -> list[str]:
    """Skill dirs holding a SKILL.md but no sidecar, at any depth under skills/.

    These are invisible to build(): no sidecar means no registry entry, and a
    skill nested below the top level is never even visited. Surfacing them is
    the whole point — 49 skills sat unregistered this way until 2026-08-15.
    """
    return sorted(
        str(md.parent.relative_to(REPO_ROOT))
        for md in SKILLS_DIR.rglob("SKILL.md")
        if not (md.parent / "skill-registry.yaml").is_file()
    )


def build():
    entries = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        sidecar = load_sidecar(skill_dir / "skill-registry.yaml")
        if not sidecar:
            continue
        entries.append({
            "name": sidecar["name"],
            "version": sidecar.get("version", "0.0.0"),
            "status": sidecar.get("status", "draft"),
            "domain": sidecar.get("domain", sidecar.get("taxonomy", {}).get("domain", "unknown")),
            "health_score": sidecar.get("metrics", {}).get("health_score") if isinstance(sidecar.get("metrics"), dict) else None,
        })

    status_counts = Counter(e["status"] for e in entries)
    today = datetime.date.today().isoformat()

    # Build output as plain text to avoid PyYAML dependency
    lines = [
        "# Skill Forge Registry Index",
        "# Auto-generated aggregation of all skill-registry.yaml files",
        "# Consumers: Forge review pass, Sky-Lynx analysis, AutoResearch catalog awareness",
        "# Regenerate: python src/build_registry.py",
        "",
        f'generated_at: "{today}"',
        f"total_skills: {len(entries)}",
        "by_status:",
    ]
    ordered = [s for s in STATUS_ORDER if status_counts.get(s)]
    ordered += sorted(s for s in status_counts if s not in STATUS_ORDER)
    for status in ordered:
        lines.append(f"  {status}: {status_counts[status]}")

    lines.append("")
    lines.append("skills:")
    for entry in entries:
        lines.append(f"  - name: {entry['name']}")
        lines.append(f'    version: "{entry["version"]}"')
        lines.append(f"    status: {entry['status']}")
        lines.append(f"    domain: {entry['domain']}")
        hs = entry["health_score"]
        lines.append(f"    health_score: {hs if hs is not None else 'null'}")
        lines.append("")

    OUTPUT.write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUTPUT} with {len(entries)} skills")

    unregistered = find_unregistered()
    for path in unregistered:
        print(f"WARNING: {path} has a SKILL.md but no skill-registry.yaml, "
              f"so it is missing from {OUTPUT.name}")
    return unregistered


if __name__ == "__main__":
    missing = build()
    # --strict turns the warning into a failure. Off by default so a stray
    # sidecar-less skill cannot block registry regeneration on main; the
    # blocking gate lives at PR time in .github/scripts/haiku_review.py.
    if "--strict" in sys.argv and missing:
        sys.exit(1)
