import asyncio
import json
import logging

import aio_pika
from redis import asyncio as aioredis

from src.app.db.repository import DatabaseRepository
from src.app.services.keydb import get_value_from_keydb, keydb_perform_task
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
async def update_keydb_with_new_transaction(
    keydb: aioredis.Redis, repo: DatabaseRepository, provider_dict: dict[int, str]
) -> None:
    last_processed_id = await get_value_from_keydb(keydb, key="last_processed_id")

    # Check if this is the first run (i.e., no transactions processed yet)
    is_first_run = int(last_processed_id) == 0

    # Get new transactions since the last processed ID
    new_transactions = await repo.get_new_historical_transactions(
        int(last_processed_id)
    )

    if not new_transactions:
        return  # No new transactions to process

    # Combine new transactions from DB and existing values from KeyDB
    combined_data = {}

    for transaction in new_transactions:
        provider_id = transaction.provider_id_id
        combined_value = combined_data.get(provider_id, 0) + float(
            transaction.transaction_value
        )
        combined_data[provider_id] = combined_value

    # If it's the first run, include initial data in the combined values
    if is_first_run:
        initial_data = await repo.get_initial_data()
        for provider_id, initial_value in initial_data.items():
            combined_data[provider_id] = (
                combined_data.get(provider_id, 0) + initial_value
            )

    # Update KeyDB with combined values
    for provider_id, value in combined_data.items():
        # Get the current value in KeyDB (if any) and add the new combined value
        provider_key = f"{provider_id}_{provider_dict.get(provider_id)}"
        existing_value = await get_value_from_keydb(keydb, key=provider_key)
        updated_value = existing_value + value

        # Update KeyDB
        await keydb_perform_task(keydb, key=provider_key, value=updated_value)

    # Update the last processed ID in KeyDB
    if new_transactions:
        last_processed_id = max(transaction.id for transaction in new_transactions)
        await keydb_perform_task(
            keydb, key="last_processed_id", value=last_processed_id
        )
        logger.info(f"Updated last_processed_id to {last_processed_id}")


@with_retry()
async def update_keydb_periodically(
    keydb: aioredis.Redis, repo: DatabaseRepository, provider_dict: dict
) -> None:
    while True:
        await asyncio.sleep(60)  # Wait 60 seconds
        logger.info("Updating KeyDB with latest values from the DB")
        await update_keydb_with_new_transaction(keydb, repo, provider_dict)
