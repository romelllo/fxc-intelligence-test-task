import asyncio
import logging
import time

from src.app.db.repository import DatabaseRepository
from src.app.services.rabbitmq import connect_to_rabbitmq, publish_message

LOGGING_FORMAT = "[%(filename)s:%(lineno)d] | %(levelname)-8s | %(message)s"
logger = logging.getLogger()


def configure_logger() -> None:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


async def init_db() -> None:
    repo = DatabaseRepository()

    time.sleep(10)

    # Initialize the database
    await repo.init()

    # Insert initial data
    visa_id = await repo.insert_initial_data("Visa", 1000.00)
    mastercard_id = await repo.insert_initial_data("Mastercard", 2000.00)

    # Insert historical transactions
    await repo.insert_historical_transaction(visa_id, 100.00)
    await repo.insert_historical_transaction(visa_id, 200.00)
    await repo.insert_historical_transaction(mastercard_id, -200.00)

    # Close the repository
    await repo.close()


async def main() -> None:
    configure_logger()
    await init_db()
    channel = await connect_to_rabbitmq()
    if channel:
        await publish_message(channel, 1, 100)


if __name__ == "__main__":
    asyncio.run(main())
