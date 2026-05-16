from fastapi import APIRouter, Depends, File, UploadFile

from app.dependencies import get_review_service
from app.models.review import ReviewResult
from app.services.review_service import ResumeReviewService

router = APIRouter(prefix="/api/v1")


@router.post("/reviews", response_model=ReviewResult)
async def create_review(
    resume: UploadFile = File(...),
    service: ResumeReviewService = Depends(get_review_service),
) -> ReviewResult:
    pdf_bytes = await resume.read()
    return service.review(pdf_bytes, filename=resume.filename)
