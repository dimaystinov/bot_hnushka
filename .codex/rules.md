# Codex Rules for bot_hnushka

## CRITICAL: Working Directory
- PROJECT ROOT: /root/bot_hnushka (or wherever bot_hnushka is located)
- You MUST work ONLY in bot_hnushka directory and its subdirectories
- NEVER change directory outside of bot_hnushka
- ALL file operations must be relative to bot_hnushka root
- Use relative paths: bot/handlers/media.py (NOT absolute paths)
- Current working directory should always be bot_hnushka root

## Project Context
- Python 3.10+ async Telegram bot using aiogram 3
- Processes voice messages with Whisper transcription
- Uses LLM chain (OpenRouter → local Ollama) for message classification
- SQLite database with SQLModel ORM
- Modular structure: handlers, services, storage, utils
- Project root: bot_hnushka directory

## Code Quality Standards

### Python Best Practices
- Use type hints everywhere
- Follow PEP 8 style guide
- Use async/await properly (no blocking I/O in async functions)
- Handle all exceptions explicitly
- Use context managers for resources
- No global mutable state

### Async Patterns
- All I/O operations must be async
- Use `asyncio.to_thread()` for CPU-bound operations
- Properly handle asyncio tasks and cancellation
- Use `asyncio.gather()` for parallel operations when safe
- Never use `time.sleep()` - use `asyncio.sleep()` instead

### Error Handling
- Log all errors with context
- Never silently swallow exceptions
- Use specific exception types
- Provide user-friendly error messages
- Implement retry logic for external API calls

### Database
- Always use transactions for multi-step operations
- Close database sessions properly
- Handle connection errors gracefully
- Use proper SQLModel relationships

### Security
- Never log sensitive data (tokens, passwords, API keys)
- Validate all user input
- Sanitize file paths
- Use parameterized queries (SQLModel does this automatically)

### Performance
- Avoid loading large files into memory
- Use streaming for large data
- Cache expensive operations when appropriate
- Optimize database queries (avoid N+1 problems)

### Testing & Debugging
- Code should be testable
- Functions should be pure when possible
- Avoid side effects in utility functions
- Add logging at key decision points

## Specific Requirements

### File Handling
- Download large files to disk, not memory
- Clean up temporary files
- Handle file size limits gracefully

### LLM Integration
- Implement proper fallback chain
- Handle rate limits and timeouts
- Cache responses when appropriate
- Validate LLM responses

### Telegram Bot
- Handle all Telegram API errors
- Implement proper rate limiting
- Send user-friendly error messages
- Progress updates for long operations

### Code Structure
- Single responsibility principle
- DRY (Don't Repeat Yourself)
- Clear function and variable names
- Document complex logic

## What to Fix

### Critical Issues
- Race conditions in async code
- Memory leaks (unclosed resources)
- Unhandled exceptions
- Blocking I/O in async functions
- SQL injection vulnerabilities (though SQLModel prevents this)

### Important Issues
- Missing type hints
- Unclear variable/function names
- Duplicated code
- Missing error handling
- Performance bottlenecks

### Nice to Have
- Better comments
- Code organization improvements
- Performance optimizations
- Code simplification

## What NOT to Change
- Working functionality (unless fixing a bug)
- API interfaces (unless breaking change is necessary)
- Database schema (unless migration is needed)
- External dependencies (unless security issue)

## Testing Requirements
- Code should be runnable
- No syntax errors
- No import errors
- Basic functionality should work
- Handle edge cases

## Bot Testing Checklist
When testing the bot, verify:
1. **Imports**: All modules can be imported without errors
2. **Configuration**: Settings can be loaded and validated
3. **Database**: Models can be imported, database can be initialized
4. **Services**: WhisperService, LLMClient can be instantiated
5. **Handlers**: All handlers can be imported and registered
6. **Startup**: Bot can start without immediate errors
7. **Error Handling**: All exceptions are caught and logged
8. **Resource Cleanup**: Files, connections are properly closed
9. **Async Safety**: No blocking operations in async functions
10. **Type Safety**: Type hints are correct and consistent

## Runtime Testing
- Test bot startup sequence
- Verify all services initialize correctly
- Check for memory leaks
- Verify error recovery
- Test graceful shutdown

