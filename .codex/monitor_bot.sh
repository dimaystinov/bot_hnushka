#!/usr/bin/env bash
# Мониторинг бота и автоматический запуск Codex при обнаружении ошибок

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BOT_LOG="$PROJECT_ROOT/bot.log"
ERROR_LOG="$PROJECT_ROOT/.codex/errors.log"
CODEX_SCRIPT="$PROJECT_ROOT/.codex/run_codex.sh"
LAST_CHECK_FILE="$PROJECT_ROOT/.codex/last_error_check"

cd "$PROJECT_ROOT"

# Создаем необходимые файлы
mkdir -p "$PROJECT_ROOT/.codex"
touch "$ERROR_LOG"
touch "$LAST_CHECK_FILE"

# Получаем время последней проверки
LAST_CHECK=$(cat "$LAST_CHECK_FILE" 2>/dev/null || echo "0")
CURRENT_TIME=$(date +%s)

# Проверяем логи бота на новые ошибки
if [ -f "$BOT_LOG" ]; then
  # Ищем ошибки после последней проверки
  NEW_ERRORS=$(tail -n +$((LAST_CHECK + 1)) "$BOT_LOG" 2>/dev/null | grep -iE "error|exception|traceback|failed|critical|fatal" || true)
  
  if [ -n "$NEW_ERRORS" ]; then
    echo "⚠️ New runtime errors detected in bot.log!"
    echo "$NEW_ERRORS" | tee -a "$ERROR_LOG"
    echo "--- $(date) ---" >> "$ERROR_LOG"
    
    # Запускаем Codex для исправления
    echo "🔄 Starting Codex to fix runtime errors..."
    "$CODEX_SCRIPT" > "$PROJECT_ROOT/.codex/monitor_fix.log" 2>&1 &
    
    echo "✅ Codex improvement started"
    echo "📋 Check .codex/monitor_fix.log for progress"
  else
    echo "✅ No new errors in bot.log"
  fi
else
  echo "ℹ️ bot.log not found"
fi

# Сохраняем количество строк для следующей проверки
if [ -f "$BOT_LOG" ]; then
  wc -l < "$BOT_LOG" > "$LAST_CHECK_FILE"
fi

