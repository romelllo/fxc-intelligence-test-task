import json
import logging

import aio_pika

from src.app.db.repository import DatabaseRepository
from src.app.utils import with_retry

logger = logging.getLogger(__name__)


@with_retry()
async def publish_message_to_db(
    repo: DatabaseRepository, message: aio_pika.IncomingMessage
):
    async with message.process():
        try:
            body = json.loads(message.body)
            logger.info(f"Received message: {body}")

            if "id" not in body or "value" not in body:
                logger.error(f"Invalid message content: {body}")
                return

            await repo.insert_historical_transaction(
                provider_id=body["id"], transaction_value=body["value"]
            )
            logger.info(f"Published message to historical_transactions table")

        except json.JSONDecodeError:
            logger.error("Failed to decode message")
