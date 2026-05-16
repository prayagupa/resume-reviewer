import pytest

from app.exceptions import UnreadablePdfError
from app.extraction.pdf_extractor import PdfExtractor


def test_extract_text_from_sample_pdf(sample_pdf_bytes: bytes) -> None:
    extractor = PdfExtractor()
    text = extractor.extract_text(sample_pdf_bytes)

    assert "Jane Doe" in text
    assert "Python" in text
    assert len(text) >= 50


def test_extract_rejects_empty_bytes() -> None:
    extractor = PdfExtractor()
    with pytest.raises(UnreadablePdfError):
        extractor.extract_text(b"")
