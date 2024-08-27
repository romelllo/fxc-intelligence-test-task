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
