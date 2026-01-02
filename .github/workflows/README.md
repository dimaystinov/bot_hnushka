# GitHub Actions Workflows

⚠️ **Важно:** Workflow файлы не могут быть созданы через OAuth без `workflow` scope.

## Установка workflows вручную

### Вариант 1: Через веб-интерфейс GitHub

1. Перейдите на https://github.com/dimaystinov/bot_hnushka
2. Нажмите "Add file" → "Create new file"
3. Создайте файл `.github/workflows/ci.yml`
4. Скопируйте содержимое из локального файла
5. Повторите для `codex-auto-improve.yml`

### Вариант 2: Через Personal Access Token

1. Создайте Personal Access Token с правами `workflow`
2. Используйте его для push:
   ```bash
   git remote set-url origin https://TOKEN@github.com/dimaystinov/bot_hnushka.git
   git push
   ```

### Вариант 3: Локально (для тестирования)

Workflow файлы уже созданы локально в `.github/workflows/`:
- `ci.yml` - CI/CD pipeline
- `codex-auto-improve.yml` - Автоматическое улучшение кода

Они будут работать при push через веб-интерфейс или PAT с правами workflow.

## Содержимое workflow файлов

См. файлы:
- `.github/workflows/ci.yml`
- `.github/workflows/codex-auto-improve.yml`

