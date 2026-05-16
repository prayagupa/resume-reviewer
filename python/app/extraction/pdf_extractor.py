import re
from io import BytesIO

import pdfplumber

from app.exceptions import EncryptedPdfError, TooManyPagesError, UnreadablePdfError


def normalize_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class PdfExtractor:
    def extract_text(self, pdf_bytes: bytes, max_pages: int = 10) -> str:
        if not pdf_bytes:
            raise UnreadablePdfError("PDF file is empty.")

        try:
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                if getattr(pdf, "is_encrypted", False):
                    raise EncryptedPdfError("Cannot read password-protected PDFs.")

                page_count = len(pdf.pages)
                if page_count == 0:
                    raise UnreadablePdfError("PDF contains no pages.")
                if page_count > max_pages:
                    raise TooManyPagesError(
                        f"PDF exceeds maximum of {max_pages} pages."
                    )

                chunks: list[str] = []
                for page in pdf.pages[:max_pages]:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        chunks.append(page_text)

                text = normalize_text("\n".join(chunks))
                if len(text) < 50:
                    raise UnreadablePdfError(
                        "This PDF appears to be image-only; please upload a text-based PDF."
                    )
                return text
        except (EncryptedPdfError, TooManyPagesError, UnreadablePdfError):
            raise
        except Exception as exc:
            message = str(exc).lower()
            if "password" in message or "encrypted" in message:
                raise EncryptedPdfError("Cannot read password-protected PDFs.") from exc
            raise UnreadablePdfError("Unable to read PDF content.") from exc
