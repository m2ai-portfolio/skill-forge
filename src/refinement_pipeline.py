#!/usr/bin/env python3
"""Automated refinement pipeline -- Ego identifies weakness, drafts improvement.

Reads Ego evaluation results, identifies skills below a quality threshold,
and generates structured improvement proposals for human review.

Usage:
    python src/refinement_pipeline.py                    # Propose refinements for flagged skills
    python src/refinement_pipeline.py --threshold 60     # Custom threshold (default: 50)
    python src/refinement_pipeline.py --skill name       # Target a specific skill
    python src/refinement_pipeline.py --list             # List pending proposals

Output: JSON proposals in data/refinement_proposals/ for human review.
"""
import datetime
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
RESULTS_DIR = REPO_ROOT / "data" / "ego_results"
PROPOSALS_DIR = REPO_ROOT / "data" / "refinement_proposals"


def get_latest_result(skill_name: str) -> dict | None:
    """Get the most recent Ego evaluation result for a skill."""
    if not RESULTS_DIR.is_dir():
        return None
    matches = sorted(RESULTS_DIR.glob(f"{skill_name}_*.json"), reverse=True)
    if not matches:
        return None
    return json.loads(matches[0].read_text())


def generate_proposal(result: dict) -> dict:
    """Generate a refinement proposal from an Ego evaluation result."""
    skill_name = result["skill_name"]
    total = result["total_score"]

    # Identify weakest dimensions
    dimensions = ["correctness", "completeness", "clarity", "efficiency"]
    dim_scores = [(d, result[d]["score"], result[d]["feedback"]) for d in dimensions]
    dim_scores.sort(key=lambda x: x[1])

    weakest = dim_scores[0]
    second_weakest = dim_scores[1] if len(dim_scores) > 1 else None

    priority_areas = []
    if weakest[1] < 15:
        priority_areas.append({
            "dimension": weakest[0],
            "score": weakest[1],
            "feedback": weakest[2],
            "severity": "high",
        })
    if second_weakest and second_weakest[1] < 18:
        priority_areas.append({
            "dimension": second_weakest[0],
            "score": second_weakest[1],
            "feedback": second_weakest[2],
            "severity": "medium",
        })

    return {
        "skill_name": skill_name,
        "total_score": total,
        "proposed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "pending",  # pending | applied | rejected
        "priority_areas": priority_areas,
        "suggestions": result.get("suggestions", []),
        "evaluator_model": result.get("evaluator_model", ""),
    }


def save_proposal(proposal: dict) -> Path:
    """Save a refinement proposal to disk."""
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = PROPOSALS_DIR / f"{proposal['skill_name']}_{timestamp}.json"
    path.write_text(json.dumps(proposal, indent=2) + "\n")
    return path


def list_proposals() -> list[dict]:
    """List all pending refinement proposals."""
    if not PROPOSALS_DIR.is_dir():
        return []
    proposals = []
    for f in sorted(PROPOSALS_DIR.glob("*.json")):
        data = json.loads(f.read_text())
        data["_file"] = f.name
        proposals.append(data)
    return proposals


def main():
    args = sys.argv[1:]
    threshold = 50
    target_skill = None
    do_list = "--list" in args

    for i, arg in enumerate(args):
        if arg == "--threshold" and i + 1 < len(args):
            threshold = int(args[i + 1])
        elif arg == "--skill" and i + 1 < len(args):
            target_skill = args[i + 1]

    if do_list:
        proposals = list_proposals()
        pending = [p for p in proposals if p.get("status") == "pending"]
        print(f"\n{'Skill':<35} {'Score':>6} {'Status':<10} {'Areas'}")
        print("-" * 70)
        for p in pending:
            areas = ", ".join(a["dimension"] for a in p.get("priority_areas", []))
            print(f"{p['skill_name']:<35} {p['total_score']:>6.1f} {p['status']:<10} {areas}")
        print(f"\n{len(pending)} pending proposal(s)")
        return 0

    # Determine skills to check
    if target_skill:
        skill_names = [target_skill]
    else:
        skill_names = [
            d.name for d in sorted(SKILLS_DIR.iterdir())
            if d.is_dir() and (d / "SKILL.md").is_file()
        ]

    proposals_created = 0
    for name in skill_names:
        result = get_latest_result(name)
        if not result:
            continue
        if result["total_score"] >= threshold:
            continue

        proposal = generate_proposal(result)
        path = save_proposal(proposal)
        proposals_created += 1
        print(f"  Proposal: {name} (score {result['total_score']:.1f}) -> {path.name}")
        for area in proposal["priority_areas"]:
            print(f"    [{area['severity'].upper()}] {area['dimension']}: {area['feedback']}")

    print(f"\nCreated {proposals_created} refinement proposal(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
