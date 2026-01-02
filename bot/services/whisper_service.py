"""Сервис для расшифровки аудио через Whisper."""
import io
import asyncio
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from faster_whisper import WhisperModel
from openai import OpenAI

from config import settings
from bot.utils.logger import logger


class WhisperService:
    """Сервис для расшифровки аудио."""
    
    def __init__(self):
        self.model = None
        self.openai_client = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        
        if settings.use_openai_whisper_api:
            if settings.openai_api_key:
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                logger.info("Используется OpenAI Whisper API")
            else:
                logger.warning("OpenAI API key не указан, используем локальный Whisper")
                self._init_local_model()
        else:
            self._init_local_model()
    
    def _init_local_model(self):
        """Инициализация локальной модели Whisper."""
        try:
            device = "cuda" if settings.whisper_device == "cuda" else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            
            self.model = WhisperModel(
                settings.whisper_model,
                device=device,
                compute_type=compute_type
            )
            logger.info(f"Локальная модель Whisper загружена: {settings.whisper_model} на {device}")
        except Exception as e:
            logger.error(f"Ошибка загрузки локальной модели Whisper: {e}")
            raise
    
    async def transcribe(self, audio_data: bytes, language: Optional[str] = None, progress_callback=None) -> str:
        """
        Расшифровать аудио.
        
        Args:
            audio_data: Байты аудио файла
            language: Язык (опционально, для автоопределения - None)
        
        Returns:
            Текст расшифровки
        """
        try:
            if self.openai_client:
                # Используем OpenAI API
                audio_file = io.BytesIO(audio_data)
                audio_file.name = "audio.ogg"
                
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
                return transcript.text
            else:
                # Используем локальную модель (синхронный вызов в executor)
                audio_file = io.BytesIO(audio_data)
                
                # Функция для отслеживания прогресса
                def transcribe_with_progress():
                    segments, info = self.model.transcribe(
                        audio_file,
                        language=language,
                        beam_size=5
                    )
                    return segments, info
                
                loop = asyncio.get_event_loop()
                segments, info = await loop.run_in_executor(
                    self.executor,
                    transcribe_with_progress
                )
                
                # Собираем текст из сегментов с отслеживанием прогресса
                text_parts = []
                total_segments = 0
                processed_segments = 0
                
                # Сначала считаем общее количество сегментов
                segments_list = list(segments)
                total_segments = len(segments_list)
                
                for i, segment in enumerate(segments_list):
                    text_parts.append(segment.text)
                    processed_segments = i + 1
                    
                    # Обновляем прогресс каждые 10% или каждые 5 сегментов
                    if progress_callback and (processed_segments % max(1, total_segments // 10) == 0 or processed_segments % 5 == 0):
                        progress = int((processed_segments / total_segments) * 100) if total_segments > 0 else 0
                        try:
                            await progress_callback(progress)
                        except Exception as e:
                            logger.warning(f"Ошибка обновления прогресса: {e}")
                
                full_text = " ".join(text_parts)
                logger.info(f"Расшифровка завершена, язык: {info.language}, вероятность: {info.language_probability:.2f}")
                return full_text
                
        except Exception as e:
            logger.error(f"Ошибка расшифровки аудио: {e}")
            raise

