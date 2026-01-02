# Codex Auto-Improvement Setup

## Обзор

Настроена автоматическая система улучшения кода с помощью Codex CLI:
- Автоматическое обнаружение и исправление багов
- Улучшение качества кода
- CI/CD интеграция
- Тестирование и отладка

## Структура

```
.codex/
├── run_codex.sh          # Основной скрипт для итеративного улучшения
├── test_and_debug.sh     # Скрипт для тестирования и отладки
├── rules.md              # Правила для Codex
└── memory.md             # Память о предыдущих исправлениях

.github/workflows/
├── ci.yml                # CI/CD pipeline
└── codex-auto-improve.yml # Автоматическое улучшение кода
```

## Использование

### Ручной запуск улучшения кода

```bash
cd /root/bot_hnushka
./.codex/run_codex.sh
```

Скрипт будет:
1. Анализировать код
2. Находить проблемы
3. Исправлять их
4. Коммитить изменения
5. Повторять до сходимости

### Тестирование и отладка

```bash
cd /root/bot_hnushka
./.codex/test_and_debug.sh
```

Проверяет:
- Импорты
- Конфигурацию
- Базовую функциональность
- Потенциальные баги

### Автоматический запуск

GitHub Actions автоматически запускает улучшение кода:
- **Ежедневно в 3:00 UTC** (через `codex-auto-improve.yml`)
- **При каждом PR** (code review через Codex)
- **При каждом push** (CI/CD pipeline)

## Настройка

### GitHub Secrets

Для работы Codex в GitHub Actions нужно добавить:

1. Перейдите в Settings → Secrets and variables → Actions
2. Добавьте `CODEX_API_KEY` с вашим OpenAI API ключом

Или используйте авторизацию через ChatGPT (уже настроена локально).

### Локальная настройка

Codex CLI уже установлен и авторизован:
```bash
codex login status
```

## Правила для Codex

Правила определены в `.codex/rules.md`:
- Python best practices
- Async patterns
- Error handling
- Security requirements
- Performance optimization

## Память итераций

Codex запоминает предыдущие исправления в `.codex/memory.md`:
- Избегает повторения одних и тех же исправлений
- Останавливается когда нет новых проблем
- Отслеживает прогресс улучшений

## CI/CD Pipeline

### Тесты
- Проверка форматирования (black)
- Линтинг (flake8)
- Проверка типов (mypy)
- Unit тесты (pytest)

### Безопасность
- Проверка на секреты в коде
- Сканирование уязвимостей (Trivy)
- Валидация .env.example

### Сборка
- Проверка импортов
- Валидация конфигурации
- Проверка запуска бота

## Примеры использования

### Исправить конкретную проблему

```bash
codex exec "Исправь все race conditions в async коде"
```

### Улучшить производительность

```bash
codex exec "Оптимизируй обработку больших файлов"
```

### Добавить обработку ошибок

```bash
codex exec "Добавь обработку ошибок во все критические места"
```

## Мониторинг

Проверка результатов:
```bash
# Посмотреть последние коммиты от Codex
git log --author="Codex" --oneline

# Посмотреть изменения
git log --grep="fix\|refactor\|perf" --oneline

# Проверить память итераций
cat .codex/memory.md
```

## Ограничения

1. **Sandbox**: Codex работает в sandbox с ограничениями
2. **Git History**: Изменения коммитятся автоматически
3. **API Limits**: Учитывайте лимиты OpenAI API

## Troubleshooting

### Codex не запускается
```bash
# Проверить авторизацию
codex login status

# Проверить установку
codex --version
```

### Ошибки в CI/CD
- Проверьте GitHub Secrets
- Убедитесь что токены действительны
- Проверьте логи в GitHub Actions

### Проблемы с sandbox
- Используйте `--sandbox danger-full-access` для полного доступа
- Или `--skip-git-repo-check` если проблемы с git

## Дополнительная информация

- [Codex CLI документация](https://github.com/openai/codex)
- [GitHub Actions документация](https://docs.github.com/en/actions)

