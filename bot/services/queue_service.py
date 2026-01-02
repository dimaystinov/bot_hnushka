"""Сервис очереди задач."""
import asyncio
import json
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.database import ProcessingTask, TaskStatus, MessageType
from bot.services.whisper_service import WhisperService
from bot.services.llm_service import LLMClient
from config import settings
from bot.utils.logger import logger


class QueueService:
    """Сервис для управления очередью задач."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.whisper = WhisperService()
        self.llm = LLMClient()
        self._running = False
        self._worker_task = None
        self._semaphore = asyncio.Semaphore(settings.max_concurrent_tasks)
    
    async def add_task(
        self,
        user_id: int,
        file_id: str,
        file_type: str
    ) -> ProcessingTask:
        """Добавить задачу в очередь."""
        task = ProcessingTask(
            user_id=user_id,
            file_id=file_id,
            file_type=file_type,
            status=TaskStatus.QUEUED
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        logger.info(f"Задача {task.id} добавлена в очередь для пользователя {user_id}")
        return task
    
    async def get_next_task(self) -> Optional[ProcessingTask]:
        """Получить следующую задачу из очереди."""
        stmt = select(ProcessingTask).where(
            ProcessingTask.status == TaskStatus.QUEUED
        ).order_by(ProcessingTask.created_at).limit(1)
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def start_worker(self):
        """Запустить воркер обработки задач."""
        if self._running:
            logger.warning("Воркер уже запущен")
            return
        
        self._running = True
        logger.info("Воркер очереди запущен")
        
        while self._running:
            try:
                async with self._semaphore:
                    task = await self.get_next_task()
                    if task:
                        await self._process_task(task)
                    else:
                        await asyncio.sleep(2)  # Ждём, если очередь пуста
            except Exception as e:
                logger.error(f"Ошибка в воркере: {e}")
                await asyncio.sleep(5)
    
    async def stop_worker(self):
        """Остановить воркер."""
        self._running = False
        logger.info("Воркер очереди остановлен")
    
    async def _process_task(self, task: ProcessingTask):
        """Обработать задачу."""
        try:
            task.status = TaskStatus.TRANSCRIBING
            task.started_at = datetime.utcnow()
            await self.db.commit()
            
            logger.info(f"Начата обработка задачи {task.id}")
            
            # Здесь нужно скачать файл через Telegram API
            # Пока что оставляем заглушку
            # В реальной реализации нужно передать bot экземпляр
            
            # Расшифровка
            # transcription = await self.whisper.transcribe(audio_data)
            # task.transcription = transcription
            
            # Классификация
            task.status = TaskStatus.PROCESSING
            await self.db.commit()
            
            # classification = await self.llm.classify_message(transcription)
            # task.message_type = MessageType(classification["type"].lower())
            
            # Обработка в зависимости от типа
            # result = await self._process_by_type(transcription, task.message_type)
            # task.result_data = json.dumps(result)
            
            task.status = TaskStatus.DONE
            task.completed_at = datetime.utcnow()
            await self.db.commit()
            
            logger.info(f"Задача {task.id} успешно обработана")
            
        except Exception as e:
            logger.error(f"Ошибка обработки задачи {task.id}: {e}")
            task.status = TaskStatus.ERROR
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            await self.db.commit()
    
    async def _process_by_type(self, transcription: str, message_type: MessageType) -> dict:
        """Обработать в зависимости от типа сообщения."""
        if message_type == MessageType.MEETING:
            return await self.llm.process_meeting(transcription)
        elif message_type == MessageType.REMINDER:
            return await self.llm.process_reminder(transcription)
        elif message_type == MessageType.ARCHIVE:
            return await self.llm.process_archive(transcription)
        else:
            return {"type": "unknown", "transcription": transcription}

