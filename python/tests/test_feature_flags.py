from app.config import Settings
from app.feature_flags import FeatureFlags, resolve_feature_flags


def test_resolve_defaults_from_env() -> None:
    settings = Settings(feature_llm_analyzer=False, show_extracted_text=False)
    flags = resolve_feature_flags(settings)
    assert flags == FeatureFlags(llm_analyzer=False, show_extracted_text=False)


def test_ui_cookie_overrides() -> None:
    settings = Settings(feature_llm_analyzer=False, feature_flag_ui_enabled=True)
    flags = resolve_feature_flags(settings, cookies={"ff_llm": "1", "ff_show_text": "0"})
    assert flags.llm_analyzer is True
    assert flags.show_extracted_text is False


def test_api_header_override() -> None:
    settings = Settings(feature_llm_analyzer=False, feature_flag_ui_enabled=True)
    flags = resolve_feature_flags(settings, headers={"x-feature-llm": "true"})
    assert flags.llm_analyzer is True
