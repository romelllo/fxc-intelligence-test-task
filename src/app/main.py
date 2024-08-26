import asyncio
import logging
from functools import partial

from src.app.db.repository import DatabaseRepository, fill_db
from src.app.services.rabbitmq import (
    connect_to_rabbitmq,
    consume_messages,
    declare_queue,
    publish_message,
)
from src.app.services.transactions import publish_message_to_db

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

    repo = DatabaseRepository()
    await repo.init()

    await fill_db(repo)

    channel = await connect_to_rabbitmq()
    queue = await declare_queue(channel)

    await publish_message(channel, id_=1, value=100)

    message_handler = partial(publish_message_to_db, repo)
    await consume_messages(queue, message_handler)

    await repo.close()


if __name__ == "__main__":
    asyncio.run(main())
