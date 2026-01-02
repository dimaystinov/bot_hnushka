#!/usr/bin/env bash
set -e

# Определяем корневую директорию bot_hnushka
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Проверка что это bot_hnushka
if [ ! -f "$PROJECT_ROOT/main.py" ] || [ ! -d "$PROJECT_ROOT/bot" ]; then
  echo "❌ Error: bot_hnushka directory not found"
  exit 1
fi

cd "$PROJECT_ROOT"
echo "📁 Working directory: $PROJECT_ROOT"

# Активация venv
if [ -d "$PROJECT_ROOT/venv" ]; then
  source "$PROJECT_ROOT/venv/bin/activate"
  PYTHON_CMD="python3"
  echo "🐍 Virtual environment activated"
else
  PYTHON_CMD="python3"
  echo "⚠️ venv not found, using system python"
fi

STATE=".codex"
BOT_PID_FILE="$STATE/bot.pid"
BOT_LOG="$PROJECT_ROOT/bot.log"
ERROR_LOG="$STATE/errors.log"
IMPROVEMENT_LOG="$STATE/improvement.log"

mkdir -p "$STATE"
touch "$BOT_LOG"
touch "$ERROR_LOG"
touch "$IMPROVEMENT_LOG"

# Функция для запуска бота
start_bot() {
  if [ -f "$BOT_PID_FILE" ]; then
    BOT_PID=$(cat "$BOT_PID_FILE")
    if ps -p "$BOT_PID" > /dev/null 2>&1; then
      echo "✅ Bot already running (PID: $BOT_PID)"
      return 0
    fi
  fi
  
  echo "🚀 Starting bot..."
  cd "$PROJECT_ROOT"
  
  # Активация venv для бота
  if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
  fi
  
  # Запуск бота в фоне
  nohup $PYTHON_CMD main.py >> "$BOT_LOG" 2>&1 &
  BOT_PID=$!
  echo "$BOT_PID" > "$BOT_PID_FILE"
  
  # Ждем немного для проверки запуска
  sleep 3
  
  if ps -p "$BOT_PID" > /dev/null 2>&1; then
    echo "✅ Bot started successfully (PID: $BOT_PID)"
    return 0
  else
    echo "❌ Bot failed to start"
    rm -f "$BOT_PID_FILE"
    return 1
  fi
}

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

# Функция для проверки ошибок в логах
check_runtime_errors() {
  if [ ! -f "$BOT_LOG" ]; then
    return 1
  fi
  
  # Ищем ошибки в последних 100 строках
  ERRORS=$(tail -100 "$BOT_LOG" | grep -iE "error|exception|traceback|failed|critical|fatal" | tail -10 || true)
  
  if [ -n "$ERRORS" ]; then
    echo "⚠️ Runtime errors detected:"
    echo "$ERRORS"
    echo "$ERRORS" >> "$ERROR_LOG"
    echo "--- $(date) ---" >> "$ERROR_LOG"
    return 0
  fi
  
  return 1
}

# Функция для запуска Codex улучшения
run_codex_improvement() {
  echo "🔄 Running Codex improvement..."
  echo "--- Codex improvement started at $(date) ---" >> "$IMPROVEMENT_LOG"
  
  # Запускаем Codex в фоне
  cd "$PROJECT_ROOT"
  "$PROJECT_ROOT/.codex/run_codex.sh" >> "$IMPROVEMENT_LOG" 2>&1 &
  CODEX_PID=$!
  
  echo "✅ Codex improvement started (PID: $CODEX_PID)"
  echo "📋 Check $IMPROVEMENT_LOG for progress"
  
  # Ждем завершения Codex (максимум 30 минут)
  wait $CODEX_PID 2>/dev/null || true
  
  echo "✅ Codex improvement completed"
}

# Очистка при выходе
trap stop_bot EXIT

echo "=============================="
echo " Continuous Improvement System"
echo "=============================="
echo "📁 Project: $PROJECT_ROOT"
echo "🐍 Python: $($PYTHON_CMD --version)"
echo ""

# Запускаем бота
start_bot

# Основной цикл
ITER=0
LAST_IMPROVEMENT=0
IMPROVEMENT_INTERVAL=3600  # Улучшение каждые 60 минут

while true; do
  ITER=$((ITER+1))
  CURRENT_TIME=$(date +%s)
  
  echo ""
  echo "=============================="
  echo " Cycle $ITER - $(date)"
  echo "=============================="
  
  # Проверка что бот работает
  if [ -f "$BOT_PID_FILE" ]; then
    BOT_PID=$(cat "$BOT_PID_FILE")
    if ! ps -p "$BOT_PID" > /dev/null 2>&1; then
      echo "⚠️ Bot is not running, restarting..."
      start_bot
    else
      echo "✅ Bot is running (PID: $BOT_PID)"
    fi
  else
    echo "⚠️ Bot PID file not found, starting bot..."
    start_bot
  fi
  
  # Проверка runtime ошибок
  if check_runtime_errors; then
    echo "🔧 Runtime errors detected, running Codex to fix..."
    stop_bot
    run_codex_improvement
    start_bot
    LAST_IMPROVEMENT=$CURRENT_TIME
  else
    echo "✅ No runtime errors detected"
  fi
  
  # Периодическое улучшение (каждый час)
  TIME_SINCE_IMPROVEMENT=$((CURRENT_TIME - LAST_IMPROVEMENT))
  if [ $TIME_SINCE_IMPROVEMENT -ge $IMPROVEMENT_INTERVAL ]; then
    echo "🔄 Scheduled improvement, running Codex..."
    stop_bot
    run_codex_improvement
    start_bot
    LAST_IMPROVEMENT=$CURRENT_TIME
  else
    REMAINING=$((IMPROVEMENT_INTERVAL - TIME_SINCE_IMPROVEMENT))
    echo "⏰ Next improvement in $((REMAINING / 60)) minutes"
  fi
  
  # Ждем перед следующей проверкой (5 минут)
  echo "💤 Sleeping for 5 minutes..."
  sleep 300
done

