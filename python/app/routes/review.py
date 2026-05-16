from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.dependencies import get_cached_settings, get_feature_flags, get_review_service
from app.feature_flags import (
    FeatureFlags,
    _truthy,
    available_flags,
    flags_to_cookie_values,
    resolve_feature_flags,
)
from app.models.review import ReviewContext, ReviewResult
from app.services.review_service import ResumeReviewService, parse_required_skills

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _apply_flag_cookies(response: HTMLResponse, flags: FeatureFlags) -> HTMLResponse:
    for key, value in flags_to_cookie_values(flags).items():
        response.set_cookie(key=key, value=value, max_age=60 * 60 * 24 * 30, samesite="lax")
    return response


@router.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/review", status_code=302)


@router.get("/review", response_class=HTMLResponse)
async def review_form(
    request: Request,
    flags: FeatureFlags = Depends(get_feature_flags),
) -> HTMLResponse:
    settings = get_cached_settings()
    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={
            "title": "Resume Reviewer",
            "flags": flags,
            "feature_flag_ui_enabled": settings.feature_flag_ui_enabled,
            "available_flags": available_flags(settings),
        },
    )


@router.post("/review", response_class=HTMLResponse)
async def review_submit(
    request: Request,
    resume: UploadFile = File(...),
    job_title: str = Form(""),
    required_skills: str = Form(""),
    use_llm: str | None = Form(None),
    show_extracted_text: str | None = Form(None),
    service: ResumeReviewService = Depends(get_review_service),
) -> HTMLResponse:
    settings = get_cached_settings()
    if settings.feature_flag_ui_enabled:
        flags = FeatureFlags(
            llm_analyzer=_truthy(use_llm),
            show_extracted_text=_truthy(show_extracted_text),
        )
    else:
        flags = resolve_feature_flags(settings, cookies=request.cookies)

    context = ReviewContext(
        job_title=job_title.strip() or None,
        required_skills=parse_required_skills(required_skills),
    )

    pdf_bytes = await resume.read()
    result: ReviewResult = service.review(
        pdf_bytes,
        filename=resume.filename,
        context=context,
        flags=flags,
    )

    response = templates.TemplateResponse(
        request=request,
        name="review_result.html",
        context={
            "title": "Review Results",
            "result": result,
            "flags": flags,
            "feature_flag_ui_enabled": settings.feature_flag_ui_enabled,
        },
    )
    return _apply_flag_cookies(response, flags)
