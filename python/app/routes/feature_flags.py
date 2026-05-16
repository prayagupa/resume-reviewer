from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from app.dependencies import get_cached_settings, get_feature_flags
from app.feature_flags import (
    FeatureFlagUpdate,
    FeatureFlags,
    available_flags,
    flags_to_cookie_values,
    resolve_feature_flags,
)

router = APIRouter(prefix="/api/v1")


class FeatureFlagsResponse(BaseModel):
    effective: FeatureFlags
    available: dict[str, object]
    ui_enabled: bool


@router.get("/feature-flags", response_model=FeatureFlagsResponse)
async def get_flags(
    request: Request,
    flags: FeatureFlags = Depends(get_feature_flags),
) -> FeatureFlagsResponse:
    settings = get_cached_settings()
    return FeatureFlagsResponse(
        effective=flags,
        available=available_flags(settings),
        ui_enabled=settings.feature_flag_ui_enabled,
    )


@router.post("/feature-flags", response_model=FeatureFlagsResponse)
async def update_flags(
    update: FeatureFlagUpdate,
    request: Request,
    response: Response,
) -> FeatureFlagsResponse:
    settings = get_cached_settings()
    if not settings.feature_flag_ui_enabled:
        raise HTTPException(status_code=403, detail="Feature flag UI is disabled.")

    current = resolve_feature_flags(settings, cookies=request.cookies)
    merged = FeatureFlags(
        llm_analyzer=update.llm_analyzer if update.llm_analyzer is not None else current.llm_analyzer,
        show_extracted_text=(
            update.show_extracted_text
            if update.show_extracted_text is not None
            else current.show_extracted_text
        ),
    )

    for key, value in flags_to_cookie_values(merged).items():
        response.set_cookie(key=key, value=value, max_age=60 * 60 * 24 * 30, samesite="lax")

    return FeatureFlagsResponse(
        effective=merged,
        available=available_flags(settings),
        ui_enabled=True,
    )
