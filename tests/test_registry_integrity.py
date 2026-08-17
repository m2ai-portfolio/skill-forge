"""Registry bookkeeping invariants (MAI-28).

49 committed skills were absent from registry.yaml because they carried a
SKILL.md and no skill-registry.yaml sidecar, and src/build_registry.py skips
sidecar-less dirs. Nothing checked for that, so the drift accumulated for
months across 18% of the library. These tests are the check.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
REGISTRY = REPO_ROOT / "registry.yaml"

sys.path.insert(0, str(REPO_ROOT / "src"))
import build_registry  # noqa: E402


def skill_dirs() -> list[Path]:
    """Every directory in the tree that holds a SKILL.md, at any depth."""
    return sorted(md.parent for md in SKILLS_DIR.rglob("SKILL.md"))


def sidecars() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/skill-registry.yaml"))


def test_every_skill_has_a_sidecar():
    missing = [str(d.relative_to(REPO_ROOT)) for d in skill_dirs()
               if not (d / "skill-registry.yaml").is_file()]
    assert missing == [], (
        "these skills carry a SKILL.md but no skill-registry.yaml, so "
        f"src/build_registry.py will drop them from registry.yaml: {missing}"
    )


def test_no_skill_is_nested_below_the_top_level():
    """build_registry.py iterates skills/ one level deep and never recurses."""
    nested = [str(d.relative_to(REPO_ROOT)) for d in skill_dirs() if d.parent != SKILLS_DIR]
    assert nested == [], (
        "skills below skills/<name>/ are never visited by src/build_registry.py "
        f"and cannot reach registry.yaml regardless of their sidecar: {nested}"
    )


def test_find_unregistered_agrees_with_the_tree():
    assert build_registry.find_unregistered() == []


@pytest.mark.parametrize("sidecar", sidecars(), ids=lambda p: p.parent.name)
def test_sidecar_parses_and_names_its_own_directory(sidecar: Path):
    data = yaml.safe_load(sidecar.read_text())
    assert isinstance(data, dict), f"{sidecar} did not parse to a mapping"
    assert data.get("name") == sidecar.parent.name, (
        f"{sidecar} declares name={data.get('name')!r} but lives in "
        f"{sidecar.parent.name!r}; registry.yaml would key it wrongly"
    )
    assert data.get("status"), f"{sidecar} has no status, registry.yaml would default it"


def test_registry_is_current(tmp_path, monkeypatch):
    """registry.yaml on disk must match a fresh regeneration.

    generated_at is excluded: it is stamped with today's date on every run and
    says nothing about whether the skill list drifted.
    """
    before = REGISTRY.read_text()
    monkeypatch.setattr(build_registry, "OUTPUT", tmp_path / "registry.yaml")
    build_registry.build()
    after = (tmp_path / "registry.yaml").read_text()

    def strip_stamp(text: str) -> list[str]:
        return [ln for ln in text.splitlines() if not ln.startswith("generated_at:")]

    assert strip_stamp(before) == strip_stamp(after), (
        "registry.yaml is stale; run `python src/build_registry.py` and commit the result"
    )


def test_registry_status_counts_cover_every_skill():
    """A hardcoded status list silently dropped 47 `cold` skills from by_status."""
    registry = yaml.safe_load(REGISTRY.read_text())
    assert sum(registry["by_status"].values()) == registry["total_skills"]
    assert registry["total_skills"] == len(registry["skills"])
