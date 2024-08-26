import asyncio
import json
import logging
from typing import Callable

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

    logger.info("Connected to RabbitMQ.")
    return channel


@with_retry()
async def declare_queue(
    channel: aio_pika.RobustChannel,
) -> aio_pika.abc.AbstractRobustQueue:
    queue = await channel.declare_queue(settings.RABBITMQ_QUEUE_NAME, durable=True)

    logger.info(f"Declared queue: {settings.RABBITMQ_QUEUE_NAME}")
    return queue


@with_retry()
async def publish_message(
    channel: aio_pika.RobustChannel, id_: int, value: int
) -> None:
    message = {"id": id_, "value": value}
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(message).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=settings.RABBITMQ_QUEUE_NAME,
    )
    logger.info(f" [x] Sent {message}")


@with_retry()
async def consume_messages(
    queue: aio_pika.abc.AbstractRobustQueue, message_handler: Callable
) -> None:
    await queue.consume(message_handler, no_ack=False)
    logger.info(f"Started consuming messages from {settings.RABBITMQ_QUEUE_NAME}")

    await asyncio.Future()
