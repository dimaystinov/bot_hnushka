"""Утилиты для работы с языками."""
from typing import Dict, Optional

# 15 самых популярных языков
SUPPORTED_LANGUAGES: Dict[str, str] = {
    "auto": "Автоопределение",
    "ru": "Русский",
    "en": "English",
    "zh": "中文",
    "es": "Español",
    "ar": "العربية",
    "pt": "Português",
    "ja": "日本語",
    "de": "Deutsch",
    "fr": "Français",
    "ko": "한국어",
    "it": "Italiano",
    "tr": "Türkçe",
    "hi": "हिन्दी",
    "pl": "Polski",
    "nl": "Nederlands",
}


def get_language_name(code: str) -> str:
    """Получить название языка по коду."""
    return SUPPORTED_LANGUAGES.get(code, code)


def is_valid_language(code: str) -> bool:
    """Проверить, является ли код валидным языком."""
    return code in SUPPORTED_LANGUAGES


def get_language_for_whisper(code: str) -> Optional[str]:
    """Получить код языка для Whisper (None для автоопределения)."""
    if code == "auto" or not code:
        return None
    return code if is_valid_language(code) else None

