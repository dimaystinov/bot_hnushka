"""Хранилище данных через Appwrite."""
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException

from config import settings
from bot.utils.logger import logger
from bot.models.database import (
    User, ProcessingTask, Task, Reminder, ArchiveItem,
    DiaryEntry, WorkNote, HomeTask, StudyNote, Idea, HealthLog, FinanceTransaction,
    TaskStatus, MessageType
)


class AppwriteStorage:
    """Класс для работы с Appwrite как хранилищем данных."""
    
    def __init__(self):
        if not all([settings.appwrite_endpoint, settings.appwrite_project_id, settings.appwrite_api_key]):
            raise ValueError("Appwrite credentials not configured")
        
        self.client = Client()
        self.client.set_endpoint(settings.appwrite_endpoint)
        self.client.set_project(settings.appwrite_project_id)
        self.client.set_key(settings.appwrite_api_key)
        
        self.databases = Databases(self.client)
        self.database_id = "bot_database"  # ID базы данных в Appwrite
        
        # ID коллекций
        self.collections = {
            "users": "users",
            "processing_tasks": "processing_tasks",
            "tasks": "tasks",
            "reminders": "reminders",
            "archive_items": "archive_items",
            "diary_entries": "diary_entries",
            "work_notes": "work_notes",
            "home_tasks": "home_tasks",
            "study_notes": "study_notes",
            "ideas": "ideas",
            "health_logs": "health_logs",
            "finance_transactions": "finance_transactions",
        }
    
    def init_database(self):
        """Инициализация базы данных и коллекций."""
        try:
            # Создаём базу данных (если не существует)
            try:
                self.databases.get(self.database_id)
                logger.info(f"База данных {self.database_id} уже существует")
            except AppwriteException:
                self.databases.create(
                    database_id=self.database_id,
                    name="Bot Database"
                )
                logger.info(f"Создана база данных {self.database_id}")
            
            # Создаём коллекции (если не существуют)
            self._create_collections()
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Appwrite: {e}")
            raise
    
    def _create_collections(self):
        """Создать коллекции в Appwrite."""
        # Здесь можно добавить логику создания коллекций с нужными атрибутами
        # Для простоты предполагаем, что коллекции уже созданы вручную
        logger.info("Коллекции Appwrite должны быть созданы вручную через консоль")
    
    # Методы для работы с пользователями
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID."""
        try:
            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.collections["users"],
                queries=[f"equal('telegram_id', {telegram_id})"]
            )
            
            if result.get("documents"):
                doc = result["documents"][0]
                return self._doc_to_user(doc)
            return None
        except AppwriteException as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            return None
    
    async def create_user(self, user: User) -> User:
        """Создать пользователя."""
        try:
            doc = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.collections["users"],
                document_id="unique()",
                data=self._user_to_dict(user)
            )
            return self._doc_to_user(doc)
        except AppwriteException as e:
            logger.error(f"Ошибка создания пользователя: {e}")
            raise
    
    async def update_user(self, user: User) -> User:
        """Обновить пользователя."""
        try:
            doc = self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.collections["users"],
                document_id=str(user.id),
                data=self._user_to_dict(user)
            )
            return self._doc_to_user(doc)
        except AppwriteException as e:
            logger.error(f"Ошибка обновления пользователя: {e}")
            raise
    
    # Методы для работы с задачами обработки
    async def create_processing_task(self, task: ProcessingTask) -> ProcessingTask:
        """Создать задачу обработки."""
        try:
            doc = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.collections["processing_tasks"],
                document_id="unique()",
                data=self._processing_task_to_dict(task)
            )
            return self._doc_to_processing_task(doc)
        except AppwriteException as e:
            logger.error(f"Ошибка создания задачи обработки: {e}")
            raise
    
    async def update_processing_task(self, task: ProcessingTask) -> ProcessingTask:
        """Обновить задачу обработки."""
        try:
            doc = self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.collections["processing_tasks"],
                document_id=str(task.id),
                data=self._processing_task_to_dict(task)
            )
            return self._doc_to_processing_task(doc)
        except AppwriteException as e:
            logger.error(f"Ошибка обновления задачи обработки: {e}")
            raise
    
    async def get_next_processing_task(self) -> Optional[ProcessingTask]:
        """Получить следующую задачу из очереди."""
        try:
            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.collections["processing_tasks"],
                queries=[
                    "equal('status', 'queued')",
                    "orderAsc('created_at')",
                    "limit(1)"
                ]
            )
            
            if result.get("documents"):
                doc = result["documents"][0]
                return self._doc_to_processing_task(doc)
            return None
        except AppwriteException as e:
            logger.error(f"Ошибка получения задачи: {e}")
            return None
    
    # Вспомогательные методы для конвертации
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Конвертировать User в словарь для Appwrite."""
        return {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "language": user.language or "auto",
            "settings": user.settings,
            "created_at": user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat()
        }
    
    def _doc_to_user(self, doc: Dict[str, Any]) -> User:
        """Конвертировать документ Appwrite в User."""
        return User(
            id=doc.get("$id"),
            telegram_id=doc.get("telegram_id"),
            username=doc.get("username"),
            first_name=doc.get("first_name"),
            last_name=doc.get("last_name"),
            language=doc.get("language", "auto"),
            settings=doc.get("settings"),
            created_at=datetime.fromisoformat(doc.get("created_at", datetime.utcnow().isoformat()))
        )
    
    def _processing_task_to_dict(self, task: ProcessingTask) -> Dict[str, Any]:
        """Конвертировать ProcessingTask в словарь для Appwrite."""
        return {
            "user_id": task.user_id,
            "file_id": task.file_id,
            "file_type": task.file_type,
            "status": task.status.value if isinstance(task.status, TaskStatus) else task.status,
            "transcription": task.transcription,
            "message_type": task.message_type.value if isinstance(task.message_type, MessageType) else task.message_type,
            "result_data": task.result_data,
            "error_message": task.error_message,
            "created_at": task.created_at.isoformat() if task.created_at else datetime.utcnow().isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }
    
    def _doc_to_processing_task(self, doc: Dict[str, Any]) -> ProcessingTask:
        """Конвертировать документ Appwrite в ProcessingTask."""
        return ProcessingTask(
            id=doc.get("$id"),
            user_id=doc.get("user_id"),
            file_id=doc.get("file_id"),
            file_type=doc.get("file_type"),
            status=TaskStatus(doc.get("status", "queued")),
            transcription=doc.get("transcription"),
            message_type=MessageType(doc.get("message_type", "unknown")) if doc.get("message_type") else None,
            result_data=doc.get("result_data"),
            error_message=doc.get("error_message"),
            created_at=datetime.fromisoformat(doc.get("created_at", datetime.utcnow().isoformat())),
            started_at=datetime.fromisoformat(doc.get("started_at")) if doc.get("started_at") else None,
            completed_at=datetime.fromisoformat(doc.get("completed_at")) if doc.get("completed_at") else None
        )


# Глобальный экземпляр (если используется Appwrite)
appwrite_storage: Optional[AppwriteStorage] = None


def get_appwrite_storage() -> Optional[AppwriteStorage]:
    """Получить экземпляр AppwriteStorage, если настроен."""
    global appwrite_storage
    
    if appwrite_storage is None:
        if all([settings.appwrite_endpoint, settings.appwrite_project_id, settings.appwrite_api_key]):
            try:
                appwrite_storage = AppwriteStorage()
                logger.info("Appwrite storage инициализирован")
            except Exception as e:
                logger.error(f"Ошибка инициализации Appwrite: {e}")
                return None
    
    return appwrite_storage

