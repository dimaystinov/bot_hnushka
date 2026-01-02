    async def process_diary(self, transcription: str) -> Dict[str, Any]:
        """Обработать запись дневника."""
        prompt = f"""Преобразуй расшифровку в запись личного дневника.

Расшифровка:
{transcription}

Создай JSON в формате:
{{
    "title": "заголовок записи",
    "summary": "краткое резюме (2-3 предложения)",
    "content": "полный текст записи",
    "thoughts": ["мысль1", "мысль2", ...],
    "emotions": ["эмоция1", "эмоция2", ...]
}}"""
        
        messages = [
            {"role": "system", "content": "Ты помощник для ведения личного дневника. Отвечай только валидным JSON."},
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
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}, ответ: {response}")
            return {"error": "Ошибка обработки"}
    
    async def process_work(self, transcription: str) -> Dict[str, Any]:
        """Обработать рабочую заметку."""
        prompt = f"""Преобразуй расшифровку в рабочую заметку.

Расшифровка:
{transcription}

Создай JSON в формате:
{{
    "title": "заголовок заметки",
    "project_context": "контекст проекта/задачи",
    "done": ["выполненная задача1", "выполненная задача2", ...],
    "planned": ["запланированная задача1", "запланированная задача2", ...],
    "problems": ["проблема/риск1", "проблема/риск2", ...],
    "ideas": ["идея1", "идея2", ...]
}}"""
        
        messages = [
            {"role": "system", "content": "Ты помощник для ведения рабочих заметок. Отвечай только валидным JSON."},
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
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}, ответ: {response}")
            return {"error": "Ошибка обработки"}
    
    async def process_home(self, transcription: str) -> Dict[str, Any]:
        """Обработать бытовые задачи."""
        prompt = f"""Извлеки бытовые задачи из расшифровки.

Расшифровка:
{transcription}

Создай JSON в формате:
{{
    "tasks": [
        {{
            "category": "покупки" | "ремонт" | "бытовые" | "семейные",
            "title": "название задачи",
            "description": "описание (опционально)"
        }}
    ]
}}"""
        
        messages = [
            {"role": "system", "content": "Ты помощник для управления бытовыми задачами. Отвечай только валидным JSON."},
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
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}, ответ: {response}")
            return {"error": "Ошибка обработки"}
    
    async def process_study(self, transcription: str) -> Dict[str, Any]:
        """Обработать учебный конспект."""
        prompt = f"""Преобразуй расшифровку в структурированный учебный конспект.

Расшифровка:
{transcription}

Создай JSON в формате:
{{
    "topic": "тема конспекта",
    "key_points": ["ключевой тезис1", "ключевой тезис2", ...],
    "definitions": ["определение1", "определение2", ...],
    "examples": ["пример1", "пример2", ...],
    "questions": ["вопрос для самопроверки1", "вопрос2", ...],
    "follow_up_tasks": ["задача1 (например, 'разобрать главу 3')", "задача2", ...]
}}"""
        
        messages = [
            {"role": "system", "content": "Ты помощник для создания учебных конспектов. Отвечай только валидным JSON."},
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
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}, ответ: {response}")
            return {"error": "Ошибка обработки"}
    
    async def process_ideas(self, transcription: str) -> Dict[str, Any]:
        """Обработать идеи/брейншторм."""
        prompt = f"""Извлеки идеи из расшифровки брейншторма.

Расшифровка:
{transcription}

Создай JSON в формате:
{{
    "ideas": [
        {{
            "title": "название идеи",
            "description": "описание идеи",
            "category": "работа" | "личное" | "проект" | null,
            "next_step": "MVP-шаг или следующий минимальный шаг"
        }}
    ]
}}"""
        
        messages = [
            {"role": "system", "content": "Ты помощник для фиксации идей. Отвечай только валидным JSON."},
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
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}, ответ: {response}")
            return {"error": "Ошибка обработки"}
    
    async def process_health(self, transcription: str) -> Dict[str, Any]:
        """Обработать запись о здоровье."""
        prompt = f"""Извлеки информацию о здоровье из расшифровки.

Расшифровка:
{transcription}

Создай JSON в формате:
{{
    "symptoms": ["симптом1", "симптом2", ...],
    "actions": ["действие1 (лекарство, тренировка и т.п.)", "действие2", ...],
    "triggers": ["возможный триггер1", "триггер2", ...],
    "notes": "дополнительные заметки"
}}"""
        
        messages = [
            {"role": "system", "content": "Ты помощник для ведения лога здоровья. Отвечай только валидным JSON."},
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
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}, ответ: {response}")
            return {"error": "Ошибка обработки"}
    
    async def process_finance(self, transcription: str) -> Dict[str, Any]:
        """Обработать финансовую операцию."""
        prompt = f"""Извлеки финансовую информацию из расшифровки.

Расшифровка:
{transcription}

Создай JSON в формате:
{{
    "transactions": [
        {{
            "amount": число (сумма),
            "category": "доход" | "расход",
            "subcategory": "еда" | "транспорт" | "зарплата" | "развлечения" | "другое",
            "description": "описание операции"
        }}
    ]
}}"""
        
        messages = [
            {"role": "system", "content": "Ты помощник для учёта финансов. Отвечай только валидным JSON."},
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
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}, ответ: {response}")
            return {"error": "Ошибка обработки"}

