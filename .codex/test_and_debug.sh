#!/usr/bin/env bash
set -e

# Определяем корневую директорию
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# Активация venv если существует
if [ -d "$PROJECT_ROOT/venv" ]; then
  source "$PROJECT_ROOT/venv/bin/activate"
  PYTHON_CMD="python3"
  echo "🐍 Virtual environment activated"
else
  PYTHON_CMD="python3"
  echo "⚠️ venv not found, using system python"
fi

echo "🧪 Testing and Debugging with Codex"
echo "📁 Working directory: $PROJECT_ROOT"

TEST_FILE=".codex/test_results.txt"
BOT_PID_FILE=".codex/bot.pid"
mkdir -p .codex

# Функция для остановки бота
stop_bot() {
  if [ -f "$BOT_PID_FILE" ]; then
    BOT_PID=$(cat "$BOT_PID_FILE")
    if ps -p "$BOT_PID" > /dev/null 2>&1; then
      echo "🛑 Stopping bot (PID: $BOT_PID)..."
      kill "$BOT_PID" 2>/dev/null || true
      sleep 2
      kill -9 "$BOT_PID" 2>/dev/null || true
    fi
    rm -f "$BOT_PID_FILE"
  fi
  pkill -f "python.*main.py" 2>/dev/null || true
}

trap stop_bot EXIT

echo "Running comprehensive bot tests..." | tee "$TEST_FILE"

# Тест 1: Импорты
echo "=== Test 1: Imports ===" | tee -a "$TEST_FILE"
$PYTHON_CMD -c "from config import settings; print('✅ Config OK')" 2>&1 | tee -a "$TEST_FILE"
$PYTHON_CMD -c "from bot.utils.logger import logger; logger.info('✅ Logger OK')" 2>&1 | tee -a "$TEST_FILE"
$PYTHON_CMD -c "from bot.handlers import common, media; print('✅ Handlers OK')" 2>&1 | tee -a "$TEST_FILE"
$PYTHON_CMD -c "from bot.services import whisper_service, llm_service; print('✅ Services OK')" 2>&1 | tee -a "$TEST_FILE"

# Тест 2: Синтаксис
echo "=== Test 2: Syntax ===" | tee -a "$TEST_FILE"
$PYTHON_CMD -m py_compile main.py 2>&1 | tee -a "$TEST_FILE" && echo "✅ main.py syntax OK" | tee -a "$TEST_FILE"
find bot -name "*.py" -exec $PYTHON_CMD -m py_compile {} \; 2>&1 | tee -a "$TEST_FILE" && echo "✅ All Python files syntax OK" | tee -a "$TEST_FILE"

# Тест 3: Конфигурация
echo "=== Test 3: Configuration ===" | tee -a "$TEST_FILE"
$PYTHON_CMD -c "
from config import settings
assert hasattr(settings, 'bot_token'), 'Bot token required'
assert hasattr(settings, 'whisper_model'), 'Whisper model required'
print('✅ Configuration OK')
" 2>&1 | tee -a "$TEST_FILE"

# Тест 4: Модели БД
echo "=== Test 4: Database Models ===" | tee -a "$TEST_FILE"
$PYTHON_CMD -c "
from bot.models.database import User, ProcessingTask, Task
print('✅ Database models OK')
" 2>&1 | tee -a "$TEST_FILE"

# Тест 5: Инициализация сервисов
echo "=== Test 5: Service Initialization ===" | tee -a "$TEST_FILE"
$PYTHON_CMD -c "
from bot.services.whisper_service import WhisperService
from bot.services.llm_service import LLMClient
print('✅ Services can be imported')
# Не инициализируем реально, только проверяем импорты
" 2>&1 | tee -a "$TEST_FILE"

# Тест 6: Запуск бота (краткий тест)
echo "=== Test 6: Bot Initialization ===" | tee -a "$TEST_FILE"
timeout 15 $PYTHON_CMD -c "
import asyncio
import sys
from config import settings
from bot.utils.logger import logger

async def test_init():
    try:
        logger.info('Testing bot initialization...')
        # Проверяем что все модули загружаются
        from bot.storage.database import init_db
        from bot.handlers import common, media
        from bot.services import whisper_service, llm_service
        
        logger.info('✅ All modules loaded successfully')
        print('✅ Bot initialization test passed')
        return True
    except Exception as e:
        logger.error(f'❌ Initialization error: {e}')
        import traceback
        traceback.print_exc()
        return False

result = asyncio.run(test_init())
sys.exit(0 if result else 1)
" 2>&1 | tee -a "$TEST_FILE"

# Тест 7: Запуск бота в фоне (если есть токен)
if [ -f .env ] && grep -q "BOT_TOKEN=" .env && ! grep -q "your_telegram_bot_token_here" .env; then
  echo "=== Test 7: Bot Runtime Test ===" | tee -a "$TEST_FILE"
  echo "Starting bot in background for 30 seconds..." | tee -a "$TEST_FILE"
  
  # Запуск бота в фоне (с venv если доступен)
  nohup $PYTHON_CMD main.py > .codex/bot_output.log 2>&1 &
  BOT_PID=$!
  echo "$BOT_PID" > "$BOT_PID_FILE"
  
  # Ждем запуска
  sleep 5
  
  # Проверяем что процесс жив
  if ps -p "$BOT_PID" > /dev/null; then
    echo "✅ Bot started successfully (PID: $BOT_PID)" | tee -a "$TEST_FILE"
    
    # Ждем еще немного и проверяем логи
    sleep 10
    
    if [ -f .codex/bot_output.log ]; then
      echo "Bot output (last 20 lines):" | tee -a "$TEST_FILE"
      tail -20 .codex/bot_output.log | tee -a "$TEST_FILE"
      
      # Проверяем на ошибки
      if grep -i "error\|exception\|traceback" .codex/bot_output.log > /dev/null; then
        echo "⚠️ Errors found in bot output" | tee -a "$TEST_FILE"
      else
        echo "✅ No errors in bot output" | tee -a "$TEST_FILE"
      fi
    fi
    
    # Останавливаем бота
    stop_bot
  else
    echo "❌ Bot failed to start" | tee -a "$TEST_FILE"
    if [ -f .codex/bot_output.log ]; then
      echo "Error output:" | tee -a "$TEST_FILE"
      cat .codex/bot_output.log | tee -a "$TEST_FILE"
    fi
  fi
else
  echo "=== Test 7: Bot Runtime Test ===" | tee -a "$TEST_FILE"
  echo "⚠️ Skipping runtime test (no valid BOT_TOKEN in .env)" | tee -a "$TEST_FILE"
fi

# Запуск Codex для анализа результатов
codex exec --full-auto --sandbox danger-full-access "
TASK: Analyze test results and fix any issues found

1. Read .codex/test_results.txt
2. Identify any errors or failures
3. If errors found:
   - Fix the issues
   - Re-run the tests
   - Document the fixes
4. If no errors:
   - Verify code quality
   - Check for potential issues
   - Document any improvements made
"

echo "✅ Testing completed. Check $TEST_FILE for results."

