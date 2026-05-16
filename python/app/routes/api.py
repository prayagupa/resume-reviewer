from fastapi import APIRouter, Depends, File, Form, Header, Request, UploadFile

from app.dependencies import get_cached_settings, get_review_service
from app.feature_flags import resolve_feature_flags
from app.models.review import ReviewContext, ReviewResult
from app.services.review_service import ResumeReviewService, parse_required_skills

router = APIRouter(prefix="/api/v1")


@router.post("/reviews", response_model=ReviewResult)
async def create_review(
    request: Request,
    resume: UploadFile = File(...),
    job_title: str | None = Form(None),
    required_skills: str | None = Form(None),
    use_llm: str | None = Form(None),
    show_extracted_text: str | None = Form(None),
    x_feature_llm: str | None = Header(None, alias="X-Feature-LLM"),
    x_feature_show_text: str | None = Header(None, alias="X-Feature-Show-Text"),
    service: ResumeReviewService = Depends(get_review_service),
) -> ReviewResult:
    settings = get_cached_settings()
    form_data = {
        k: v
        for k, v in {
            "use_llm": use_llm,
            "show_extracted_text": show_extracted_text,
        }.items()
        if v is not None
    }
    headers = {
        k: v
        for k, v in {
            "x-feature-llm": x_feature_llm,
            "x-feature-show-text": x_feature_show_text,
        }.items()
        if v is not None
    }
    flags = resolve_feature_flags(
        settings,
        cookies=request.cookies,
        form=form_data,
        headers=headers,
    )

    context = ReviewContext(
        job_title=job_title.strip() if job_title else None,
        required_skills=parse_required_skills(required_skills),
    )

    pdf_bytes = await resume.read()
    return service.review(
        pdf_bytes,
        filename=resume.filename,
        context=context,
        flags=flags,
    )
