from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.dependencies import get_cached_settings, get_review_service
from app.models.review import ReviewResult
from app.services.review_service import ResumeReviewService

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/review", status_code=302)


@router.get("/review", response_class=HTMLResponse)
async def review_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={"title": "Resume Reviewer"},
    )


@router.post("/review", response_class=HTMLResponse)
async def review_submit(
    request: Request,
    resume: UploadFile = File(...),
    service: ResumeReviewService = Depends(get_review_service),
) -> HTMLResponse:
    pdf_bytes = await resume.read()
    result: ReviewResult = service.review(pdf_bytes, filename=resume.filename)
    settings = get_cached_settings()

    return templates.TemplateResponse(
        request=request,
        name="review_result.html",
        context={
            "title": "Review Results",
            "result": result,
            "show_extracted_text": settings.show_extracted_text,
        },
    )
