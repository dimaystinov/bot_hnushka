#!/usr/bin/env bash
set -e

echo "🧪 Testing and Debugging with Codex"

# Создаем временный файл для тестов
TEST_FILE=".codex/test_results.txt"
mkdir -p .codex

codex exec --full-auto --sandbox danger-full-access "
TASK: Test the application and catch bugs

1. Check if the bot can start:
   - Try: python -c 'from config import settings; print(\"OK\")'
   - Try: python -c 'from bot.utils.logger import logger; logger.info(\"OK\")'
   - Try: python -c 'from bot.handlers import common, media; print(\"OK\")'

2. Check for import errors:
   - Try importing all main modules
   - Check for missing dependencies
   - Verify all imports are correct

3. Check for runtime errors:
   - Validate configuration loading
   - Check database initialization
   - Verify service initialization

4. Check for logical errors:
   - Review async/await usage
   - Check error handling
   - Verify resource cleanup

5. Check for potential bugs:
   - Race conditions
   - Memory leaks
   - Unclosed resources
   - Missing error handling

6. If bugs found:
   - Fix them immediately
   - Add tests if possible
   - Document the fix

7. Run basic validation:
   - Check syntax: python -m py_compile main.py
   - Check imports: python -c 'import main'
   - Validate config: python -c 'from config import settings'

8. Output results to .codex/test_results.txt
"

echo "✅ Testing completed. Check .codex/test_results.txt for results."

