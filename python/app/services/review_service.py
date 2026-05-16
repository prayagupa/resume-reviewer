from app.analysis.rule_based import RuleBasedAnalyzer
from app.config import Settings
from app.exceptions import EmptyUploadError, FileTooLargeError, InvalidFileTypeError
from app.extraction.pdf_extractor import PdfExtractor
from app.models.review import ReviewResult

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


class ResumeReviewService:
    def __init__(
        self,
        extractor: PdfExtractor,
        analyzer: RuleBasedAnalyzer,
        settings: Settings,
    ) -> None:
        self._extractor = extractor
        self._analyzer = analyzer
        self._settings = settings

    def review(self, pdf_bytes: bytes, filename: str | None = None) -> ReviewResult:
        validate_upload(pdf_bytes, filename, self._settings)
        text = self._extractor.extract_text(
            pdf_bytes, max_pages=self._settings.resume_max_pages
        )
        result = self._analyzer.analyze(text)

        if self._settings.show_extracted_text:
            result.extracted_text_preview = text[:500]

        return result
