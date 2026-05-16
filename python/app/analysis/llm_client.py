import json
import logging

import httpx

from app.exceptions import LlmAnalyzerError

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout_seconds: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout_seconds

    def generate_json(self, prompt: str) -> dict:
        url = f"{self._base_url}/api/generate"
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            logger.warning("Ollama request failed: %s", exc)
            raise LlmAnalyzerError(
                f"LLM service unavailable at {self._base_url}. Is Ollama running?"
            ) from exc

        raw = body.get("response", "")
        if not raw:
            raise LlmAnalyzerError("LLM returned an empty response.")

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LlmAnalyzerError("LLM response was not valid JSON.") from exc

        if not isinstance(parsed, dict):
            raise LlmAnalyzerError("LLM JSON response must be an object.")
        return parsed
