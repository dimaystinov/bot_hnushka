#!/usr/bin/env bash
set -e

STATE=".codex"
MEMORY="$STATE/memory.md"
RULES="$STATE/rules.md"

mkdir -p "$STATE"
touch "$MEMORY"

ITER=0

while true; do
  ITER=$((ITER+1))
  echo "=============================="
  echo " Codex Iteration $ITER"
  echo "=============================="

  codex exec --full-auto --sandbox danger-full-access "
$(cat "$RULES")

PAST ITERATIONS MEMORY:
$(cat "$MEMORY")

TASK:
1. Analyze the entire codebase
2. Identify NEW issues only (do not repeat memory):
   - undefined behavior
   - data races / race conditions
   - logical errors
   - potential bugs
   - performance bottlenecks
   - non-production patterns
   - missing or unclear comments
3. If NO new issues exist:
   - Print exactly: NO_NEW_ISSUES
   - Do NOT modify code
   - Do NOT commit
   - Exit

4. If issues exist:
   - Fix ALL of them
   - Add clear English comments
   - Improve readability and structure
   - Optimize performance where safe
   - Remove ALL undefined behavior and races
   - Preserve behavior unless bugfix requires change

5. After fixes:
   - Run: git status
   - If there are NO changes: stop
   - Otherwise:
     - git add -A
     - Create ONE commit

COMMIT RULES:
- Write commit message as a senior engineer
- Use conventional commit style (fix/refactor/perf/safety/docs)
- Clear, concise, technical
- No emojis, no markdown, no explanations

6. Append a short summary of what was fixed to memory.md
"
  
  # Проверка сходимости по памяти
  if tail -n 5 "$MEMORY" | grep -q "NO_NEW_ISSUES"; then
    echo "✅ Code converged. No new issues."
    break
  fi

done

