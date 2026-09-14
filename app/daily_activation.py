import asyncio
import logging
from datetime import date

from app.worldwide_daily_manager import WorldwideDailyDataManager

logger = logging.getLogger(__name__)


async def run_daily_activation():
    manager = WorldwideDailyDataManager()

    while True:
        try:
            result = manager.run(target_date=date.today().isoformat())
            logger.info(
                "Daily activation complete: %s",
                result.get("today", {}),
            )
        except Exception:
            logger.exception("Daily activation failed")

        await asyncio.sleep(3600)


def run_once():
    manager = WorldwideDailyDataManager()
    return manager.run(target_date=date.today().isoformat())
