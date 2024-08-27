import asyncio
import logging
import random
import signal
from functools import partial

from src.app.db.repository import DatabaseRepository, fill_db
from src.app.services.keydb import init_keydb, keydb_perform_task
from src.app.services.rabbitmq import (
    connect_to_rabbitmq,
    consume_messages,
    declare_queue,
    publish_message,
)
from src.app.services.transactions import fill_keydb, publish_message_to_db
from src.app.utils import generate_message, shutdown

LOGGING_FORMAT = "[%(filename)s:%(lineno)d] | %(levelname)-8s | %(message)s"
logger = logging.getLogger()


def configure_logger() -> None:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


async def main() -> None:
    configure_logger()

    # Initialize the database
    repo = DatabaseRepository()
    await repo.init()
    await fill_db(repo)
    provider_dict = await repo.get_provider_names()

    # Initialize RabbitMQ
    channel = await connect_to_rabbitmq()
    queue = await declare_queue(channel)

    # Initialize KeyDB
    keydb = await init_keydb()
    await fill_keydb(keydb, repo, provider_dict)

    # Define the message handler
    message_handler = partial(publish_message_to_db, repo)

    # Start consuming messages in the background
    consume_task = asyncio.create_task(consume_messages(queue, message_handler))

    # Register signals for shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, lambda s=sig: asyncio.create_task(shutdown(loop, signal=s))
        )

    try:
        while True:
            # Generate and publish a new message
            message = generate_message()
            await publish_message(channel, id_=message["id"], value=message["value"])

            # Wait before publishing the next message
            await asyncio.sleep(random.randint(10, 40))

    except asyncio.CancelledError:
        logger.info("Main loop cancelled, performing shutdown.")

    await repo.close()
    await channel.close()  # Close RabbitMQ channel when done
    await consume_task  # Ensure the consume task completes


if __name__ == "__main__":
    asyncio.run(main())
