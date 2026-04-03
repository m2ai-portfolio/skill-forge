"""Quality rubric for LLM-evaluated skill quality scoring.

Defines the four evaluation dimensions and scoring criteria that the Ego
quality judge uses to assess skill definitions.

Dimensions:
  - Correctness:   Does the skill produce working code/config?
  - Completeness:  Does it cover the technique end-to-end?
  - Clarity:       Are instructions unambiguous?
  - Efficiency:    Does it avoid unnecessary steps or token waste?

Each dimension scores 0-25 for a total of 0-100.
"""

from dataclasses import dataclass, field


@dataclass
class DimensionScore:
    """Score for a single rubric dimension."""
    name: str
    score: float  # 0-25
    max_score: float = 25.0
    feedback: str = ""

    def normalized(self) -> float:
        """Return score normalized to 0-100 scale."""
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0.0


@dataclass
class QualityResult:
    """Full quality evaluation result for a skill."""
    skill_name: str
    correctness: DimensionScore
    completeness: DimensionScore
    clarity: DimensionScore
    efficiency: DimensionScore
    suggestions: list[str] = field(default_factory=list)
    evaluator_model: str = ""
    evaluated_at: str = ""

    @property
    def total_score(self) -> float:
        """Aggregate score from 0-100."""
        return round(
            self.correctness.score
            + self.completeness.score
            + self.clarity.score
            + self.efficiency.score,
            1,
        )

    @property
    def dimensions(self) -> list[DimensionScore]:
        return [self.correctness, self.completeness, self.clarity, self.efficiency]

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "total_score": self.total_score,
            "correctness": {"score": self.correctness.score, "feedback": self.correctness.feedback},
            "completeness": {"score": self.completeness.score, "feedback": self.completeness.feedback},
            "clarity": {"score": self.clarity.score, "feedback": self.clarity.feedback},
            "efficiency": {"score": self.efficiency.score, "feedback": self.efficiency.feedback},
            "suggestions": self.suggestions,
            "evaluator_model": self.evaluator_model,
            "evaluated_at": self.evaluated_at,
        }


# Evaluation prompt template for LLM judges
EVALUATION_PROMPT = """You are a skill quality evaluator for Claude Code skills.

A Claude Code skill is a SKILL.md file that tells Claude how to perform a specific task.
Good skills have clear triggers, phased instructions, verification steps, and source attribution.

## Rubric

Score each dimension from 0-25:

### Correctness (0-25)
- Does the skill produce working, accurate output?
- Are code examples syntactically correct?
- Are tool references and API calls accurate?
- Would following these instructions actually work?

Scoring guide:
  0-5:   Major errors that would cause failure
  6-12:  Some errors, partial functionality
  13-18: Mostly correct, minor issues
  19-25: Fully correct and reliable

### Completeness (0-25)
- Does it cover the technique end-to-end?
- Are all phases present (gather context, execute, verify)?
- Does it handle edge cases or at least acknowledge them?
- Is source attribution included?

Scoring guide:
  0-5:   Missing major sections
  6-12:  Covers basics but gaps in workflow
  13-18: Good coverage, minor omissions
  19-25: Comprehensive, nothing missing

### Clarity (0-25)
- Are instructions unambiguous?
- Is the language direct and actionable?
- Are trigger conditions well-defined in the description?
- Would another LLM (or human) know exactly what to do?

Scoring guide:
  0-5:   Confusing, contradictory instructions
  6-12:  Understandable but vague in places
  13-18: Clear with minor ambiguity
  19-25: Crystal clear, no room for misinterpretation

### Efficiency (0-25)
- Does it avoid unnecessary steps or token waste?
- Are instructions concise without sacrificing clarity?
- Does it avoid redundant tool calls or over-engineering?
- Is the skill focused on one task (not trying to do too much)?

Scoring guide:
  0-5:   Bloated, redundant, unfocused
  6-12:  Some unnecessary steps
  13-18: Lean with minor bloat
  19-25: Optimally concise and focused

## Input

Skill name: {skill_name}

Skill definition (SKILL.md):
```
{skill_content}
```

## Output Format

Respond with ONLY a JSON object (no markdown fences, no explanation outside the JSON):

{{
  "correctness": {{"score": <0-25>, "feedback": "<1-2 sentences>"}},
  "completeness": {{"score": <0-25>, "feedback": "<1-2 sentences>"}},
  "clarity": {{"score": <0-25>, "feedback": "<1-2 sentences>"}},
  "efficiency": {{"score": <0-25>, "feedback": "<1-2 sentences>"}},
  "suggestions": ["<improvement 1>", "<improvement 2>", "<improvement 3>"]
}}
"""
