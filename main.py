"""Главный файл запуска бота."""
import asyncio
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings
from bot.utils.logger import logger
from bot.handlers import common, media
from bot.storage.database import init_db
from bot.storage.appwrite_storage import get_appwrite_storage


async def main():
    """Главная функция запуска бота."""
    # Инициализация БД
    if settings.use_appwrite:
        logger.info("Инициализация Appwrite...")
        appwrite = get_appwrite_storage()
        if appwrite:
            appwrite.init_database()
            logger.info("Appwrite инициализирован")
        else:
            logger.warning("Appwrite не настроен, используем SQLite")
            await init_db()
            logger.info("База данных SQLite инициализирована")
    else:
        logger.info("Инициализация базы данных SQLite...")
        await init_db()
        logger.info("База данных инициализирована")
    
    # Создание бота и диспетчера
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(common.router)
    dp.include_router(media.router)
    
    logger.info("Бот запущен")
    
    # Запуск polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
        sys.exit(0)

