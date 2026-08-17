"""The PR-time sidecar gate in .github/scripts/haiku_review.py (MAI-28).

The Haiku reviewer auto-merges forge/* skill PRs, so a skill shipped without a
skill-registry.yaml sidecar lands on main unreviewed and never reaches
registry.yaml. missing_sidecars() is the deterministic hold for that, in the
same shape as the existing secret pre-scan: the model does not get a vote.
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / ".github" / "scripts" / "haiku_review.py"


@pytest.fixture(scope="module")
def haiku_review():
    """Import the review script without needing the anthropic SDK installed.

    The workflow pip-installs it; the unit under test never touches the client.
    """
    if "anthropic" not in sys.modules:
        sys.modules["anthropic"] = types.ModuleType("anthropic")
    spec = importlib.util.spec_from_file_location("haiku_review", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_flags_a_skill_added_without_a_sidecar(haiku_review, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills" / "brand-new").mkdir(parents=True)
    (tmp_path / "skills" / "brand-new" / "SKILL.md").write_text("---\nname: brand-new\n---\n")

    assert haiku_review.missing_sidecars(["skills/brand-new/SKILL.md"]) == [
        "skills/brand-new"
    ]


def test_passes_a_skill_that_ships_its_sidecar(haiku_review, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill = tmp_path / "skills" / "well-formed"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: well-formed\n---\n")
    (skill / "skill-registry.yaml").write_text("name: well-formed\n")

    assert haiku_review.missing_sidecars(
        ["skills/well-formed/SKILL.md", "skills/well-formed/skill-registry.yaml"]
    ) == []


def test_ignores_files_that_are_not_skill_manifests(haiku_review, tmp_path, monkeypatch):
    """Editing a reference file in an existing skill must not trip the gate."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "skills" / "existing").mkdir(parents=True)

    assert haiku_review.missing_sidecars(["skills/existing/references/notes.md"]) == []


def test_reports_every_offender_not_just_the_first(haiku_review, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for name in ("alpha", "beta"):
        (tmp_path / "skills" / name).mkdir(parents=True)
        (tmp_path / "skills" / name / "SKILL.md").write_text("---\n")

    assert haiku_review.missing_sidecars(
        ["skills/beta/SKILL.md", "skills/alpha/SKILL.md"]
    ) == ["skills/alpha", "skills/beta"]
