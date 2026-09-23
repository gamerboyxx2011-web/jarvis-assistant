import pytest
from pydantic import ValidationError

from app.config import Settings


def test_valid_configuration(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "valid-key")
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "9000")
    settings = Settings(_env_file=None)
    assert settings.NVIDIA_API_KEY == "valid-key"
    assert settings.HOST == "127.0.0.1"
    assert settings.PORT == 9000


def test_missing_api_key_is_clear(monkeypatch):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    with pytest.raises(ValidationError, match="NVIDIA_API_KEY"):
        Settings(_env_file=None)


def test_placeholder_api_key_is_rejected(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "your_nvidia_api_key_here")
    with pytest.raises(ValidationError, match="valid NVIDIA NIM API key"):
        Settings(_env_file=None)
