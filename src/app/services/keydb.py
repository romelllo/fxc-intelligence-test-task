import logging

from redis import asyncio as aioredis

from src.app.settings import settings
from src.app.utils import with_retry

logger = logging.getLogger(__name__)


@with_retry()
async def init_keydb() -> aioredis.Redis:
    keydb = await aioredis.from_url(settings.keydb_url, decode_responses=True)
    logger.info("Connected to KeyDB")
    return keydb


@with_retry()
async def keydb_perform_task(keydb: aioredis.Redis, key: str, value: str) -> None:
    await keydb.set(key, value)
    task_value = await keydb.get(key)
    logger.info(f"Set new value {task_value} for key {key} in KeyDB")


@with_retry()
async def get_value_from_keydb(keydb: aioredis.Redis, key: str) -> str | float:
    value = await keydb.get(key)
    if value is None:
        value = 0  # Assuming 0 as the initial value
        await keydb_perform_task(keydb, key=key, value=value)
    return float(value)
