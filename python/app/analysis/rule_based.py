from pathlib import Path

from app.analysis.resume_parser import ResumeParser
from app.analysis.scoring_engine import ScoringEngine
from app.models.review import ReviewContext, ReviewResult, score_to_band


class RuleBasedAnalyzer:
    def __init__(self, skills_path: Path) -> None:
        self._parser = ResumeParser(skills_path)
        self._scoring = ScoringEngine()

    def analyze(self, text: str, context: ReviewContext | None = None) -> ReviewResult:
        parsed = self._parser.parse(text)
        total, breakdown, rationale = self._scoring.score(parsed)
        summary = self._build_summary(parsed)

        return ReviewResult(
            score=total,
            band=score_to_band(total),
            summary=summary,
            rationale=rationale,
            sections=parsed.sections,
            breakdown=breakdown,
            analyzer_used="rule",
        )

    def _build_summary(self, parsed) -> str:
        years = parsed.years_experience
        years_text = f"~{years:.0f}" if years else "unknown"
        skills = ", ".join(parsed.sections.skills[:8]) or "not clearly listed"
        roles = ", ".join(parsed.sections.experience_titles[:2]) or "not clearly listed"
        education = "; ".join(parsed.sections.education[:2]) or "not clearly listed"

        name_prefix = f"{parsed.name} — " if parsed.name else ""
        return (
            f"{name_prefix}Candidate overview: {years_text} years experience; "
            f"skills include {skills}. "
            f"Recent roles: {roles}. "
            f"Education: {education}."
        )
