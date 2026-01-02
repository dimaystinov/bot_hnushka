# ⚠️ КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ О БЕЗОПАСНОСТИ

## Обнаружена утечка API ключей

**Дата:** 2026-01-02  
**Проблема:** В README.md были обнаружены реальные API ключи и токены

### Скомпрометированные ключи:

1. **Telegram Bot Token**
   - Токен: `[REMOVED_BOT_TOKEN]`
   - **ДЕЙСТВИЕ:** Немедленно отзовите этот токен через [@BotFather](https://t.me/BotFather) в Telegram
   - Создайте новый токен и обновите его в `.env`

2. **OpenRouter API Key**
   - Ключ: `[REMOVED_API_KEY]`
   - **ДЕЙСТВИЕ:** Немедленно отзовите этот ключ на [OpenRouter.ai](https://openrouter.ai/keys)
   - Создайте новый ключ и обновите его в `.env`

## Что было сделано:

1. ✅ Удалены все реальные ключи из README.md
2. ✅ Заменены на placeholder значения
3. ✅ Изменения отправлены в репозиторий

## ⚠️ ВАЖНО: История Git

**Проблема:** Ключи остались в истории Git коммитов!

Даже после удаления из README, ключи все еще доступны в истории коммитов на GitHub.

### Решение: Очистка истории Git

#### Вариант 1: Использовать git filter-repo (рекомендуется)

```bash
# Установить git-filter-repo
pip install git-filter-repo

# Удалить ключи из истории
cd /root/bot_hnushka
git filter-repo --invert-paths --path README.md --force

# Или удалить конкретные строки
git filter-repo --replace-text <(echo "[REMOVED_BOT_TOKEN]==>YOUR_BOT_TOKEN_HERE")
git filter-repo --replace-text <(echo "[REMOVED_API_KEY]==>YOUR_OPENROUTER_KEY_HERE")

# Принудительно отправить (ОСТОРОЖНО! Это перезапишет историю)
git push origin --force --all
```

#### Вариант 2: Создать новый репозиторий (проще)

```bash
# Создать новый репозиторий
gh repo create bot_hnushka_new --public

# Скопировать только текущее состояние (без истории)
cd /root/bot_hnushka
git checkout --orphan new-main
git add .
git commit -m "Initial commit (cleaned)"
git remote set-url origin https://github.com/dimaystinov/bot_hnushka_new.git
git push -u origin new-main --force
```

#### Вариант 3: Использовать BFG Repo-Cleaner

```bash
# Скачать BFG
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

# Создать файл с ключами для удаления
echo "[REMOVED_BOT_TOKEN]" > keys.txt
echo "[REMOVED_API_KEY]" >> keys.txt

# Очистить историю
java -jar bfg-1.14.0.jar --replace-text keys.txt /root/bot_hnushka

# Очистить и отправить
cd /root/bot_hnushka
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin --force --all
```

## Немедленные действия:

1. **Отзовите все скомпрометированные ключи:**
   - Telegram Bot Token через @BotFather
   - OpenRouter API Key через веб-интерфейс

2. **Создайте новые ключи:**
   - Новый Telegram Bot Token
   - Новый OpenRouter API Key

3. **Обновите `.env` файл** с новыми ключами

4. **Очистите историю Git** (выберите один из вариантов выше)

5. **Проверьте логи** на предмет несанкционированного доступа

## Предотвращение в будущем:

1. ✅ `.gitignore` уже настроен для игнорирования `.env`
2. ✅ Используйте только `env.example` в репозитории
3. ✅ Никогда не коммитьте реальные ключи
4. ✅ Используйте секретные менеджеры для продакшена
5. ✅ Регулярно проверяйте репозиторий на наличие секретов

## Инструменты для проверки:

```bash
# Проверить наличие секретов в репозитории
grep -r "sk-or\|BOT_TOKEN\|API_KEY" --exclude-dir=.git .

# Использовать git-secrets
git secrets --install
git secrets --register-aws
git secrets --scan

# Использовать truffleHog
pip install truffleHog
truffleHog git file:///root/bot_hnushka
```

## Контакты для экстренных случаев:

- **Telegram Bot Support:** [@BotSupport](https://t.me/BotSupport)
- **OpenRouter Support:** support@openrouter.ai
- **GitHub Security:** https://github.com/security

---

**ВАЖНО:** Эта проблема была обнаружена и исправлена. Все ключи должны быть немедленно отозваны и заменены!

