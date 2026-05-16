from app.analysis.llm_analyzer import LlmAnalyzer
from app.analysis.rule_based import RuleBasedAnalyzer
from app.config import Settings
from app.exceptions import EmptyUploadError, FileTooLargeError, InvalidFileTypeError
from app.extraction.pdf_extractor import PdfExtractor
from app.feature_flags import FeatureFlags
from app.models.review import ReviewContext, ReviewResult

PDF_MAGIC = b"%PDF"


def validate_upload(pdf_bytes: bytes, filename: str | None, settings: Settings) -> None:
    if not pdf_bytes:
        raise EmptyUploadError("Please select a PDF file.")

    if len(pdf_bytes) > settings.resume_max_file_size_bytes:
        raise FileTooLargeError("File exceeds maximum size.")

    if not pdf_bytes.startswith(PDF_MAGIC):
        raise InvalidFileTypeError("Only PDF files are supported.")

    if filename and not filename.lower().endswith(".pdf"):
        raise InvalidFileTypeError("Only PDF files are supported.")


def parse_required_skills(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.replace(";", ",").split(",") if part.strip()]


class ResumeReviewService:
    def __init__(
        self,
        extractor: PdfExtractor,
        rule_analyzer: RuleBasedAnalyzer,
        llm_analyzer: LlmAnalyzer,
        settings: Settings,
    ) -> None:
        self._extractor = extractor
        self._rule = rule_analyzer
        self._llm = llm_analyzer
        self._settings = settings

    def review(
        self,
        pdf_bytes: bytes,
        filename: str | None = None,
        *,
        context: ReviewContext | None = None,
        flags: FeatureFlags | None = None,
    ) -> ReviewResult:
        flags = flags or FeatureFlags()
        context = context or ReviewContext()

        validate_upload(pdf_bytes, filename, self._settings)
        text = self._extractor.extract_text(
            pdf_bytes, max_pages=self._settings.resume_max_pages
        )

        if flags.llm_analyzer:
            result = self._llm.analyze(text, context)
        else:
            result = self._rule.analyze(text, context)

        if flags.show_extracted_text:
            result.extracted_text = text

        return result
