from functools import lru_cache

from app.analysis.rule_based import RuleBasedAnalyzer
from app.config import Settings, get_settings
from app.extraction.pdf_extractor import PdfExtractor
from app.services.review_service import ResumeReviewService


@lru_cache
def get_cached_settings() -> Settings:
    return get_settings()


def get_review_service() -> ResumeReviewService:
    settings = get_cached_settings()
    extractor = PdfExtractor()
    analyzer = RuleBasedAnalyzer(settings.skills_dictionary_path)
    return ResumeReviewService(extractor, analyzer, settings)
