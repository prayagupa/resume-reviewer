class ResumeReviewerError(Exception):
    """Base error for resume review operations."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EmptyUploadError(ResumeReviewerError):
    pass


class InvalidFileTypeError(ResumeReviewerError):
    pass


class FileTooLargeError(ResumeReviewerError):
    pass


class EncryptedPdfError(ResumeReviewerError):
    pass


class UnreadablePdfError(ResumeReviewerError):
    pass


class TooManyPagesError(ResumeReviewerError):
    pass


class LlmAnalyzerError(ResumeReviewerError):
    pass
