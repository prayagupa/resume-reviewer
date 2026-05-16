from pathlib import Path

from app.analysis.resume_parser import ResumeParser
from app.config import BASE_DIR


def test_parse_detects_contact_skills_and_sections(sample_resume_text: str) -> None:
    parser = ResumeParser(BASE_DIR / "data" / "skills_dictionary.txt")
    parsed = parser.parse(sample_resume_text)

    assert parsed.email == "jane.doe@example.com"
    assert parsed.has_experience_section
    assert parsed.has_education_section
    assert parsed.has_skills_section
    assert "Python" in parsed.sections.skills
    assert parsed.years_experience >= 4
    assert parsed.action_verb_count >= 2
    assert parsed.metric_count >= 1


def test_parse_fixture_file() -> None:
    text = (Path(__file__).parent / "fixtures" / "sample_resume.txt").read_text(encoding="utf-8")
    parser = ResumeParser(BASE_DIR / "data" / "skills_dictionary.txt")
    parsed = parser.parse(text)

    assert "Python" in parsed.sections.skills
    assert parsed.has_experience_section
