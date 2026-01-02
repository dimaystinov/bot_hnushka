"""Сервис для работы с LLM."""
import json
from typing import Optional, Dict, Any, List
from enum import Enum

import httpx

from config import settings
from bot.utils.logger import logger


class LLMProvider(str, Enum):
    """Провайдеры LLM."""
    FREEWEN = "freewen"
    OPENROUTER = "openrouter"
    LOCAL = "local"


class LLMClient:
    """Клиент для работы с различными LLM."""
    
    def __init__(self):
        # Приоритет: OpenRouter (Gemini бесплатно) -> Ollama (локальный Qwen)
        self.provider_priority = [
            LLMProvider.OPENROUTER,  # Приоритет: OpenRouter с Gemini (бесплатно)
            LLMProvider.LOCAL         # Fallback: локальный Ollama (Qwen)
        ]
        self.timeout = 60.0
    
    async def _call_freewen(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Вызов FreeQwenApi."""
        try:
            # FreeQwenApi использует OpenAI-совместимый эндпоинт
            url = f"{settings.freewen_api_url}/api/chat/completions"
            headers = {
                "Content-Type": "application/json"
            }
            if settings.freewen_api_key:
                headers["Authorization"] = f"Bearer {settings.freewen_api_key}"
            
            payload = {
                "model": settings.freewen_model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"Ошибка вызова FreeQwenApi: {e}")
            return None
    
    async def _call_openrouter(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Вызов OpenRouter."""
        try:
            if not settings.openrouter_api_key:
                return None
            
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "HTTP-Referer": "https://github.com/your-repo",  # Опционально
                "X-Title": "Voice Bot"  # Опционально
            }
            
            payload = {
                "model": settings.openrouter_model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"Ошибка вызова OpenRouter: {e}")
            return None
    
    async def _call_local(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Вызов локальной LLM."""
        try:
            if settings.local_llm_api_type == "ollama":
                url = f"{settings.local_llm_url}/api/chat"
                payload = {
                    "model": settings.local_llm_model,
                    "messages": messages,
                    "stream": False
                }
            elif settings.local_llm_api_type in ["lmstudio", "textgen"]:
                # OpenAI-совместимый API
                url = f"{settings.local_llm_url}/v1/chat/completions"
                payload = {
                    "model": settings.local_llm_model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            else:
                logger.error(f"Неизвестный тип локального API: {settings.local_llm_api_type}")
                return None
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                if settings.local_llm_api_type == "ollama":
                    return data.get("message", {}).get("content", "")
                else:
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"Ошибка вызова локальной LLM: {e}")
            return None
    
    async def chat(self, messages: List[Dict[str, str]], provider: Optional[LLMProvider] = None) -> Optional[str]:
        """
        Вызвать LLM с автоматическим fallback.
        
        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]
            provider: Принудительный выбор провайдера (опционально)
        
        Returns:
            Ответ от LLM или None
        """
        if provider:
            providers = [provider]
        else:
            providers = self.provider_priority
        
        for prov in providers:
            logger.info(f"Попытка вызова LLM через {prov.value}")
            
            if prov == LLMProvider.FREEWEN:
                result = await self._call_freewen(messages)
            elif prov == LLMProvider.OPENROUTER:
                result = await self._call_openrouter(messages)
            elif prov == LLMProvider.LOCAL:
                result = await self._call_local(messages)
            else:
                continue
            
            if result:
                logger.info(f"Успешный ответ от {prov.value}")
                return result
        
        logger.error("Все провайдеры LLM недоступны")
        return None
    
    async def classify_message(self, transcription: str) -> Dict[str, Any]:
        """
        Классифицировать тип сообщения.
        
        Returns:
            Словарь с типом и дополнительной информацией
        """
        prompt = f"""Проанализируй следующую расшифровку аудио и определи её тип.

Типы сообщений:
1. MEETING - собрание/митинг: диалог нескольких людей, обсуждение задач, планов
2. REMINDER - напоминание: короткая фраза с явным будущим действием/датой ("напомни", "завтра", "через час")
3. ARCHIVE - архив: описательная речь о том, что сделано/делается, без явного запроса
4. DIARY - личный дневник: поток мыслей, переживаний, планов ("сегодня было...", "я чувствую...", "надо подумать о...")
5. WORK - работа: наброски по задачам, размышления о проекте, технические идеи, ретро, ревью дня
6. HOME - дом/быт: домашние дела ("купить", "починить", "убрать", "сделать с детьми/родителями")
7. STUDY - обучение: конспекты с лекций, курсов, книг, статей
8. IDEAS - идеи/брейншторм: поток идей, стартапы, фичи, сценарии, "надо бы сделать..."
9. HEALTH - здоровье: заметки о самочувствии ("плохо спал", "болит голова", "выпил таблетки", "тренировка")
10. FINANCE - финансы: надиктовка трат и доходов ("потратил столько-то на...", "получил зарплату...")

Расшифровка:
{transcription}

Верни JSON в формате:
{{
    "type": "MEETING" | "REMINDER" | "ARCHIVE" | "DIARY" | "WORK" | "HOME" | "STUDY" | "IDEAS" | "HEALTH" | "FINANCE",
    "confidence": 0.0-1.0,
    "reason": "краткое объяснение"
}}"""
        
        messages = [
            {"role": "system", "content": "Ты помощник для классификации сообщений. Отвечай только валидным JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat(messages)
        if not response:
            return {"type": "UNKNOWN", "confidence": 0.0, "reason": "LLM недоступен"}
        
        try:
            # Пытаемся извлечь JSON из ответа
            response = response.strip()
            if response.startswith("```"):
                # Убираем markdown код блоки
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            result = json.loads(response)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON от LLM: {e}, ответ: {response}")
            return {"type": "UNKNOWN", "confidence": 0.0, "reason": "Ошибка парсинга ответа"}
    
    async def process_meeting(self, transcription: str) -> Dict[str, Any]:
        """Обработать собрание и извлечь задачи."""
        prompt = f"""Проанализируй расшифровку собрания и создай структурированный отчёт.

Расшифровка:
{transcription}

Создай JSON в формате:
{{
    "title": "краткий заголовок встречи",
    "summary": "краткое резюме (2-3 предложения)",
    "participants": ["имя1", "имя2", ...],
    "tasks": [
        {{
            "title": "название задачи",
            "assignee": "исполнитель (если известен)",
            "due_date": "срок (если упомянут)",
            "description": "описание"
        }}
    ],
    "decisions": ["решение1", "решение2", ...],
    "key_points": ["важный момент1", "важный момент2", ...]
}}"""
        
        messages = [
            {"role": "system", "content": "Ты помощник для анализа собраний. Отвечай только валидным JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat(messages)
        if not response:
            return {"error": "LLM недоступен"}
        
        try:
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            result = json.loads(response)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}, ответ: {response}")
            return {"error": "Ошибка обработки"}
    
    async def process_reminder(self, transcription: str) -> Dict[str, Any]:
        """Обработать напоминание."""
        prompt = f"""Проанализируй расшифровку напоминания и извлеки информацию.

Расшифровка:
{transcription}

Создай JSON в формате:
{{
    "text": "текст напоминания",
    "reminder_date": "дата/время если указано явно (YYYY-MM-DD HH:MM или null)",
    "relative_time": "относительное время если указано ('через час', 'завтра', 'через неделю' или null)",
    "needs_clarification": true/false
}}"""
        
        messages = [
            {"role": "system", "content": "Ты помощник для обработки напоминаний. Отвечай только валидным JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat(messages)
        if not response:
            return {"error": "LLM недоступен"}
        
        try:
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            result = json.loads(response)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}, ответ: {response}")
            return {"error": "Ошибка обработки"}
    
    async def process_archive(self, transcription: str) -> Dict[str, Any]:
        """Обработать архивную заметку."""
        prompt = f"""Преобразуй расшифровку в структурированную статью/заметку.

Расшифровка:
{transcription}

Создай JSON в формате:
{{
    "title": "заголовок статьи",
    "summary": "краткое резюме (2-3 предложения)",
    "content": "структурированный текст с подзаголовками и списками (markdown формат)",
    "tags": ["тег1", "тег2", ...]
}}"""
        
        messages = [
            {"role": "system", "content": "Ты помощник для создания структурированных заметок. Отвечай только валидным JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat(messages)
        if not response:
            return {"error": "LLM недоступен"}
        
        try:
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            result = json.loads(response)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}, ответ: {response}")
            return {"error": "Ошибка обработки"}

