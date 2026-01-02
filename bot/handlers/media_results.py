"""Вспомогательные функции для отправки результатов обработки."""
import asyncio
import tempfile
from pathlib import Path
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from bot.utils.logger import logger

# Максимальная длина сообщения Telegram (4096 символов)
MAX_MESSAGE_LENGTH = 4096


def clean_text(text: str) -> str:
    """Очистить текст от проблемных символов для безопасной отправки."""
    if not text:
        return text
    # Просто возвращаем текст как есть, форматирование убрали
    return str(text)


async def _delete_file_after_delay(file_path: Path, delay: int):
    """Удалить файл через указанное время."""
    await asyncio.sleep(delay)
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        logger.warning(f"Не удалось удалить файл {file_path}: {e}")


async def _send_text_or_file(
    message: Message,
    status_msg: Message,
    text: str,
    title: str = "Результат",
    keyboard: InlineKeyboardMarkup = None
):
    """Отправить текст или файл, если текст слишком длинный."""
    if len(text) > MAX_MESSAGE_LENGTH:
        # Создаём временный файл
        temp_dir = Path(tempfile.gettempdir()) / "bot_hnushka"
        temp_dir.mkdir(exist_ok=True)
        temp_file = temp_dir / f"result_{message.from_user.id}_{message.message_id}.txt"
        
        try:
            # Записываем текст в файл
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # Отправляем файл
            file_input = FSInputFile(temp_file, filename=f"{title}.txt")
            await status_msg.delete()
            await message.answer_document(
                document=file_input,
                caption=f"📄 {title}\n\nТекст слишком длинный для сообщения, отправлен файлом.",
                reply_markup=keyboard
            )
        finally:
            # Удаляем временный файл через некоторое время
            if temp_file.exists():
                try:
                    # Удаляем файл асинхронно через 60 секунд
                    asyncio.create_task(_delete_file_after_delay(temp_file, 60))
                except Exception as e:
                    logger.warning(f"Не удалось запланировать удаление файла {temp_file}: {e}")
    else:
        # Отправляем обычное сообщение
        await status_msg.edit_text(text, reply_markup=keyboard)


async def _send_diary_result(
    message: Message,
    status_msg: Message,
    result: dict,
    task_id: int
):
    """Отправить результат обработки дневника."""
    if "error" in result:
        await status_msg.edit_text(f"❌ Ошибка обработки: {result['error']}")
        return
    
    title = clean_text(str(result.get('title', 'Дневник')))
    summary = clean_text(str(result.get('summary', '')))
    content = clean_text(str(result.get('content', '')))
    
    text = f"📔 {title}\n\n"
    text += f"📋 {summary}\n\n"
    text += f"{content}\n\n"
    
    if result.get("thoughts"):
        text += "💭 Мысли:\n"
        for i, thought in enumerate(result["thoughts"], 1):
            thought_text = clean_text(str(thought))
            text += f"{i}. {thought_text}\n"
        text += "\n"
    
    if result.get("emotions"):
        emotions = [clean_text(str(e)) for e in result['emotions']]
        text += f"😊 Эмоции: {', '.join(emotions)}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Переформулировать", callback_data=f"reprocess_{task_id}"),
            InlineKeyboardButton(text="✏️ Изменить тип", callback_data=f"change_type_{task_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task_id}")
        ]
    ])
    
    await _send_text_or_file(message, status_msg, text, "Дневник", keyboard)


async def _send_work_result(
    message: Message,
    status_msg: Message,
    result: dict,
    task_id: int
):
    """Отправить результат обработки рабочей заметки."""
    if "error" in result:
        await status_msg.edit_text(f"❌ Ошибка обработки: {result['error']}")
        return
    
    title = clean_text(str(result.get('title', 'Рабочая заметка')))
    context = clean_text(str(result.get('project_context', '')))
    
    text = f"💼 {title}\n\n"
    if context:
        text += f"📁 Контекст: {context}\n\n"
    
    if result.get("done"):
        text += "✅ Выполнено:\n"
        for i, item in enumerate(result["done"], 1):
            item_text = clean_text(str(item))
            text += f"{i}. {item_text}\n"
        text += "\n"
    
    if result.get("planned"):
        text += "📅 Запланировано:\n"
        for i, item in enumerate(result["planned"], 1):
            item_text = clean_text(str(item))
            text += f"{i}. {item_text}\n"
        text += "\n"
    
    if result.get("problems"):
        text += "⚠️ Проблемы/Риски:\n"
        for i, problem in enumerate(result["problems"], 1):
            problem_text = clean_text(str(problem))
            text += f"{i}. {problem_text}\n"
        text += "\n"
    
    if result.get("ideas"):
        text += "💡 Идеи:\n"
        for i, idea in enumerate(result["ideas"], 1):
            idea_text = clean_text(str(idea))
            text += f"{i}. {idea_text}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Переформулировать", callback_data=f"reprocess_{task_id}"),
            InlineKeyboardButton(text="✏️ Изменить тип", callback_data=f"change_type_{task_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task_id}")
        ]
    ])
    
    await _send_text_or_file(message, status_msg, text, "Рабочая заметка", keyboard)


async def _send_home_result(
    message: Message,
    status_msg: Message,
    result: dict,
    task_id: int
):
    """Отправить результат обработки бытовых задач."""
    if "error" in result:
        await status_msg.edit_text(f"❌ Ошибка обработки: {result['error']}")
        return
    
    title = clean_text(str(result.get('title', 'Бытовые задачи')))
    text = f"🏠 {title}\n\n"
    
    if result.get("shopping"):
        text += "🛒 Покупки:\n"
        for i, item in enumerate(result["shopping"], 1):
            item_text = clean_text(str(item))
            text += f"{i}. {item_text}\n"
        text += "\n"
    
    if result.get("repairs"):
        text += "🔧 Ремонт:\n"
        for i, item in enumerate(result["repairs"], 1):
            item_text = clean_text(str(item))
            text += f"{i}. {item_text}\n"
        text += "\n"
    
    if result.get("household"):
        text += "🧹 Бытовые задачи:\n"
        for i, item in enumerate(result["household"], 1):
            item_text = clean_text(str(item))
            text += f"{i}. {item_text}\n"
        text += "\n"
    
    if result.get("family"):
        text += "👨‍👩‍👧 Семейные дела:\n"
        for i, item in enumerate(result["family"], 1):
            item_text = clean_text(str(item))
            text += f"{i}. {item_text}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Переформулировать", callback_data=f"reprocess_{task_id}"),
            InlineKeyboardButton(text="✏️ Изменить тип", callback_data=f"change_type_{task_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task_id}")
        ]
    ])
    
    await _send_text_or_file(message, status_msg, text, "Бытовые задачи", keyboard)


async def _send_study_result(
    message: Message,
    status_msg: Message,
    result: dict,
    task_id: int
):
    """Отправить результат обработки конспекта."""
    if "error" in result:
        await status_msg.edit_text(f"❌ Ошибка обработки: {result['error']}")
        return
    
    title = clean_text(str(result.get('title', 'Конспект')))
    summary = clean_text(str(result.get('summary', '')))
    
    text = f"📚 {title}\n\n"
    text += f"📋 {summary}\n\n"
    
    if result.get("key_points"):
        text += "🔑 Ключевые тезисы:\n"
        for i, point in enumerate(result["key_points"], 1):
            point_text = clean_text(str(point))
            text += f"{i}. {point_text}\n"
        text += "\n"
    
    if result.get("definitions"):
        text += "📖 Определения:\n"
        for i, definition in enumerate(result["definitions"], 1):
            def_text = clean_text(str(definition))
            text += f"{i}. {def_text}\n"
        text += "\n"
    
    if result.get("examples"):
        text += "💡 Примеры:\n"
        for i, example in enumerate(result["examples"], 1):
            example_text = clean_text(str(example))
            text += f"{i}. {example_text}\n"
        text += "\n"
    
    if result.get("questions"):
        text += "❓ Вопросы для самопроверки:\n"
        for i, question in enumerate(result["questions"], 1):
            question_text = clean_text(str(question))
            text += f"{i}. {question_text}\n"
        text += "\n"
    
    if result.get("follow_up"):
        text += "📝 Следующие шаги:\n"
        for i, step in enumerate(result["follow_up"], 1):
            step_text = clean_text(str(step))
            text += f"{i}. {step_text}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Переформулировать", callback_data=f"reprocess_{task_id}"),
            InlineKeyboardButton(text="✏️ Изменить тип", callback_data=f"change_type_{task_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task_id}")
        ]
    ])
    
    await _send_text_or_file(message, status_msg, text, "Конспект", keyboard)


async def _send_ideas_result(
    message: Message,
    status_msg: Message,
    result: dict,
    task_id: int
):
    """Отправить результат обработки идей."""
    if "error" in result:
        await status_msg.edit_text(f"❌ Ошибка обработки: {result['error']}")
        return
    
    text = "💡 Идеи:\n\n"
    
    if result.get("ideas"):
        for i, idea in enumerate(result["ideas"], 1):
            idea_title = clean_text(str(idea.get('title', f'Идея {i}')))
            idea_desc = clean_text(str(idea.get('description', '')))
            idea_tag = clean_text(str(idea.get('tag', '')))
            idea_step = clean_text(str(idea.get('next_step', '')))
            
            text += f"{i}. {idea_title}\n"
            if idea_desc:
                text += f"   {idea_desc}\n"
            if idea_tag:
                text += f"   🏷 Тег: {idea_tag}\n"
            if idea_step:
                text += f"   👣 Следующий шаг: {idea_step}\n"
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
    
    await _send_text_or_file(message, status_msg, text, "Идеи", keyboard)


async def _send_health_result(
    message: Message,
    status_msg: Message,
    result: dict,
    task_id: int
):
    """Отправить результат обработки записи о здоровье."""
    if "error" in result:
        await status_msg.edit_text(f"❌ Ошибка обработки: {result['error']}")
        return
    
    date = clean_text(str(result.get('date', '')))
    text = f"🏥 Запись о здоровье"
    if date:
        text += f" - {date}"
    text += "\n\n"
    
    if result.get("symptoms"):
        text += "🤒 Симптомы:\n"
        for i, symptom in enumerate(result["symptoms"], 1):
            symptom_text = clean_text(str(symptom))
            text += f"{i}. {symptom_text}\n"
        text += "\n"
    
    if result.get("actions"):
        text += "💊 Действия:\n"
        for i, action in enumerate(result["actions"], 1):
            action_text = clean_text(str(action))
            text += f"{i}. {action_text}\n"
        text += "\n"
    
    if result.get("triggers"):
        triggers = [clean_text(str(t)) for t in result['triggers']]
        text += f"⚡ Триггеры: {', '.join(triggers)}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Переформулировать", callback_data=f"reprocess_{task_id}"),
            InlineKeyboardButton(text="✏️ Изменить тип", callback_data=f"change_type_{task_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task_id}")
        ]
    ])
    
    await _send_text_or_file(message, status_msg, text, "Здоровье", keyboard)


async def _send_finance_result(
    message: Message,
    status_msg: Message,
    result: dict,
    task_id: int
):
    """Отправить результат обработки финансовой записи."""
    if "error" in result:
        await status_msg.edit_text(f"❌ Ошибка обработки: {result['error']}")
        return
    
    text = "💰 Финансовые операции:\n\n"
    
    if result.get("operations"):
        for i, op in enumerate(result["operations"], 1):
            amount = clean_text(str(op.get('amount', '')))
            category = clean_text(str(op.get('category', '')))
            comment = clean_text(str(op.get('comment', '')))
            op_type = clean_text(str(op.get('type', 'расход')))
            
            text += f"{i}. {op_type}: {amount}"
            if category:
                text += f" ({category})"
            if comment:
                text += f" - {comment}"
            text += "\n"
    
    if result.get("total_income"):
        total = clean_text(str(result['total_income']))
        text += f"\n📈 Всего доходов: {total}\n"
    
    if result.get("total_expenses"):
        total = clean_text(str(result['total_expenses']))
        text += f"📉 Всего расходов: {total}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Переформулировать", callback_data=f"reprocess_{task_id}"),
            InlineKeyboardButton(text="✏️ Изменить тип", callback_data=f"change_type_{task_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task_id}")
        ]
    ])
    
    await _send_text_or_file(message, status_msg, text, "Финансы", keyboard)

