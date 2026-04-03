"""Tests for ego_evaluator.py -- LLM response parsing, registry updates, and scoring."""
import json
import sys
import tempfile
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ego_evaluator import parse_llm_response, update_registry_ego_score, read_skill
import ego_evaluator


class TestParseLlmResponse:
    VALID_JSON = json.dumps({
        "correctness": {"score": 20, "feedback": "Solid"},
        "completeness": {"score": 18, "feedback": "Missing edge cases"},
        "clarity": {"score": 22, "feedback": "Very clear"},
        "efficiency": {"score": 15, "feedback": "Some bloat"},
        "suggestions": ["Add error handling", "Trim phase 3"],
    })

    def test_parse_valid_json(self):
        result = parse_llm_response(self.VALID_JSON, "test-skill")
        assert result.skill_name == "test-skill"
        assert result.correctness.score == 20
        assert result.completeness.score == 18
        assert result.clarity.score == 22
        assert result.efficiency.score == 15
        assert result.total_score == 75.0
        assert len(result.suggestions) == 2

    def test_parse_json_with_markdown_fences(self):
        text = f"```json\n{self.VALID_JSON}\n```"
        result = parse_llm_response(text, "fenced-skill")
        assert result.skill_name == "fenced-skill"
        assert result.total_score == 75.0

    def test_parse_clamps_scores(self):
        bad_json = json.dumps({
            "correctness": {"score": 30, "feedback": "Over max"},
            "completeness": {"score": -5, "feedback": "Under min"},
            "clarity": {"score": 25, "feedback": "Max"},
            "efficiency": {"score": 0, "feedback": "Zero"},
            "suggestions": [],
        })
        result = parse_llm_response(bad_json, "clamped")
        assert result.correctness.score == 25.0  # clamped from 30
        assert result.completeness.score == 0.0  # clamped from -5

    def test_parse_missing_dimensions_default_zero(self):
        minimal = json.dumps({"suggestions": ["Do better"]})
        result = parse_llm_response(minimal, "minimal")
        assert result.total_score == 0.0
        assert len(result.suggestions) == 1

    def test_parse_invalid_json_raises(self):
        try:
            parse_llm_response("not json at all", "bad")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Failed to parse" in str(e)

    def test_result_has_metadata(self):
        result = parse_llm_response(self.VALID_JSON, "meta-skill")
        assert result.evaluator_model  # should be set by default
        assert result.evaluated_at  # should be set


class TestUpdateRegistryEgoScore:
    SAMPLE_REGISTRY = textwrap.dedent("""\
        name: test-skill
        version: "1.0.0"
        status: active
        created: "2026-03-26"
        last_reviewed: null
        sync_hash: null

        source:
          type: newsletter
          url: "https://example.com"
          author: "Test Author"
          date: "2026-03-25"

        taxonomy:
          domain: agent-architecture
          complexity: intermediate

        metrics:
          invocations_30d: 5
          last_invoked: null
          manual_rating: null
          health_score: 30.0

        learning:
          total_patches_applied: 0
          total_patches_proposed: 0
          last_patch_at: null
          effectiveness_score: null

        lineage:
          parent_version: null
          derived_from: null
          changelog: []

        dependencies: []
    """)

    def test_inserts_ego_score(self, tmp_path):
        # Set up fake skills directory
        skill_dir = tmp_path / "skills" / "test-skill"
        skill_dir.mkdir(parents=True)
        reg_path = skill_dir / "skill-registry.yaml"
        reg_path.write_text(self.SAMPLE_REGISTRY)

        # Patch SKILLS_DIR
        original = ego_evaluator.SKILLS_DIR
        ego_evaluator.SKILLS_DIR = tmp_path / "skills"
        try:
            result = update_registry_ego_score("test-skill", 72.5)
            assert result is True
            content = reg_path.read_text()
            assert "ego_quality_score: 72.5" in content
        finally:
            ego_evaluator.SKILLS_DIR = original

    def test_updates_existing_ego_score(self, tmp_path):
        registry_with_ego = self.SAMPLE_REGISTRY.replace(
            "health_score: 30.0",
            "health_score: 30.0\n    ego_quality_score: 50.0",
        )
        skill_dir = tmp_path / "skills" / "test-skill"
        skill_dir.mkdir(parents=True)
        reg_path = skill_dir / "skill-registry.yaml"
        reg_path.write_text(registry_with_ego)

        original = ego_evaluator.SKILLS_DIR
        ego_evaluator.SKILLS_DIR = tmp_path / "skills"
        try:
            result = update_registry_ego_score("test-skill", 85.0)
            assert result is True
            content = reg_path.read_text()
            assert "ego_quality_score: 85.0" in content
            assert "ego_quality_score: 50.0" not in content
        finally:
            ego_evaluator.SKILLS_DIR = original

    def test_nonexistent_skill_returns_false(self, tmp_path):
        original = ego_evaluator.SKILLS_DIR
        ego_evaluator.SKILLS_DIR = tmp_path / "skills"
        try:
            result = update_registry_ego_score("nonexistent", 50.0)
            assert result is False
        finally:
            ego_evaluator.SKILLS_DIR = original


class TestReadSkill:
    def test_reads_existing_skill(self, tmp_path):
        skill_dir = tmp_path / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill\nDo the thing.")

        original = ego_evaluator.SKILLS_DIR
        ego_evaluator.SKILLS_DIR = tmp_path / "skills"
        try:
            content = read_skill("my-skill")
            assert content == "# My Skill\nDo the thing."
        finally:
            ego_evaluator.SKILLS_DIR = original

    def test_returns_none_for_missing(self, tmp_path):
        original = ego_evaluator.SKILLS_DIR
        ego_evaluator.SKILLS_DIR = tmp_path / "skills"
        try:
            content = read_skill("no-such-skill")
            assert content is None
        finally:
            ego_evaluator.SKILLS_DIR = original
