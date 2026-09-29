#!/data/data/com.termux/files/usr/bin/bash

cd "$HOME/football_ai" || exit 1

export TZ=Africa/Nairobi

echo "=================================================="
echo "FOOTBALL AI — AUTOMATIC 12-HOUR REFRESH"
echo "=================================================="
echo "NAIROBI TIME:"
date '+%Y-%m-%d %H:%M:%S %Z'
echo "TARGET DATE:"
date '+%Y-%m-%d'
echo "=================================================="

python - <<'PY'
from datetime import date
from app.worldwide_daily_manager import WorldwideDailyDataManager

target_date = date.today().isoformat()

print("RUNNING DAILY MANAGER FOR:", target_date)

manager = WorldwideDailyDataManager()
result = manager.run(target_date=target_date)

print("=" * 80)
print("REFRESH RESULT")
print("=" * 80)
print("STATUS      :", result.get("status"))
print("TODAY GAMES :", result.get("today_count"))
print("TOMORROW    :", result.get("tomorrow_count"))
print("SAVED TODAY :", len(result.get("today_ids", [])))
print("SAVED TOMORROW:", len(result.get("tomorrow_ids", [])))
print("=" * 80)
PY
