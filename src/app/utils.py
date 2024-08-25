import asyncio
import logging
from functools import wraps

from tortoise.exceptions import DBConnectionError

logger = logging.getLogger(__name__)


def with_retry(max_retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except DBConnectionError as e:
                    retries += 1
                    logger.error(
                        f"Retry {retries}/{max_retries} failed with error: {e}"
                    )
                    if retries < max_retries:
                        await asyncio.sleep(delay)
                    else:
                        logger.error("Max retries reached. Raising the exception.")
                        raise

        return wrapper

    return decorator
