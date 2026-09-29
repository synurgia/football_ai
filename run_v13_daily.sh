#!/data/data/com.termux/files/usr/bin/bash

cd "$HOME/football_ai" || exit 1

LOG="$HOME/football_ai/logs/v13_daily_$(date +%Y-%m-%d).log"
mkdir -p "$HOME/football_ai/logs"

echo "=== V1.3 DAILY RUN START $(date -Iseconds) ===" >> "$LOG"

python - <<'PY' >> "$LOG" 2>&1
import asyncio
import inspect

from app.worldwide_daily_manager import WorldwideDailyDataManager

manager = WorldwideDailyDataManager()
result = manager.run()

if inspect.isawaitable(result):
    result = asyncio.run(result)

print("V1.3 DAILY MANAGER RESULT:")
print(result)
PY

echo "=== V1.3 DAILY RUN END $(date -Iseconds) ===" >> "$LOG"
