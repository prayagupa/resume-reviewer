from collections.abc import Mapping

from pydantic import BaseModel

from app.config import Settings


class FeatureFlags(BaseModel):
    llm_analyzer: bool = False
    show_extracted_text: bool = False


def _truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"1", "true", "on", "yes"}


def resolve_feature_flags(
    settings: Settings,
    *,
    cookies: Mapping[str, str] | None = None,
    form: Mapping[str, str] | None = None,
    headers: Mapping[str, str] | None = None,
) -> FeatureFlags:
    """Merge env defaults with cookie/form/header overrides (when UI dev mode is on)."""
    llm = settings.feature_llm_analyzer
    show_text = settings.show_extracted_text

    if settings.feature_flag_ui_enabled:
        if cookies:
            if "ff_llm" in cookies:
                llm = _truthy(cookies["ff_llm"])
            if "ff_show_text" in cookies:
                show_text = _truthy(cookies["ff_show_text"])

        if form:
            if "use_llm" in form:
                llm = _truthy(form.get("use_llm"))
            if "show_extracted_text" in form:
                show_text = _truthy(form.get("show_extracted_text"))

        if headers:
            if "x-feature-llm" in headers:
                llm = _truthy(headers["x-feature-llm"])
            if "x-feature-show-text" in headers:
                show_text = _truthy(headers["x-feature-show-text"])

    if llm and not settings.feature_llm_analyzer and not settings.feature_flag_ui_enabled:
        llm = False

    return FeatureFlags(llm_analyzer=llm, show_extracted_text=show_text)


class FeatureFlagUpdate(BaseModel):
    llm_analyzer: bool | None = None
    show_extracted_text: bool | None = None


def flags_to_cookie_values(flags: FeatureFlags) -> dict[str, str]:
    return {
        "ff_llm": "1" if flags.llm_analyzer else "0",
        "ff_show_text": "1" if flags.show_extracted_text else "0",
    }


def available_flags(settings: Settings) -> dict[str, object]:
    return {
        "llm_analyzer": {
            "enabled": settings.feature_llm_analyzer,
            "ui_toggle": settings.feature_flag_ui_enabled,
            "description": "Use Ollama LLM for resume analysis (Phase 3)",
        },
        "show_extracted_text": {
            "enabled": settings.show_extracted_text,
            "ui_toggle": settings.feature_flag_ui_enabled,
            "description": "Show full extracted PDF text on results page",
        },
    }
