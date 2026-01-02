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
    
    # Запускаем Codex для исправления в tmux
    echo "🔄 Starting Codex to fix runtime errors in tmux..."
    TMUX_SESSION="hnushka"
    
    # Проверка существования tmux сессии
    if ! tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
      # Создаем новую сессию если не существует
      tmux new-session -d -s "$TMUX_SESSION" -c "$PROJECT_ROOT"
    fi
    
    # Запуск Codex в tmux сессии
    tmux send-keys -t "$TMUX_SESSION" "cd $PROJECT_ROOT && $CODEX_SCRIPT" Enter
    
    echo "✅ Codex improvement started in tmux session '$TMUX_SESSION'"
    echo "📋 Attach to session: tmux attach -t $TMUX_SESSION"
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

