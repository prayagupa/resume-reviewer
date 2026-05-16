from io import BytesIO
from pathlib import Path

import pytest
from fpdf import FPDF

from app.analysis.llm_analyzer import build_llm_analyzer
from app.analysis.rule_based import RuleBasedAnalyzer
from app.config import BASE_DIR, Settings
from app.extraction.pdf_extractor import PdfExtractor
from app.services.review_service import ResumeReviewService

FIXTURES_DIR = Path(__file__).parent / "fixtures"

SAMPLE_RESUME_TEXT = """
Jane Doe
jane.doe@example.com | (555) 123-4567 | linkedin.com/in/janedoe

Summary
Senior software engineer with experience building scalable web services.

Skills
Python, FastAPI, AWS, Docker, PostgreSQL, Git, Kubernetes

Experience
Senior Software Engineer | Acme Corp
Jan 2020 - Present
- Built microservices handling 50k requests/day
- Led team of 4 engineers and reduced latency by 35%
- Deployed services on AWS using Docker and Kubernetes

Software Engineer | Beta LLC
Jun 2016 - Dec 2019
- Developed REST APIs with Python and PostgreSQL
- Improved deployment pipeline with CI/CD

Education
B.S. Computer Science, State University, 2016
""".strip()


@pytest.fixture
def settings() -> Settings:
    return Settings(skills_dictionary_path=BASE_DIR / "data" / "skills_dictionary.txt")


@pytest.fixture
def sample_resume_text() -> str:
    return SAMPLE_RESUME_TEXT


@pytest.fixture
def sample_pdf_bytes(sample_resume_text: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    for line in sample_resume_text.splitlines():
        pdf.multi_cell(pdf.epw, 6, line)
    out = BytesIO()
    pdf.output(out)
    return out.getvalue()


@pytest.fixture
def review_service(settings: Settings) -> ResumeReviewService:
    rule = RuleBasedAnalyzer(settings.skills_dictionary_path)
    llm = build_llm_analyzer(settings, settings.skills_dictionary_path)
    return ResumeReviewService(PdfExtractor(), rule, llm, settings)
