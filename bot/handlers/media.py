"""Обработчики медиа (голосовые, аудио, видео)."""
import io
import os
import tempfile
import asyncio
import aiohttp
from pathlib import Path
from aiogram import Router, Bot, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, BufferedInputFile
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from bot.models.database import User, ProcessingTask
from bot.services.queue_service import QueueService
from bot.utils.logger import logger
from bot.handlers.media_results import _send_text_or_file, clean_text

router = Router()


@router.message(F.voice | F.audio | F.video_note)
async def handle_media(message: Message, bot: Bot, state: FSMContext):
    """Обработчик голосовых сообщений, аудио и видео-кружков."""
    try:
        # Определяем тип файла
        if message.voice:
            file_id = message.voice.file_id
            file_type = "voice"
            duration = message.voice.duration
        elif message.audio:
            file_id = message.audio.file_id
            file_type = "audio"
            duration = message.audio.duration
        elif message.video_note:
            file_id = message.video_note.file_id
            file_type = "video_note"
            duration = message.video_note.duration
        else:
            return
        
        user_id = message.from_user.id
        
        # Отправляем подтверждение
        status_msg = await message.answer(
            f"🎤 Принял {file_type}, расшифровываю...\n"
            f"⏱ Длительность: {duration} сек.\n"
            f"⏳ Это может занять некоторое время..."
        )
        
        # Получаем или создаём пользователя
        from bot.storage.database import AsyncSessionLocal
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.telegram_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(
                    telegram_id=user_id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
            
            # Добавляем задачу в очередь
            queue_service = QueueService(session)
            task = await queue_service.add_task(
                user_id=user.id,
                file_id=file_id,
                file_type=file_type
            )
            
            # Скачиваем файл на диск (для больших файлов)
            await status_msg.edit_text("📥 Скачиваю файл...")
            file = await bot.get_file(file_id)
            file_path = file.file_path
            
            # Проверяем размер файла (если доступен)
            file_size = getattr(file, 'file_size', None)
            # Лимит Bot API для скачивания: 50 МБ, но лучше ограничить до 20 МБ для надежности
            max_size = 20 * 1024 * 1024  # 20 МБ
            if file_size and file_size > max_size:
                await status_msg.edit_text(
                    f"❌ Файл слишком большой ({file_size / 1024 / 1024:.1f} MB).\n"
                    f"Максимальный размер: 20 MB.\n"
                    f"Пожалуйста, отправьте файл меньшего размера."
                )
                return
            
            # Создаём временный файл для скачивания
            temp_dir = Path(tempfile.gettempdir()) / "bot_hnushka"
            temp_dir.mkdir(exist_ok=True)
            temp_file = temp_dir / f"{file_id}_{user_id}.ogg"
            
            try:
                # Скачиваем файл на диск
                await bot.download_file(file_path, destination=str(temp_file))
                
                # Проверяем, что файл скачался
                if not temp_file.exists() or temp_file.stat().st_size == 0:
                    raise Exception("Файл не был скачан или пуст")
                
                # Читаем файл с диска
                with open(temp_file, 'rb') as f:
                    audio_bytes = f.read()
                
                # Обновляем статус
                file_size_mb = len(audio_bytes) / 1024 / 1024
                await status_msg.edit_text(
                    f"🎤 Файл скачан ({file_size_mb:.1f} MB), начинаю расшифровку...\n"
                    f"📝 Задача #{task.id} в очереди"
                )
            except Exception as download_error:
                error_msg = str(download_error)
                if "too big" in error_msg.lower() or "file is too big" in error_msg.lower():
                    await status_msg.edit_text(
                        f"❌ Файл слишком большой для скачивания через Bot API.\n"
                        f"Максимальный размер: 20 MB.\n"
                        f"Пожалуйста, отправьте файл меньшего размера или разделите его на части."
                    )
                else:
                    logger.error(f"Ошибка скачивания файла: {download_error}", exc_info=True)
                    await status_msg.edit_text(
                        f"❌ Ошибка скачивания файла: {error_msg}\n"
                        f"Попробуйте отправить файл ещё раз."
                    )
                return
            finally:
                # Удаляем временный файл после использования
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                    except Exception as e:
                        logger.warning(f"Не удалось удалить временный файл {temp_file}: {e}")
            
            # Здесь должна быть обработка через очередь
            # Пока что делаем простую обработку напрямую
            from bot.services.whisper_service import WhisperService
            from bot.services.llm_service import LLMClient
            
            whisper = WhisperService()
            llm = LLMClient()
            
            # Расшифровка с прогрессом
            async def update_transcription_progress(progress: int):
                """Обновить прогресс расшифровки."""
                try:
                    await status_msg.edit_text(f"🎤 Расшифровываю аудио...\n📊 Прогресс: {progress}%")
                except Exception as e:
                    logger.warning(f"Не удалось обновить прогресс: {e}")
            
            await status_msg.edit_text("🎤 Расшифровываю аудио...\n📊 Прогресс: 0%")
            # Получаем язык пользователя
            from bot.utils.languages import get_language_for_whisper
            user_language = get_language_for_whisper(user.language or "auto")
            transcription = await whisper.transcribe(audio_bytes, language=user_language, progress_callback=update_transcription_progress)
            
            if not transcription or len(transcription.strip()) == 0:
                await status_msg.edit_text("❌ Не удалось расшифровать аудио. Попробуй ещё раз.")
                return
            
            # Классификация
            await status_msg.edit_text("🤖 Анализирую содержимое...\n📊 Прогресс обработки: 20%")
            classification = await llm.classify_message(transcription)
            message_type = classification.get("type", "UNKNOWN").lower()
            
            # Обработка в зависимости от типа
            await status_msg.edit_text("📝 Формирую результат...\n📊 Прогресс обработки: 60%")
            
            if message_type == "meeting":
                result = await llm.process_meeting(transcription)
                await _send_meeting_result(message, status_msg, result, task.id)
            elif message_type == "reminder":
                result = await llm.process_reminder(transcription)
                await status_msg.edit_text("📊 Прогресс обработки: 100%\n✅ Готово!")
                await _send_reminder_result(message, status_msg, result, task.id)
            elif message_type == "archive":
                result = await llm.process_archive(transcription)
                await status_msg.edit_text("📊 Прогресс обработки: 100%\n✅ Готово!")
                await _send_archive_result(message, status_msg, result, task.id)
            elif message_type == "diary":
                result = await llm.process_diary(transcription)
                await status_msg.edit_text("📊 Прогресс обработки: 100%\n✅ Готово!")
                from bot.handlers.media_results import _send_diary_result
                await _send_diary_result(message, status_msg, result, task.id)
            elif message_type == "work":
                result = await llm.process_work(transcription)
                await status_msg.edit_text("📊 Прогресс обработки: 100%\n✅ Готово!")
                from bot.handlers.media_results import _send_work_result
                await _send_work_result(message, status_msg, result, task.id)
            elif message_type == "home":
                result = await llm.process_home(transcription)
                await status_msg.edit_text("📊 Прогресс обработки: 100%\n✅ Готово!")
                from bot.handlers.media_results import _send_home_result
                await _send_home_result(message, status_msg, result, task.id)
            elif message_type == "study":
                result = await llm.process_study(transcription)
                await status_msg.edit_text("📊 Прогресс обработки: 100%\n✅ Готово!")
                from bot.handlers.media_results import _send_study_result
                await _send_study_result(message, status_msg, result, task.id)
            elif message_type == "ideas":
                result = await llm.process_ideas(transcription)
                await status_msg.edit_text("📊 Прогресс обработки: 100%\n✅ Готово!")
                from bot.handlers.media_results import _send_ideas_result
                await _send_ideas_result(message, status_msg, result, task.id)
            elif message_type == "health":
                result = await llm.process_health(transcription)
                await status_msg.edit_text("📊 Прогресс обработки: 100%\n✅ Готово!")
                from bot.handlers.media_results import _send_health_result
                await _send_health_result(message, status_msg, result, task.id)
            elif message_type == "finance":
                result = await llm.process_finance(transcription)
                await status_msg.edit_text("📊 Прогресс обработки: 100%\n✅ Готово!")
                from bot.handlers.media_results import _send_finance_result
                await _send_finance_result(message, status_msg, result, task.id)
            else:
                await status_msg.edit_text(
                    f"📝 Расшифровка:\n\n{transcription}\n\n"
                    f"⚠️ Не удалось определить тип сообщения."
                )
            
            # Обновляем задачу
            task.transcription = transcription
            from bot.models.database import TaskStatus
            task.status = TaskStatus.DONE
            await session.commit()
            
    except Exception as e:
        logger.error(f"Ошибка обработки медиа: {e}", exc_info=True)
        await message.answer(f"❌ Произошла ошибка при обработке: {str(e)}")


# Функции _send_text_or_file и _delete_file_after_delay перенесены в media_results.py


async def _send_meeting_result(
    message: Message,
    status_msg: Message,
    result: dict,
    task_id: int
):
    """Отправить результат обработки собрания."""
    if "error" in result:
        await status_msg.edit_text(f"❌ Ошибка обработки: {result['error']}")
        return
    
    title = clean_text(str(result.get('title', 'Собрание')))
    summary = clean_text(str(result.get('summary', '')))
    
    text = f"👥 {title}\n\n"
    text += f"📋 {summary}\n\n"
    
    if result.get("participants"):
        participants = [clean_text(str(p)) for p in result['participants']]
        text += f"👤 Участники: {', '.join(participants)}\n\n"
    
    if result.get("tasks"):
        text += "✅ Задачи:\n"
        for i, task in enumerate(result["tasks"], 1):
            task_title = clean_text(str(task.get('title', '')))
            text += f"{i}. {task_title}"
            if task.get("assignee"):
                assignee = clean_text(str(task['assignee']))
                text += f" → {assignee}"
            if task.get("due_date"):
                due_date = clean_text(str(task['due_date']))
                text += f" (до {due_date})"
            text += "\n"
        text += "\n"
    
    if result.get("decisions"):
        text += "💡 Решения:\n"
        for i, decision in enumerate(result["decisions"], 1):
            decision_text = clean_text(str(decision))
            text += f"{i}. {decision_text}\n"
        text += "\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Переформулировать", callback_data=f"reprocess_{task_id}"),
            InlineKeyboardButton(text="✏️ Изменить тип", callback_data=f"change_type_{task_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task_id}")
        ]
    ])
    
    await _send_text_or_file(message, status_msg, text, "Собрание", keyboard)


async def _send_reminder_result(
    message: Message,
    status_msg: Message,
    result: dict,
    task_id: int
):
    """Отправить результат обработки напоминания."""
    if "error" in result:
        await status_msg.edit_text(f"❌ Ошибка обработки: {result['error']}")
        return
    
    reminder_text = clean_text(str(result.get('text', '')))
    text = f"⏰ Напоминание создано\n\n"
    text += f"📝 {reminder_text}\n\n"
    
    if result.get("reminder_date"):
        date = clean_text(str(result['reminder_date']))
        text += f"📅 Дата: {date}\n"
    elif result.get("relative_time"):
        time = clean_text(str(result['relative_time']))
        text += f"⏱ Время: {time}\n"
    
    if result.get("needs_clarification"):
        text += "\n⚠️ Нужно уточнить дату/время"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 Уточнить время", callback_data=f"clarify_time_{task_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task_id}")
        ]
    ])
    
    await _send_text_or_file(message, status_msg, text, "Напоминание", keyboard)


async def _send_archive_result(
    message: Message,
    status_msg: Message,
    result: dict,
    task_id: int
):
    """Отправить результат обработки архива."""
    if "error" in result:
        await status_msg.edit_text(f"❌ Ошибка обработки: {result['error']}")
        return
    
    title = clean_text(str(result.get('title', 'Заметка')))
    summary = clean_text(str(result.get('summary', '')))
    content = clean_text(str(result.get('content', '')))
    
    text = f"📚 {title}\n\n"
    text += f"📋 {summary}\n\n"
    text += f"{content}\n\n"
    
    if result.get("tags"):
        tags = [clean_text(str(tag)) for tag in result['tags']]
        text += f"🏷 Теги: {', '.join(tags)}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Переформулировать", callback_data=f"reprocess_{task_id}"),
            InlineKeyboardButton(text="✏️ Изменить тип", callback_data=f"change_type_{task_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task_id}")
        ]
    ])
    
    await _send_text_or_file(message, status_msg, text, "Собрание", keyboard)

