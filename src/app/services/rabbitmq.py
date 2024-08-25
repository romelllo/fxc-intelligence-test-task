import asyncio
import json
import logging

import aio_pika

from src.app.settings import settings
from src.app.utils import with_retry

logger = logging.getLogger(__name__)


@with_retry()
async def connect_to_rabbitmq() -> aio_pika.RobustChannel:
    connection = await aio_pika.connect_robust(
        host=settings.RABBITMQ_HOST,
        port=settings.FORWARD_RABBITMQ_PORT,
        login=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASSWORD,
    )

    channel = await connection.channel()

    await channel.declare_queue(settings.RABBITMQ_QUEUE_NAME, durable=True)

    logger.info("Connected to RabbitMQ and declared queue.")
    return channel


@with_retry()
async def publish_message(channel: aio_pika.RobustChannel, id: int, value: int):
    if not channel or channel.is_closed:
        logger.error("Cannot publish message, channel is closed.")
        return

    message = {"id": id, "value": value}
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(message).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=settings.RABBITMQ_QUEUE_NAME,
    )
    logger.info(f" [x] Sent {message}")
