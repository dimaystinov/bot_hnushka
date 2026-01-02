# Статус системы

## ✅ Настроено и работает

### 1. OpenRouter (Основной провайдер)
- **Модель:** `google/gemini-2.0-flash-exp:free`
- **Статус:** ✅ Настроено
- **Лимиты:** 20 req/min, 200 req/day
- **Бесплатные токены:** 1.5 млрд

### 2. Ollama (Локальный fallback)
- **Модель:** `qwen:4b` (Qwen 2.5 4B)
- **Статус:** ✅ Работает
- **Размер:** 2.3 GB
- **API:** http://localhost:11434
- **Тест:** ✅ Протестировано

## 🔄 Цепочка fallback

1. **OpenRouter** (Gemini бесплатно) → Основной
2. **Ollama** (локальный Qwen) → Если OpenRouter недоступен

## 📊 Проверка работы

### Тест OpenRouter (Gemini):
```bash
export OPENAI_API_KEY="your-key"
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{"model":"google/gemini-2.0-flash-exp:free","messages":[{"role":"user","content":"Привет"}]}'
```

### Тест Ollama (локальный Qwen 4B):
```bash
curl -s http://localhost:11434/api/chat \
  -d '{"model":"qwen:4b","messages":[{"role":"user","content":"Привет"}],"stream":false}' \
  | python3 -m json.tool
```

## 🚀 Запуск бота

```bash
cd /root/bot_hnushka
source venv/bin/activate
python3 main.py
```

## 📝 Конфигурация

Все настройки в `.env`:
- `OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free`
- `LOCAL_LLM_MODEL=qwen:4b` (Qwen 2.5 4B, легкая модель)
- `LOCAL_LLM_API_TYPE=ollama`

## ⚠️ Заметки

- Ollama работает в CPU-only режиме (GPU не обнаружен)
- FreeQwenApi отключен из fallback цепочки (не работает)
- OpenRouter и Ollama протестированы и работают

