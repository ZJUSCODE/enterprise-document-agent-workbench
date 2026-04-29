from app.core.config import Settings


def test_siliconflow_provider_config() -> None:
    settings = Settings(
        AI_PROVIDER="siliconflow",
        SILICONFLOW_API_KEY="test-key",
        SILICONFLOW_MODEL="deepseek-ai/DeepSeek-V3.2",
    )

    assert settings.llm.provider == "siliconflow"
    assert settings.llm.api_key == "test-key"
    assert settings.llm.base_url == "https://api.siliconflow.cn/v1"
    assert settings.llm.model == "deepseek-ai/DeepSeek-V3.2"


def test_deepseek_provider_config() -> None:
    settings = Settings(AI_PROVIDER="deepseek", DEEPSEEK_API_KEY="test-key")

    assert settings.llm.provider == "deepseek"
    assert settings.llm.api_key == "test-key"
    assert settings.llm.base_url == "https://api.deepseek.com"
    assert settings.llm.model == "deepseek-chat"


def test_api_key_credentials_config() -> None:
    settings = Settings(
        API_AUTH_ENABLED=True,
        API_KEYS="admin-token:alice:admin|operator|reviewer,viewer-token:bob:viewer",
    )

    assert settings.api_auth_enabled is True
    assert settings.api_credentials["admin-token"].actor == "alice"
    assert settings.api_credentials["admin-token"].roles == {"admin", "operator", "reviewer"}
    assert settings.api_credentials["viewer-token"].actor == "bob"
    assert settings.api_credentials["viewer-token"].roles == {"viewer"}
