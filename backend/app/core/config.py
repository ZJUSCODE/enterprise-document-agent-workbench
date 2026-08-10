from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass(frozen=True)
class LlmProviderConfig:
    provider: str
    api_key: str | None
    base_url: str | None
    model: str


@dataclass(frozen=True)
class ApiCredential:
    token: str
    actor: str
    roles: set[str]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Enterprise Document Workflow Agent"
    app_env: str = "development"
    api_prefix: str = "/api"
    cors_origins: str = "http://localhost:4173,http://127.0.0.1:4173,http://localhost:5174,http://127.0.0.1:5174"
    api_auth_enabled: bool = Field(default=False, alias="API_AUTH_ENABLED")
    api_keys: str = Field(default="", alias="API_KEYS")

    database_url: str = Field(default="sqlite:///./storage/app.db", alias="DATABASE_URL")

    queue_backend: str = Field(default="inline", alias="QUEUE_BACKEND")
    celery_broker_url: str = Field(default="redis://localhost:6379/0", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/1", alias="CELERY_RESULT_BACKEND")

    storage_backend: str = Field(default="local", alias="STORAGE_BACKEND")
    local_storage_dir: Path = Field(default=Path("storage"), alias="LOCAL_STORAGE_DIR")
    minio_endpoint: str | None = Field(default=None, alias="MINIO_ENDPOINT")
    minio_access_key: str | None = Field(default=None, alias="MINIO_ACCESS_KEY")
    minio_secret_key: str | None = Field(default=None, alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field(default="document-workflow", alias="MINIO_BUCKET")
    minio_secure: bool = Field(default=False, alias="MINIO_SECURE")

    ocr_enabled: bool = Field(default=True, alias="OCR_ENABLED")
    ocr_languages: str = Field(default="chi_sim+eng", alias="OCR_LANGUAGES")
    ocr_min_text_length: int = Field(default=40, alias="OCR_MIN_TEXT_LENGTH")
    ocr_max_pdf_pages: int = Field(default=5, alias="OCR_MAX_PDF_PAGES")

    ai_provider: str = Field(default="openai", alias="AI_PROVIDER")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: str | None = Field(default=None, alias="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")

    siliconflow_api_key: str | None = Field(default=None, alias="SILICONFLOW_API_KEY")
    siliconflow_base_url: str = Field(default="https://api.siliconflow.cn/v1", alias="SILICONFLOW_BASE_URL")
    siliconflow_model: str = Field(default="deepseek-ai/DeepSeek-V3.2", alias="SILICONFLOW_MODEL")

    deepseek_api_key: str | None = Field(default=None, alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", alias="DEEPSEEK_BASE_URL")
    deepseek_model: str = Field(default="deepseek-chat", alias="DEEPSEEK_MODEL")

    openai_timeout_seconds: int = Field(default=45, alias="OPENAI_TIMEOUT_SECONDS")
    rag_chunk_size: int = Field(default=900, alias="RAG_CHUNK_SIZE")
    rag_chunk_overlap: int = Field(default=120, alias="RAG_CHUNK_OVERLAP")
    rag_default_top_k: int = Field(default=5, alias="RAG_DEFAULT_TOP_K")

    approval_required: bool = Field(default=True, alias="APPROVAL_REQUIRED")
    max_task_retries: int = Field(default=2, alias="MAX_TASK_RETRIES")
    default_actor: str = Field(default="system", alias="DEFAULT_ACTOR")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def upload_dir(self) -> Path:
        return self.local_storage_dir / "uploads"

    @property
    def export_dir(self) -> Path:
        return self.local_storage_dir / "exports"

    @property
    def temp_dir(self) -> Path:
        return self.local_storage_dir / "tmp"

    @property
    def api_credentials(self) -> dict[str, ApiCredential]:
        credentials: dict[str, ApiCredential] = {}
        for raw_item in self.api_keys.split(","):
            item = raw_item.strip()
            if not item:
                continue
            parts = [part.strip() for part in item.split(":")]
            token = parts[0] if parts else ""
            if not token:
                continue
            actor = parts[1] if len(parts) >= 2 and parts[1] else "api-user"
            roles = {role.strip() for role in (parts[2] if len(parts) >= 3 else "viewer").split("|") if role.strip()}
            credentials[token] = ApiCredential(token=token, actor=actor, roles=roles or {"viewer"})
        return credentials

    @property
    def llm(self) -> LlmProviderConfig:
        provider = self.ai_provider.lower().strip()
        if provider == "siliconflow":
            return LlmProviderConfig(
                provider=provider,
                api_key=self._clean_secret(self.siliconflow_api_key),
                base_url=self.siliconflow_base_url,
                model=self.siliconflow_model,
            )
        if provider == "deepseek":
            return LlmProviderConfig(
                provider=provider,
                api_key=self._clean_secret(self.deepseek_api_key),
                base_url=self.deepseek_base_url,
                model=self.deepseek_model,
            )
        return LlmProviderConfig(
            provider="openai",
            api_key=self._clean_secret(self.openai_api_key),
            base_url=self._clean_secret(self.openai_base_url),
            model=self.openai_model,
        )

    def _clean_secret(self, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.export_dir.mkdir(parents=True, exist_ok=True)
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    return settings
