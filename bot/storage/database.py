"""Управление базой данных."""
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from config import settings

# Импортируем все модели для регистрации в SQLModel.metadata
from bot.models.database import (
    User, ProcessingTask, Task, Reminder, ArchiveItem,
    DiaryEntry, WorkNote, HomeTask, StudyNote, Idea, HealthLog, FinanceTransaction
)


# Асинхронный движок
async_engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Инициализация базы данных."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Получить сессию БД."""
    async with AsyncSessionLocal() as session:
        yield session

