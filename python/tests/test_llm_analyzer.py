from unittest.mock import MagicMock

import pytest

from app.analysis.llm_analyzer import LlmAnalyzer
from app.analysis.rule_based import RuleBasedAnalyzer
from app.config import Settings
from app.exceptions import LlmAnalyzerError
from app.models.review import ReviewContext


@pytest.fixture
def rule_analyzer(settings: Settings) -> RuleBasedAnalyzer:
    return RuleBasedAnalyzer(settings.skills_dictionary_path)


def test_llm_analyzer_success(rule_analyzer: RuleBasedAnalyzer, sample_resume_text: str) -> None:
    client = MagicMock()
    client.generate_json.return_value = {
        "score": 78,
        "summary": "Strong backend engineer with relevant stack.",
        "rationale": ["Good Python experience", "Clear career progression"],
        "sections": {
            "skills": ["Python", "AWS"],
            "education": ["B.S. Computer Science"],
            "experience_titles": ["Senior Software Engineer"],
        },
    }
    settings = Settings()
    analyzer = LlmAnalyzer(client, settings, rule_analyzer)

    result = analyzer.analyze(sample_resume_text, ReviewContext(job_title="Backend Engineer"))

    assert result.analyzer_used == "llm"
    assert result.score == 78
    assert result.fallback_reason is None
    client.generate_json.assert_called_once()


def test_llm_analyzer_falls_back_on_error(
    rule_analyzer: RuleBasedAnalyzer, sample_resume_text: str
) -> None:
    client = MagicMock()
    client.generate_json.side_effect = LlmAnalyzerError("Ollama down")
    settings = Settings()
    analyzer = LlmAnalyzer(client, settings, rule_analyzer)

    result = analyzer.analyze(sample_resume_text)

    assert result.analyzer_used == "rule"
    assert result.fallback_reason is not None
    assert result.score >= 0
