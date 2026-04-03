#!/usr/bin/env python3
"""Compute health scores for all registered skills and update registry files.

Scoring formula (0-100):
  When ego_quality_score IS present:
  - Ego quality:        35% — LLM-evaluated quality from ego_evaluator.py
  - Invocations (30d):  25% — normalized against the most-used skill
  - Staleness:          15% — days since created, decays over 60d
  - Deployed:           15% — sync_hash present = deployed to ~/.claude/skills/
  - Manual rating:      10% — from skill-registry.yaml (0-10 scaled to 0-100)

  When ego_quality_score is null but manual_rating IS present:
  - Invocations (30d):  40% — normalized against the most-used skill
  - Staleness:          20% — days since created, decays over 60d
  - Deployed:           20% — sync_hash present = deployed to ~/.claude/skills/
  - Manual rating:      20% — from skill-registry.yaml (0-10 scaled to 0-100)

  When both ego_quality_score and manual_rating are null:
  - Invocations (30d):  50% — normalized against the most-used skill
  - Staleness:          20% — days since created, decays over 60d
  - Deployed:           30% — sync_hash present = deployed to ~/.claude/skills/

Usage:
    python src/scorecard.py              # Score all skills, print report
    python src/scorecard.py --update     # Also write health_score to registry files
    python src/scorecard.py --threshold 30  # Flag skills below threshold
"""
import datetime
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
DB_PATH = REPO_ROOT / "data" / "skill_invocations.db"

WEIGHTS_WITH_EGO_AND_RATING = {
    "ego_quality": 0.35,
    "invocations": 0.25,
    "staleness": 0.15,
    "deployed": 0.15,
    "manual_rating": 0.10,
}

WEIGHTS_WITH_EGO_NO_RATING = {
    "ego_quality": 0.40,
    "invocations": 0.30,
    "staleness": 0.15,
    "deployed": 0.15,
    "manual_rating": 0.00,
}

WEIGHTS_WITH_RATING = {
    "ego_quality": 0.00,
    "invocations": 0.40,
    "staleness": 0.20,
    "deployed": 0.20,
    "manual_rating": 0.20,
}

WEIGHTS_NO_RATING = {
    "ego_quality": 0.00,
    "invocations": 0.50,
    "staleness": 0.20,
    "deployed": 0.30,
    "manual_rating": 0.00,
}


def get_invocation_counts(days: int = 30) -> dict[str, int]:
    """Get invocation counts per skill for the last N days."""
    if not DB_PATH.is_file():
        return {}
    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT skill_name, COUNT(*) FROM skill_invocations "
        "WHERE invoked_at >= ? GROUP BY skill_name",
        (cutoff,),
    ).fetchall()
    conn.close()
    return dict(rows)


def parse_registry(path: Path) -> dict:
    """Parse key fields from a skill-registry.yaml without PyYAML."""
    data = {"name": None, "status": None, "created": None, "sync_hash": None,
            "manual_rating": None, "ego_quality_score": None}
    in_metrics = False
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("name:"):
            data["name"] = stripped.split(":", 1)[1].strip().strip('"')
        elif stripped.startswith("status:"):
            data["status"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("created:"):
            data["created"] = stripped.split(":", 1)[1].strip().strip('"')
        elif stripped.startswith("sync_hash:"):
            val = stripped.split(":", 1)[1].strip()
            data["sync_hash"] = None if val == "null" else val
        elif stripped == "metrics:":
            in_metrics = True
        elif in_metrics and stripped.startswith("manual_rating:"):
            val = stripped.split(":", 1)[1].strip()
            data["manual_rating"] = None if val == "null" else float(val)
        elif in_metrics and stripped.startswith("ego_quality_score:"):
            val = stripped.split(":", 1)[1].strip()
            data["ego_quality_score"] = None if val == "null" else float(val)
        elif in_metrics and not stripped.startswith(("invocations_30d:", "last_invoked:", "health_score:")):
            if ":" in stripped and not stripped.startswith("#"):
                in_metrics = False
    return data


def compute_scores(threshold: int = 0) -> list[dict]:
    """Compute health scores for all skills."""
    invocations = get_invocation_counts(30)
    max_invocations = max(invocations.values()) if invocations else 1
    today = datetime.date.today()

    results = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        registry_path = skill_dir / "skill-registry.yaml"
        if not registry_path.is_file():
            continue

        reg = parse_registry(registry_path)
        if not reg["name"]:
            continue

        # Skip deprecated skills
        if reg["status"] == "deprecated":
            results.append({"name": reg["name"], "score": 0, "status": reg["status"],
                            "components": {}, "flagged": False})
            continue

        has_rating = reg["manual_rating"] is not None
        has_ego = reg["ego_quality_score"] is not None

        if has_ego and has_rating:
            weights = WEIGHTS_WITH_EGO_AND_RATING
        elif has_ego:
            weights = WEIGHTS_WITH_EGO_NO_RATING
        elif has_rating:
            weights = WEIGHTS_WITH_RATING
        else:
            weights = WEIGHTS_NO_RATING

        # Ego quality score: already 0-100 from ego_evaluator
        ego_score = reg["ego_quality_score"] if has_ego else 0

        # Invocation score (0-100): normalized against max
        inv_count = invocations.get(reg["name"], 0)
        inv_score = (inv_count / max_invocations) * 100 if max_invocations > 0 else 0

        # Staleness score (0-100): 100 if created today, decays to 0 over 60 days
        if reg["created"]:
            created_date = datetime.date.fromisoformat(reg["created"])
            age_days = (today - created_date).days
            staleness_score = max(0, 100 - (age_days / 60) * 100)
        else:
            staleness_score = 0

        # Deployed score: 100 if sync_hash present, 0 otherwise
        deployed_score = 100 if reg["sync_hash"] else 0

        # Manual rating score: 0-10 scaled to 0-100
        rating_score = (reg["manual_rating"] / 10) * 100 if has_rating else 0

        components = {
            "ego_quality": ego_score,
            "invocations": inv_score,
            "staleness": staleness_score,
            "deployed": deployed_score,
            "manual_rating": rating_score,
        }

        total = sum(components[k] * weights[k] for k in weights)
        total = round(total, 1)

        results.append({
            "name": reg["name"],
            "score": total,
            "status": reg["status"],
            "components": components,
            "inv_count": inv_count,
            "flagged": total < threshold if threshold > 0 else False,
        })

    return results


def update_registry_score(skill_name: str, score: float, inv_count: int) -> bool:
    """Write health_score and invocations_30d back to skill-registry.yaml."""
    registry_path = SKILLS_DIR / skill_name / "skill-registry.yaml"
    if not registry_path.is_file():
        return False

    content = registry_path.read_text()
    lines = content.splitlines()
    new_lines = []
    updated = False

    for line in lines:
        if line.strip().startswith("health_score:"):
            new_line = line.split("health_score:")[0] + f"health_score: {score}"
            if line != new_line:
                new_lines.append(new_line)
                updated = True
            else:
                new_lines.append(line)
        elif line.strip().startswith("invocations_30d:"):
            new_line = line.split("invocations_30d:")[0] + f"invocations_30d: {inv_count}"
            if line != new_line:
                new_lines.append(new_line)
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
    threshold = 30  # default
    for i, arg in enumerate(args):
        if arg == "--threshold" and i + 1 < len(args):
            threshold = int(args[i + 1])

    results = compute_scores(threshold)

    # Print report
    print(f"\n{'Skill':<35} {'Score':>6} {'Status':<14} {'Inv':>4} {'Flag'}")
    print("-" * 72)
    for r in results:
        flag = "***" if r.get("flagged") else ""
        inv = r.get("inv_count", 0)
        print(f"{r['name']:<35} {r['score']:>6.1f} {r['status']:<14} {inv:>4} {flag}")

    flagged = [r for r in results if r.get("flagged")]
    if flagged:
        print(f"\n{len(flagged)} skill(s) below threshold {threshold}:")
        for r in flagged:
            print(f"  - {r['name']} ({r['score']:.1f})")

    if do_update:
        updated = 0
        for r in results:
            if update_registry_score(r["name"], r["score"], r.get("inv_count", 0)):
                updated += 1
        print(f"\nUpdated {updated} registry files")

        # Regenerate aggregated registry
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_registry", REPO_ROOT / "src" / "build_registry.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build()

    return 0


if __name__ == "__main__":
    sys.exit(main())
