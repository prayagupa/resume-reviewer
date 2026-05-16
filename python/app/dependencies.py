from functools import lru_cache

from fastapi import Request

from app.analysis.llm_analyzer import build_llm_analyzer
from app.analysis.rule_based import RuleBasedAnalyzer
from app.config import Settings, get_settings
from app.extraction.pdf_extractor import PdfExtractor
from app.feature_flags import FeatureFlags, resolve_feature_flags
from app.services.review_service import ResumeReviewService


@lru_cache
def get_cached_settings() -> Settings:
    return get_settings()


@lru_cache
def _get_rule_analyzer() -> RuleBasedAnalyzer:
    settings = get_cached_settings()
    return RuleBasedAnalyzer(settings.skills_dictionary_path)


@lru_cache
def _get_llm_analyzer() -> object:
    settings = get_cached_settings()
    return build_llm_analyzer(settings, settings.skills_dictionary_path)


@lru_cache
def _get_extractor() -> PdfExtractor:
    return PdfExtractor()


def get_review_service() -> ResumeReviewService:
    settings = get_cached_settings()
    return ResumeReviewService(
        _get_extractor(),
        _get_rule_analyzer(),
        _get_llm_analyzer(),
        settings,
    )


def get_feature_flags(request: Request) -> FeatureFlags:
    settings = get_cached_settings()
    return resolve_feature_flags(
        settings,
        cookies=request.cookies,
        headers={k.lower(): v for k, v in request.headers.items()},
    )
