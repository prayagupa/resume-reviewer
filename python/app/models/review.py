from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ResumeSections(BaseModel):
    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience_titles: list[str] = Field(default_factory=list)


class ParsedResume(BaseModel):
    raw_text: str
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    years_experience: float = 0.0
    sections: ResumeSections = Field(default_factory=ResumeSections)
    has_experience_section: bool = False
    has_education_section: bool = False
    has_skills_section: bool = False
    page_count_estimate: int = 1
    action_verb_count: int = 0
    metric_count: int = 0
    progression_keyword_count: int = 0


class ScoreBreakdown(BaseModel):
    structure: int = 0
    experience: int = 0
    skills: int = 0
    impact: int = 0
    clarity: int = 0

    @property
    def total(self) -> int:
        return self.structure + self.experience + self.skills + self.impact + self.clarity


class ReviewContext(BaseModel):
    job_title: str | None = None
    required_skills: list[str] = Field(default_factory=list)


class LlmReviewOutput(BaseModel):
    score: int = Field(ge=0, le=100)
    summary: str
    rationale: list[str] = Field(min_length=1)
    sections: ResumeSections = Field(default_factory=ResumeSections)


class ReviewResult(BaseModel):
    score: int = Field(ge=0, le=100)
    band: str
    summary: str
    rationale: list[str]
    sections: ResumeSections
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    extracted_text: str | None = None
    breakdown: ScoreBreakdown | None = None
    analyzer_used: str = "rule"
    fallback_reason: str | None = None


def score_to_band(score: int) -> str:
    if score < 40:
        return "Low likelihood"
    if score < 70:
        return "Moderate likelihood"
    return "Strong likelihood"
