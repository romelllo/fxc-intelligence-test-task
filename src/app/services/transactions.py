import json
import logging

import aio_pika
from redis import asyncio as aioredis

from src.app.db.repository import DatabaseRepository
from src.app.services.keydb import keydb_perform_task
from src.app.utils import with_retry

logger = logging.getLogger(__name__)


@with_retry()
async def publish_message_to_db(
    repo: DatabaseRepository, message: aio_pika.IncomingMessage
):
    async with message.process():
        try:
            body = json.loads(message.body)
            logger.info(f"Received message from RabbitMQ: {body}")

            if "id" not in body or "value" not in body:
                logger.error(f"Invalid message content from RabbitMQ: {body}")
                return

            await repo.insert_historical_transaction(
                provider_id=body["id"], transaction_value=body["value"]
            )
            logger.info(f"Published message to historical_transactions DB table")

        except json.JSONDecodeError:
            logger.error("Failed to decode message")


@with_retry()
async def fill_keydb(
    keydb: aioredis.Redis, repo: DatabaseRepository, provider_dict: dict
) -> None:
    await keydb_perform_task(keydb, key="key", value="value")

    initial_data = await repo.get_initial_data()
    historical_data = await repo.get_historical_transactions_by_provider()

    combined_data = {}
    for provider_id, initial_value in initial_data.items():
        combined_value = initial_value + historical_data.get(provider_id, 0)
        combined_data[provider_id] = combined_value

    for provider_id, value in combined_data.items():
        await keydb_perform_task(
            keydb, key=f"{provider_id}_{provider_dict.get(provider_id)}", value=value
        )

    logger.info("Filled KeyDB based on initial DB tables state")
