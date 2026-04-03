"""Tests for scorecard.py -- health score computation with ego quality integration."""
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import scorecard


class TestWeightSelection:
    """Verify the correct weight set is chosen based on available data."""

    def test_weights_with_ego_and_rating(self):
        w = scorecard.WEIGHTS_WITH_EGO_AND_RATING
        assert abs(sum(w.values()) - 1.0) < 0.001
        assert w["ego_quality"] == 0.35

    def test_weights_with_ego_no_rating(self):
        w = scorecard.WEIGHTS_WITH_EGO_NO_RATING
        assert abs(sum(w.values()) - 1.0) < 0.001
        assert w["ego_quality"] == 0.40
        assert w["manual_rating"] == 0.00

    def test_weights_with_rating_no_ego(self):
        w = scorecard.WEIGHTS_WITH_RATING
        assert abs(sum(w.values()) - 1.0) < 0.001
        assert w["ego_quality"] == 0.00

    def test_weights_no_rating_no_ego(self):
        w = scorecard.WEIGHTS_NO_RATING
        assert abs(sum(w.values()) - 1.0) < 0.001
        assert w["ego_quality"] == 0.00
        assert w["manual_rating"] == 0.00


class TestParseRegistry:
    REGISTRY_WITH_EGO = textwrap.dedent("""\
        name: test-skill
        version: "1.0.0"
        status: active
        created: "2026-03-26"
        last_reviewed: null
        sync_hash: abc123def456

        metrics:
          invocations_30d: 5
          last_invoked: null
          manual_rating: 8.0
          health_score: 65.0
          ego_quality_score: 72.5

        learning:
          total_patches_applied: 0
    """)

    REGISTRY_WITHOUT_EGO = textwrap.dedent("""\
        name: basic-skill
        version: "1.0.0"
        status: active
        created: "2026-03-20"
        sync_hash: null

        metrics:
          invocations_30d: 0
          last_invoked: null
          manual_rating: null
          health_score: 20.0

        learning:
          total_patches_applied: 0
    """)

    def test_parse_with_ego_score(self, tmp_path):
        p = tmp_path / "reg.yaml"
        p.write_text(self.REGISTRY_WITH_EGO)
        data = scorecard.parse_registry(p)
        assert data["ego_quality_score"] == 72.5
        assert data["manual_rating"] == 8.0
        assert data["name"] == "test-skill"
        assert data["sync_hash"] == "abc123def456"

    def test_parse_without_ego_score(self, tmp_path):
        p = tmp_path / "reg.yaml"
        p.write_text(self.REGISTRY_WITHOUT_EGO)
        data = scorecard.parse_registry(p)
        assert data["ego_quality_score"] is None
        assert data["manual_rating"] is None


class TestComputeScores:
    """Test score computation with ego quality integrated."""

    def _setup_skill(self, tmp_path, name, registry_text):
        skill_dir = tmp_path / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "skill-registry.yaml").write_text(registry_text)

    def test_ego_score_increases_total(self, tmp_path):
        """A skill with a high ego score should get a boost."""
        reg_with_ego = textwrap.dedent("""\
            name: good-skill
            version: "1.0.0"
            status: active
            created: "2026-04-03"
            sync_hash: null

            metrics:
              invocations_30d: 0
              last_invoked: null
              manual_rating: null
              health_score: null
              ego_quality_score: 90.0

            learning:
              total_patches_applied: 0
        """)
        reg_without_ego = textwrap.dedent("""\
            name: plain-skill
            version: "1.0.0"
            status: active
            created: "2026-04-03"
            sync_hash: null

            metrics:
              invocations_30d: 0
              last_invoked: null
              manual_rating: null
              health_score: null

            learning:
              total_patches_applied: 0
        """)

        self._setup_skill(tmp_path, "good-skill", reg_with_ego)
        self._setup_skill(tmp_path, "plain-skill", reg_without_ego)

        original = scorecard.SKILLS_DIR
        scorecard.SKILLS_DIR = tmp_path
        try:
            results = scorecard.compute_scores(threshold=0)
            scores = {r["name"]: r["score"] for r in results}
            # The skill with ego=90 and ego weight 0.40 should score higher
            assert scores["good-skill"] > scores["plain-skill"]
        finally:
            scorecard.SKILLS_DIR = original

    def test_deprecated_skill_scores_zero(self, tmp_path):
        reg = textwrap.dedent("""\
            name: old-skill
            version: "1.0.0"
            status: deprecated
            created: "2026-01-01"
            sync_hash: null

            metrics:
              invocations_30d: 0
              last_invoked: null
              manual_rating: null
              health_score: null
              ego_quality_score: 80.0

            learning:
              total_patches_applied: 0
        """)
        self._setup_skill(tmp_path, "old-skill", reg)

        original = scorecard.SKILLS_DIR
        scorecard.SKILLS_DIR = tmp_path
        try:
            results = scorecard.compute_scores()
            assert results[0]["score"] == 0
        finally:
            scorecard.SKILLS_DIR = original
