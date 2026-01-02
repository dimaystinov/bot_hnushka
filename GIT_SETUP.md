# Настройка Git репозитория

## ✅ Текущий статус

Git репозиторий инициализирован и готов к использованию:
- Репозиторий: `/root/bot_hnushka`
- Ветка: `main`
- Первый коммит: создан (26 файлов, 3211 строк)
- **GitHub CLI установлен и авторизован** ✅
  - Пользователь: `dimaystinov`
  - Авторизация через браузер выполнена
  - Git теперь работает автоматически с GitHub

## ⚠️ Важно: Аутентификация в Git

**GitHub и GitLab больше НЕ поддерживают аутентификацию по паролю!**

Для работы с git репозиториями нужно использовать один из двух методов:
1. **SSH ключи** (рекомендуется) - самый безопасный и удобный способ
2. **Personal Access Token (PAT)** - для HTTPS соединений

---

## Добавление remote репозитория (GitHub/GitLab)

### Вариант 1: GitHub (через SSH - рекомендуется)

#### Шаг 1: Создание SSH ключа (если еще нет)

```bash
# Проверить существующие SSH ключи
ls -la ~/.ssh

# Создать новый SSH ключ (если нет)
ssh-keygen -t ed25519 -C "your.email@example.com"
# Нажмите Enter для сохранения в стандартное место
# Можно оставить passphrase пустым (Enter) или установить пароль

# Показать публичный ключ для копирования
cat ~/.ssh/id_ed25519.pub
```

#### Шаг 2: Добавление SSH ключа на GitHub

1. Скопируйте содержимое `~/.ssh/id_ed25519.pub`
2. Перейдите на GitHub: https://github.com/settings/keys
3. Нажмите "New SSH key"
4. Вставьте ключ и сохраните

#### Шаг 3: Проверка подключения

```bash
ssh -T git@github.com
# Должно появиться: "Hi username! You've successfully authenticated..."
```

#### Шаг 4: Создание репозитория и добавление remote

1. **Создайте репозиторий на GitHub:**
   - Перейдите на https://github.com/new
   - Создайте новый репозиторий (например, `bot_hnushka`)
   - **НЕ** инициализируйте его с README, .gitignore или лицензией

2. **Добавьте remote и отправьте код:**
   ```bash
   cd /root/bot_hnushka
   
   # Добавить remote через SSH (замените YOUR_USERNAME на ваш GitHub username)
   git remote add origin git@github.com:YOUR_USERNAME/bot_hnushka.git
   
   # Отправить код
   git push -u origin main
   ```

### Вариант 1.2: GitHub (через HTTPS с Personal Access Token)

#### Шаг 1: Создание Personal Access Token

1. Перейдите на GitHub: https://github.com/settings/tokens
2. Нажмите "Generate new token" → "Generate new token (classic)"
3. Установите срок действия и права доступа:
   - Минимум: `repo` (полный доступ к репозиториям)
   - Для приватных репозиториев: `repo` (все права)
4. Нажмите "Generate token"
5. **ВАЖНО:** Скопируйте токен сразу! Он показывается только один раз

#### Шаг 2: Использование токена

```bash
cd /root/bot_hnushka

# Добавить remote через HTTPS
git remote add origin https://github.com/YOUR_USERNAME/bot_hnushka.git

# При push/pull будет запрошен пароль:
# Username: ваш_github_username
# Password: вставьте_ваш_PAT_токен (НЕ пароль от GitHub!)

# Отправить код
git push -u origin main
```

**Альтернатива:** Сохранить токен в git credential helper:
```bash
# Сохранить токен (будет запрошен один раз)
git config --global credential.helper store

# При первом push введите:
# Username: ваш_github_username
# Password: ваш_PAT_токен
```

### Вариант 2: GitLab (через SSH - рекомендуется)

#### Шаг 1: Создание SSH ключа (если еще нет)

```bash
# Используйте тот же SSH ключ, что и для GitHub, или создайте новый
ssh-keygen -t ed25519 -C "your.email@example.com"
cat ~/.ssh/id_ed25519.pub
```

#### Шаг 2: Добавление SSH ключа на GitLab

1. Скопируйте содержимое `~/.ssh/id_ed25519.pub`
2. Перейдите на GitLab: https://gitlab.com/-/profile/keys
3. Вставьте ключ и сохраните

#### Шаг 3: Создание проекта и добавление remote

1. **Создайте проект на GitLab:**
   - Перейдите на https://gitlab.com/projects/new
   - Создайте новый проект

2. **Добавьте remote и отправьте код:**
   ```bash
   cd /root/bot_hnushka
   
   # Добавить remote через SSH (замените YOUR_USERNAME на ваш GitLab username)
   git remote add origin git@gitlab.com:YOUR_USERNAME/bot_hnushka.git
   
   # Отправить код
   git push -u origin main
   ```

### Вариант 2.2: GitLab (через HTTPS с Personal Access Token)

1. Создайте токен: https://gitlab.com/-/user_settings/personal_access_tokens
2. Установите права: `write_repository`, `read_repository`
3. Используйте токен как пароль при push/pull

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

### Работа с remote
```bash
# Посмотреть текущий remote
git remote -v

# Изменить URL remote (например, с HTTPS на SSH)
git remote set-url origin git@github.com:USERNAME/REPO.git

# Удалить remote
git remote remove origin
```

### Работа с коммитами
```bash
# Добавить изменения
git add .

# Создать коммит
git commit -m "Описание изменений"

# Отправить изменения
git push

# Если нужно указать токен в URL (не рекомендуется, но возможно)
git push https://TOKEN@github.com/USERNAME/REPO.git main

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

