from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    resume_max_file_size_bytes: int = 5_242_880
    resume_max_pages: int = 10
    llm_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3.2"
    llm_timeout_seconds: float = 90.0
    llm_max_resume_chars: int = 12_000

    # Feature flags (env defaults)
    feature_llm_analyzer: bool = False
    feature_flag_ui_enabled: bool = True
    show_extracted_text: bool = False

    skills_dictionary_path: Path = BASE_DIR / "data" / "skills_dictionary.txt"


def get_settings() -> Settings:
    return Settings()
