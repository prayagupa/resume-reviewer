from typing import Protocol

from app.models.review import ReviewContext, ReviewResult


class ResumeAnalyzer(Protocol):
    def analyze(self, text: str, context: ReviewContext | None = None) -> ReviewResult: ...
