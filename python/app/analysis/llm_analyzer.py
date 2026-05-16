import json
import logging
from pathlib import Path

from pydantic import ValidationError

from app.analysis.llm_client import OllamaClient
from app.analysis.rule_based import RuleBasedAnalyzer
from app.config import Settings
from app.exceptions import LlmAnalyzerError
from app.models.review import LlmReviewOutput, ReviewContext, ReviewResult, score_to_band

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a hiring-manager assistant reviewing resumes.
Return ONLY valid JSON matching this schema (no markdown):
{
  "score": <integer 0-100>,
  "summary": "<2-4 sentence candidate overview>",
  "rationale": ["<bullet>", "..."],
  "sections": {
    "skills": ["..."],
    "education": ["..."],
    "experience_titles": ["..."]
  }
}
Score how likely a hiring manager shortlists this resume. Be constructive and specific."""


class LlmAnalyzer:
    def __init__(
        self,
        client: OllamaClient,
        settings: Settings,
        fallback: RuleBasedAnalyzer,
    ) -> None:
        self._client = client
        self._settings = settings
        self._fallback = fallback

    def analyze(self, text: str, context: ReviewContext | None = None) -> ReviewResult:
        context = context or ReviewContext()
        prompt = self._build_prompt(text, context)

        try:
            raw = self._client.generate_json(prompt)
            output = LlmReviewOutput.model_validate(raw)
            return ReviewResult(
                score=output.score,
                band=score_to_band(output.score),
                summary=output.summary,
                rationale=output.rationale[:5],
                sections=output.sections,
                analyzer_used="llm",
            )
        except (LlmAnalyzerError, ValidationError) as exc:
            logger.warning("LLM analysis failed, falling back to rules: %s", exc)
            result = self._fallback.analyze(text, context)
            result.analyzer_used = "rule"
            result.fallback_reason = (
                exc.message if isinstance(exc, LlmAnalyzerError) else str(exc)
            )
            return result

    def _build_prompt(self, text: str, context: ReviewContext) -> str:
        truncated = text[: self._settings.llm_max_resume_chars]
        job_block = ""
        if context.job_title:
            job_block += f"\nTarget job title: {context.job_title}"
        if context.required_skills:
            job_block += f"\nRequired skills: {', '.join(context.required_skills)}"

        return (
            f"{SYSTEM_PROMPT}{job_block}\n\n"
            f"Resume text:\n{truncated}\n\n"
            "JSON:"
        )


def build_llm_analyzer(settings: Settings, skills_path: Path) -> LlmAnalyzer:
    client = OllamaClient(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        timeout_seconds=settings.llm_timeout_seconds,
    )
    fallback = RuleBasedAnalyzer(skills_path)
    return LlmAnalyzer(client, settings, fallback)
