"""Конфигурация бота."""
import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Telegram Bot
    bot_token: str
    
    # Whisper
    whisper_model: str = "medium"
    whisper_device: str = "cpu"
    use_openai_whisper_api: bool = False
    openai_api_key: Optional[str] = None
    
    # FreeQwenApi
    freewen_api_url: str = "http://localhost:3264"
    freewen_api_key: Optional[str] = None
    freewen_model: str = "qwen-max-latest"
    
    # OpenRouter
    openrouter_api_key: Optional[str] = None
    # Бесплатные модели: google/gemini-2.0-flash-exp:free (лучшая), meta-llama/llama-3.3-70b-instruct:free, qwen/qwen-2.5-vl-7b-instruct:free
    openrouter_model: str = "google/gemini-2.0-flash-exp:free"  # Бесплатная модель через OpenRouter
    
    # Local LLM
    local_llm_url: str = "http://localhost:11434"
    local_llm_model: str = "qwen:4b"  # Qwen 2.5 4B через Ollama (локальный fallback)
    local_llm_api_type: str = "ollama"  # ollama, lmstudio, textgen
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./bot.db"
    use_appwrite: bool = False  # Использовать Appwrite вместо SQLite
    
    # Appwrite (optional)
    appwrite_endpoint: Optional[str] = None
    appwrite_project_id: Optional[str] = None
    appwrite_api_key: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    # Queue settings
    max_concurrent_tasks: int = 3
    max_tasks_per_user: int = 5


# Глобальный экземпляр настроек
settings = Settings()

# Путь к корню проекта
BASE_DIR = Path(__file__).parent

