import asyncio
import logging
import random
from functools import wraps

from src.app.constants import ORG_COUNT

logger = logging.getLogger(__name__)


def with_retry(max_attempts=10, delay=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt_count = 0
            while attempt_count < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt_count += 1
                    logging.error(f"Attempt {attempt_count} failed with error: {e}")
                    await asyncio.sleep(delay)
            else:
                logging.error("Max attempts reached. Operation failed.")
                return None

        return wrapper

    return decorator


def generate_message():
    return {"id": random.randint(1, ORG_COUNT), "value": random.randint(-1000, 1000)}


async def shutdown(loop, signal=None):
    """Cleanup tasks tied to the service's shutdown."""
    if signal:
        logger.info(f"Received exit signal {signal.name}...")

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    logger.info(f"Cancelling {len(tasks)} outstanding tasks")
    [task.cancel() for task in tasks]

    logger.info("Shutting down...")
    loop.stop()

    await asyncio.gather(*tasks, return_exceptions=True)
    loop.close()

    logger.info("Shutdown complete.")
