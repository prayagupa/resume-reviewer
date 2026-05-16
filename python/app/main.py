import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.exceptions import (
    EmptyUploadError,
    EncryptedPdfError,
    FileTooLargeError,
    InvalidFileTypeError,
    ResumeReviewerError,
    TooManyPagesError,
    UnreadablePdfError,
)
from app.exceptions import LlmAnalyzerError
from app.routes import api, feature_flags, review

logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Reviewer", version="0.1.0")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(review.router)
app.include_router(api.router)
app.include_router(feature_flags.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def _error_payload(exc: ResumeReviewerError) -> dict[str, str]:
    return {"error": exc.message}


@app.exception_handler(EmptyUploadError)
@app.exception_handler(InvalidFileTypeError)
@app.exception_handler(FileTooLargeError)
async def handle_bad_request(request: Request, exc: ResumeReviewerError) -> JSONResponse | HTMLResponse:
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=400, content=_error_payload(exc))
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"title": "Request error", "message": exc.message},
        status_code=400,
    )


@app.exception_handler(EncryptedPdfError)
@app.exception_handler(UnreadablePdfError)
@app.exception_handler(LlmAnalyzerError)
async def handle_llm_error(request: Request, exc: ResumeReviewerError) -> JSONResponse | HTMLResponse:
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=503, content=_error_payload(exc))
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"title": "LLM unavailable", "message": exc.message},
        status_code=503,
    )


@app.exception_handler(TooManyPagesError)
async def handle_unprocessable(request: Request, exc: ResumeReviewerError) -> JSONResponse | HTMLResponse:
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=422, content=_error_payload(exc))
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"title": "Could not process PDF", "message": exc.message},
        status_code=422,
    )


@app.exception_handler(RequestValidationError)
async def handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse | HTMLResponse:
    message = "Please upload a PDF file."
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=400, content={"error": message, "detail": exc.errors()})
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"title": "Request error", "message": message},
        status_code=400,
    )


@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse | HTMLResponse:
    logger.exception("Unexpected error during resume review")
    message = "An unexpected error occurred. Please try again."
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=500, content={"error": message})
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"title": "Server error", "message": message},
        status_code=500,
    )
