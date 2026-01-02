"""Общие обработчики (start, menu, help)."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from bot.utils.logger import logger
from bot.utils.languages import SUPPORTED_LANGUAGES, get_language_name
from bot.models.database import User
from bot.storage.database import AsyncSessionLocal
from sqlalchemy import select

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start."""
    await message.answer(
        "👋 Привет! Я бот для обработки голосовых сообщений.\n\n"
        "Отправь мне голосовое сообщение, аудио или видео-кружок, "
        "и я расшифрую его, проанализирую и создам структурированную заметку, "
        "задачу или напоминание.\n\n"
        "Используй /menu для доступа к меню управления."
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Показать главное меню."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Режим обработки", callback_data="menu_mode")
        ],
        [
            InlineKeyboardButton(text="✅ Мои задачи", callback_data="menu_tasks"),
            InlineKeyboardButton(text="⏰ Напоминания", callback_data="menu_reminders")
        ],
        [
            InlineKeyboardButton(text="📚 Архив", callback_data="menu_archive"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")
        ]
    ])
    
    await message.answer("📋 Главное меню:", reply_markup=keyboard)


@router.callback_query(F.data == "menu_mode")
async def callback_menu_mode(callback: CallbackQuery):
    """Меню режимов обработки."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🤖 Авто-режим", callback_data="mode_auto")
        ],
        [
            InlineKeyboardButton(text="👥 Собрание", callback_data="mode_meeting"),
            InlineKeyboardButton(text="⏰ Напоминание", callback_data="mode_reminder")
        ],
        [
            InlineKeyboardButton(text="📚 Архив", callback_data="mode_archive"),
            InlineKeyboardButton(text="📔 Дневник", callback_data="mode_diary")
        ],
        [
            InlineKeyboardButton(text="💼 Работа", callback_data="mode_work"),
            InlineKeyboardButton(text="🏠 Дом", callback_data="mode_home")
        ],
        [
            InlineKeyboardButton(text="📖 Учёба", callback_data="mode_study"),
            InlineKeyboardButton(text="💡 Идеи", callback_data="mode_ideas")
        ],
        [
            InlineKeyboardButton(text="🏥 Здоровье", callback_data="mode_health"),
            InlineKeyboardButton(text="💰 Финансы", callback_data="mode_finance")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="menu_main")
        ]
    ])
    
    await callback.message.edit_text(
        "📝 Выбери режим обработки голосовых сообщений:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "menu_tasks")
async def callback_menu_tasks(callback: CallbackQuery):
    """Показать список задач."""
    # TODO: Получить задачи из БД
    await callback.message.edit_text(
        "✅ Твои задачи:\n\n"
        "Пока что задач нет.\n\n"
        "Задачи будут создаваться автоматически из собраний.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_main")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data == "menu_reminders")
async def callback_menu_reminders(callback: CallbackQuery):
    """Показать напоминания."""
    # TODO: Получить напоминания из БД
    await callback.message.edit_text(
        "⏰ Твои напоминания:\n\n"
        "Пока что напоминаний нет.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_main")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data == "menu_archive")
async def callback_menu_archive(callback: CallbackQuery):
    """Показать архив."""
    # TODO: Получить архив из БД
    await callback.message.edit_text(
        "📚 Твой архив:\n\n"
        "Пока что архив пуст.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_main")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data == "menu_settings")
async def callback_menu_settings(callback: CallbackQuery):
    """Настройки."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌐 Язык расшифровки", callback_data="settings_language")
        ],
        [
            InlineKeyboardButton(text="🤖 Настройки моделей", callback_data="settings_models")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="menu_main")
        ]
    ])
    
    await callback.message.edit_text(
        "⚙️ Настройки:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "menu_main")
async def callback_menu_main(callback: CallbackQuery):
    """Вернуться в главное меню."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Режим обработки", callback_data="menu_mode")
        ],
        [
            InlineKeyboardButton(text="✅ Мои задачи", callback_data="menu_tasks"),
            InlineKeyboardButton(text="⏰ Напоминания", callback_data="menu_reminders")
        ],
        [
            InlineKeyboardButton(text="📚 Архив", callback_data="menu_archive"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")
        ]
    ])
    
    await callback.message.edit_text("📋 Главное меню:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("mode_"))
async def callback_set_mode(callback: CallbackQuery):
    """Установить режим обработки."""
    mode = callback.data.split("_")[1]
    mode_names = {
        "auto": "Авто-режим",
        "meeting": "Собрание",
        "reminder": "Напоминание",
        "archive": "Архив",
        "diary": "Дневник",
        "work": "Работа",
        "home": "Дом",
        "study": "Учёба",
        "ideas": "Идеи",
        "health": "Здоровье",
        "finance": "Финансы"
    }
    
    # TODO: Сохранить режим в настройках пользователя
    
    await callback.answer(f"Режим установлен: {mode_names.get(mode, mode)}")
    await callback_menu_main(callback)

