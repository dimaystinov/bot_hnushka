"""Модели базы данных."""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship


class TaskStatus(str, Enum):
    """Статусы задач в очереди."""
    QUEUED = "queued"
    TRANSCRIBING = "transcribing"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


class MessageType(str, Enum):
    """Типы сообщений."""
    MEETING = "meeting"
    REMINDER = "reminder"
    ARCHIVE = "archive"
    DIARY = "diary"  # Личный дневник
    WORK = "work"  # Работа / профессиональные заметки
    HOME = "home"  # Дом / бытовые дела
    STUDY = "study"  # Обучение / конспекты
    IDEAS = "ideas"  # Идеи / брейншторм
    HEALTH = "health"  # Здоровье / самочувствие
    FINANCE = "finance"  # Финансы / траты
    UNKNOWN = "unknown"


class User(SQLModel, table=True):
    """Пользователь."""
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True, index=True)
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    settings: Optional[str] = None  # JSON строка с настройками
    language: Optional[str] = Field(default="auto")  # Код языка для Whisper или "auto" для автоопределения


class ProcessingTask(SQLModel, table=True):
    """Задача обработки медиа."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    file_id: str
    file_type: str  # voice, audio, video_note
    status: TaskStatus = Field(default=TaskStatus.QUEUED, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    transcription: Optional[str] = None
    message_type: Optional[MessageType] = None
    result_data: Optional[str] = None  # JSON строка с результатом
    
    # Relationships
    user: User = Relationship()


class Task(SQLModel, table=True):
    """Задача из собрания."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed: bool = Field(default=False)
    source_processing_task_id: Optional[int] = None


class Reminder(SQLModel, table=True):
    """Напоминание."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    text: str
    reminder_date: Optional[datetime] = None
    relative_time: Optional[str] = None  # "через час", "завтра" и т.п.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notified: bool = Field(default=False)
    source_processing_task_id: Optional[int] = None


class ArchiveItem(SQLModel, table=True):
    """Архивная заметка."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    content: str
    summary: Optional[str] = None
    tags: Optional[str] = None  # JSON массив тегов
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_processing_task_id: Optional[int] = None


class DiaryEntry(SQLModel, table=True):
    """Запись в личном дневнике."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    content: str
    summary: Optional[str] = None
    thoughts: Optional[str] = None  # JSON массив мыслей
    emotions: Optional[str] = None  # JSON массив эмоций/тегов
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_processing_task_id: Optional[int] = None


class WorkNote(SQLModel, table=True):
    """Рабочая заметка."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    project_context: Optional[str] = None
    done: Optional[str] = None  # JSON массив выполненных задач
    planned: Optional[str] = None  # JSON массив запланированных задач
    problems: Optional[str] = None  # JSON массив проблем/рисков
    ideas: Optional[str] = None  # JSON массив идей
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_processing_task_id: Optional[int] = None


class HomeTask(SQLModel, table=True):
    """Бытовая задача."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    category: str  # покупки, ремонт, бытовые, семейные
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_processing_task_id: Optional[int] = None


class StudyNote(SQLModel, table=True):
    """Конспект / учебная заметка."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    topic: str
    key_points: Optional[str] = None  # JSON массив ключевых тезисов
    definitions: Optional[str] = None  # JSON массив определений
    examples: Optional[str] = None  # JSON массив примеров
    questions: Optional[str] = None  # JSON массив вопросов для самопроверки
    follow_up_tasks: Optional[str] = None  # JSON массив follow-up задач
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_processing_task_id: Optional[int] = None


class Idea(SQLModel, table=True):
    """Идея / брейншторм."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    description: Optional[str] = None
    category: Optional[str] = None  # работа/личное/проект
    next_step: Optional[str] = None  # MVP-шаг
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_processing_task_id: Optional[int] = None


class HealthLog(SQLModel, table=True):
    """Запись о здоровье."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    symptoms: Optional[str] = None  # JSON массив симптомов
    actions: Optional[str] = None  # JSON массив действий (лекарства, тренировки и т.п.)
    triggers: Optional[str] = None  # JSON массив возможных триггеров
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_processing_task_id: Optional[int] = None


class FinanceTransaction(SQLModel, table=True):
    """Финансовая операция."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    amount: float
    category: str  # доход/расход
    subcategory: Optional[str] = None  # еда, транспорт, зарплата и т.п.
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_processing_task_id: Optional[int] = None

