import logging

from tortoise import Tortoise, exceptions

from src.app.db.models import HistoricalTransaction, InitialData
from src.app.settings import settings
from src.app.utils import with_retry

logger = logging.getLogger(__name__)


class DatabaseRepository:
    def __init__(self):
        self.db_url = settings.postgresql_url

    @with_retry()
    async def init(self):
        await Tortoise.init(
            db_url=self.db_url, modules={"models": ["src.app.db.models"]}
        )
        # Generate the schema
        await Tortoise.generate_schemas()
        logger.info("Database initialized successfully.")

    @with_retry()
    async def insert_initial_data(
        self, provider_name: str, initial_value: float
    ) -> int:
        data = await InitialData.create(
            provider_name=provider_name, initial_value=initial_value
        )
        logger.info(f"Inserted initial data: {provider_name}, {initial_value}")
        return data.id

    @with_retry()
    async def insert_historical_transaction(
        self,
        provider_id: int,
        transaction_value: float,
    ) -> int:
        try:
            # Retrieve the InitialData instance
            provider_instance = await InitialData.get(id=provider_id)

            transaction = await HistoricalTransaction.create(
                provider_id=provider_instance, transaction_value=transaction_value
            )
            logger.info(
                f"Inserted historical transaction: {transaction_value} for provider {provider_instance.provider_name}"
            )
            return transaction.id
        except exceptions.DoesNotExist:
            logger.error(f"Provider with ID {provider_id} does not exist.")
            raise

    @with_retry()
    async def close(self) -> None:
        # Close the connection
        await Tortoise.close_connections()
        logger.info("Database connection closed successfully.")


async def fill_db(repo: DatabaseRepository) -> None:
    # asyncio.sleep(10)

    # Insert initial data
    visa_id = await repo.insert_initial_data("Visa", 1000.00)
    mastercard_id = await repo.insert_initial_data("Mastercard", 2000.00)

    # Insert historical transactions
    await repo.insert_historical_transaction(visa_id, 100.00)
    await repo.insert_historical_transaction(visa_id, 200.00)
    await repo.insert_historical_transaction(mastercard_id, -200.00)
