from app.analysis.resume_parser import ResumeParser
from app.analysis.scoring_engine import ScoringEngine
from app.config import BASE_DIR


def test_scoring_returns_reasonable_range(sample_resume_text: str) -> None:
    parser = ResumeParser(BASE_DIR / "data" / "skills_dictionary.txt")
    parsed = parser.parse(sample_resume_text)
    engine = ScoringEngine()

    score, breakdown, rationale = engine.score(parsed)

    assert 40 <= score <= 100
    assert breakdown.total == score
    assert len(rationale) >= 3


def test_scoring_empty_text() -> None:
    parser = ResumeParser(BASE_DIR / "data" / "skills_dictionary.txt")
    parsed = parser.parse("No sections here.")
    engine = ScoringEngine()

    score, _, rationale = engine.score(parsed)

    assert 0 <= score <= 40
    assert rationale
