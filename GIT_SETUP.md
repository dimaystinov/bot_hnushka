# Настройка Git репозитория

## ✅ Текущий статус

Git репозиторий инициализирован и готов к использованию:
- Репозиторий: `/root/bot_hnushka`
- Ветка: `main`
- Первый коммит: создан (26 файлов, 3211 строк)

## Добавление remote репозитория (GitHub/GitLab)

### Вариант 1: GitHub

1. **Создайте репозиторий на GitHub:**
   - Перейдите на https://github.com/new
   - Создайте новый репозиторий (например, `bot_hnushka`)
   - **НЕ** инициализируйте его с README, .gitignore или лицензией

2. **Добавьте remote и отправьте код:**
   ```bash
   cd /root/bot_hnushka
   
   # Добавить remote (замените YOUR_USERNAME на ваш GitHub username)
   git remote add origin https://github.com/YOUR_USERNAME/bot_hnushka.git
   
   # Или через SSH (если настроен SSH ключ)
   git remote add origin git@github.com:YOUR_USERNAME/bot_hnushka.git
   
   # Отправить код
   git push -u origin main
   ```

### Вариант 2: GitLab

1. **Создайте проект на GitLab:**
   - Перейдите на https://gitlab.com/projects/new
   - Создайте новый проект

2. **Добавьте remote и отправьте код:**
   ```bash
   cd /root/bot_hnushka
   
   # Добавить remote (замените YOUR_USERNAME на ваш GitLab username)
   git remote add origin https://gitlab.com/YOUR_USERNAME/bot_hnushka.git
   
   # Или через SSH
   git remote add origin git@gitlab.com:YOUR_USERNAME/bot_hnushka.git
   
   # Отправить код
   git push -u origin main
   ```

### Вариант 3: Другой Git хостинг

```bash
cd /root/bot_hnushka
git remote add origin <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
git push -u origin main
```

## Проверка текущего состояния

```bash
# Проверить статус
git status

# Посмотреть remote репозитории
git remote -v

# Посмотреть историю коммитов
git log --oneline

# Посмотреть ветки
git branch -a
```

## Полезные команды

### Работа с коммитами
```bash
# Добавить изменения
git add .

# Создать коммит
git commit -m "Описание изменений"

# Отправить изменения
git push

# Получить изменения
git pull
```

### Работа с ветками
```bash
# Создать новую ветку
git checkout -b feature/new-feature

# Переключиться на ветку
git checkout main

# Посмотреть все ветки
git branch
```

### Настройка git (если нужно изменить)
```bash
# Настроить имя пользователя
git config user.name "Ваше Имя"

# Настроить email
git config user.email "your.email@example.com"

# Посмотреть текущие настройки
git config --list
```

## Важно

⚠️ **Файл `.env` не добавлен в репозиторий** (благодаря `.gitignore`)
- Это правильно, так как он содержит секретные данные
- Не забудьте настроить `.env` на новом сервере

## Текущие настройки git

```bash
# Посмотреть настройки
git config --list --local
```

Текущие настройки:
- `user.name`: Bot Hnushka
- `user.email`: bot@hnushka.local

Можете изменить их, если нужно:
```bash
git config user.name "Ваше Имя"
git config user.email "your.email@example.com"
```

