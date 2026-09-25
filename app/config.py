"""JARVIS AI Assistant V3 configuration."""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.providers.model_catalog import DEFAULT_MODEL_ID
class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env",env_file_encoding="utf-8",extra="ignore")
    APP_NAME:str="JARVIS AI Assistant V3"
    VERSION:str="0.1.0"
    HOST:str="0.0.0.0"
    PORT:int=Field(default=8000,ge=1,le=65535)
    HISTORY_DB_PATH:str="jarvis_history.db"
    NVIDIA_API_KEY:str=Field(min_length=1)
    NVIDIA_API_BASE_URL:str="https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL:str=DEFAULT_MODEL_ID
    OPENAI_API_KEY:str=""
    OPENAI_API_BASE_URL:str="https://api.openai.com/v1"
    OPENAI_STT_MODEL:str="whisper-1"
    OPENAI_TTS_MODEL:str="tts-1"
    OPENAI_TTS_VOICE:str="alloy"
    OPENAI_TTS_FORMAT:str="mp3"
    OPENAI_SPEECH_TIMEOUT:float=Field(default=60.0,gt=0)
    VOICE_MAX_RECORDING_SECONDS:float=Field(default=60.0,gt=0,le=60.0)
    VOICE_MAX_UPLOAD_BYTES:int=Field(default=25*1024*1024,ge=1)
    VOICE_TTS_PHRASE_CHARS:int=Field(default=240,ge=40,le=1000)
    @field_validator("NVIDIA_API_KEY")
    @classmethod
    def validate_nvidia_api_key(cls,value:str)->str:
        value=value.strip()
        if not value or value=="your_nvidia_api_key_here": raise ValueError("NVIDIA_API_KEY must contain a valid NVIDIA NIM API key")
        return value
settings=Settings()
