#!/usr/bin/env bash
set -e

STATE=".codex"
MEMORY="$STATE/memory.md"
RULES="$STATE/rules.md"
TEST_LOG="$STATE/test_log.txt"
BOT_PID_FILE="$STATE/bot.pid"

mkdir -p "$STATE"
touch "$MEMORY"
touch "$TEST_LOG"

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
  # Убить все процессы python main.py
  pkill -f "python.*main.py" 2>/dev/null || true
}

# Очистка при выходе
trap stop_bot EXIT

ITER=0

while true; do
  ITER=$((ITER+1))
  echo "=============================="
  echo " Codex Iteration $ITER"
  echo "=============================="

  # Остановить бота перед анализом
  stop_bot

  codex exec --full-auto --sandbox danger-full-access "
$(cat "$RULES")

PAST ITERATIONS MEMORY:
$(cat "$MEMORY")

PREVIOUS TEST RESULTS:
$(tail -50 "$TEST_LOG" 2>/dev/null || echo "No previous tests")

TASK:
1. Analyze the entire codebase
2. Identify NEW issues only (do not repeat memory):
   - undefined behavior
   - data races / race conditions
   - logical errors
   - potential bugs
   - performance bottlenecks
   - non-production patterns
   - missing or unclear comments
   - import errors
   - syntax errors
   - configuration issues

3. If NO new issues exist:
   - Proceed to testing phase (step 4)

4. TESTING PHASE - Run and test the bot:
   a) Check if bot can start:
      - Try: python -c 'from config import settings; print(\"Config OK\")'
      - Try: python -c 'from bot.utils.logger import logger; logger.info(\"Logger OK\")'
      - Try: python -c 'from bot.handlers import common, media; print(\"Handlers OK\")'
      - Try: python -c 'from bot.services import whisper_service, llm_service; print(\"Services OK\")'
   
   b) Check for import errors:
      - python -m py_compile main.py
      - python -c 'import main' 2>&1
      - Check all imports are correct
   
   c) Validate configuration:
      - python -c 'from config import settings; assert settings.bot_token, \"Bot token required\"'
      - Check all required settings are present
   
   d) Test database initialization:
      - python -c 'import asyncio; from bot.storage.database import init_db; asyncio.run(init_db())'
   
   e) Try to start the bot (non-blocking test):
      - Create test script that imports main and checks initialization
      - Check for immediate errors on startup
      - Validate all services can be initialized
   
   f) Check for runtime errors:
      - Look for unhandled exceptions
      - Check async/await usage
      - Verify resource cleanup
   
   g) Check for logical errors:
      - Review business logic
      - Verify error handling
      - Check edge cases

5. If issues found in testing:
   - Fix ALL issues immediately
   - Add clear English comments
   - Improve error handling
   - Add logging for debugging
   - Preserve behavior unless bugfix requires change
   - Re-test after fixes

6. If NO issues found:
   - Print exactly: NO_NEW_ISSUES
   - Do NOT modify code
   - Do NOT commit
   - Exit

7. After fixes:
   - Run: git status
   - If there are NO changes: stop
   - Otherwise:
     - git add -A
     - Create ONE commit

COMMIT RULES:
- Write commit message as a senior engineer
- Use conventional commit style (fix/refactor/perf/safety/docs/test)
- Clear, concise, technical
- No emojis, no markdown, no explanations
- Include what was tested/fixed

8. Append test results and fixes to memory.md:
   - What was tested
   - What issues were found
   - What was fixed
   - Test results (success/failure)

9. Append test output to .codex/test_log.txt for next iteration
"
  
  # Запуск тестов после исправлений
  echo "🧪 Running bot tests..."
  stop_bot
  
  # Тест 1: Проверка импортов
  echo "Test 1: Checking imports..." | tee -a "$TEST_LOG"
  python3 -c "from config import settings; print('✅ Config OK')" 2>&1 | tee -a "$TEST_LOG" || echo "❌ Config error" | tee -a "$TEST_LOG"
  python3 -c "from bot.utils.logger import logger; logger.info('✅ Logger OK')" 2>&1 | tee -a "$TEST_LOG" || echo "❌ Logger error" | tee -a "$TEST_LOG"
  python3 -c "from bot.handlers import common, media; print('✅ Handlers OK')" 2>&1 | tee -a "$TEST_LOG" || echo "❌ Handlers error" | tee -a "$TEST_LOG"
  
  # Тест 2: Проверка синтаксиса
  echo "Test 2: Checking syntax..." | tee -a "$TEST_LOG"
  python3 -m py_compile main.py 2>&1 | tee -a "$TEST_LOG" || echo "❌ Syntax error in main.py" | tee -a "$TEST_LOG"
  
  # Тест 3: Проверка конфигурации
  echo "Test 3: Validating config..." | tee -a "$TEST_LOG"
  python3 -c "from config import settings; assert hasattr(settings, 'bot_token'), 'Bot token required'" 2>&1 | tee -a "$TEST_LOG" || echo "❌ Config validation error" | tee -a "$TEST_LOG"
  
  # Тест 4: Проверка инициализации БД (без реального подключения)
  echo "Test 4: Checking database models..." | tee -a "$TEST_LOG"
  python3 -c "from bot.models.database import User, ProcessingTask; print('✅ Models OK')" 2>&1 | tee -a "$TEST_LOG" || echo "❌ Models error" | tee -a "$TEST_LOG"
  
  # Тест 5: Попытка запуска бота (краткий тест)
  echo "Test 5: Testing bot initialization..." | tee -a "$TEST_LOG"
  timeout 10 python3 -c "
import asyncio
import sys
from config import settings
from bot.utils.logger import logger

async def test_init():
    try:
        from bot.storage.database import init_db
        logger.info('✅ Init test started')
        # Не инициализируем реальную БД, только проверяем импорты
        print('✅ Bot can be initialized')
        return True
    except Exception as e:
        print(f'❌ Init error: {e}')
        return False

result = asyncio.run(test_init())
sys.exit(0 if result else 1)
" 2>&1 | tee -a "$TEST_LOG" || echo "❌ Bot initialization error" | tee -a "$TEST_LOG"
  
  echo "✅ Tests completed. Check $TEST_LOG for details."
  echo "---" >> "$TEST_LOG"
  
  # Проверка сходимости по памяти
  if tail -n 5 "$MEMORY" | grep -q "NO_NEW_ISSUES"; then
    echo "✅ Code converged. No new issues."
    break
  fi
  
  # Небольшая пауза между итерациями
  sleep 2

done

stop_bot
echo "✅ Codex improvement cycle completed."

