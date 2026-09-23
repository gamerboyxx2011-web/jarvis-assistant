"""
JARVIS AI Assistant V3 - Configuration Management
"""

import os
import sys
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "JARVIS AI Assistant V3"
    VERSION: str = "0.1.0"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # NVIDIA NIM API (OpenAI-compatible endpoint)
    NVIDIA_API_KEY: str
    NVIDIA_API_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL: str = "nvidia/nemotron-3-super-120b-a12b"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

# UNIQUE IDENTIFIER TO VERIFY THIS EXACT FILE IS LOADED
print(f"=== LOADING CONFIG FROM: {__file__} ===", file=sys.stderr)
print(f"=== LINE 8 SHOULD SHOW: from pydantic_settings import BaseSettings ===", file=sys.stderr)
