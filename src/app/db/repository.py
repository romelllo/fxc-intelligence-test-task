import logging

from tortoise import Tortoise, exceptions

from src.app.db.models import HistoricalTransaction, InitialData
from src.app.settings import settings

logger = logging.getLogger(__name__)


class DatabaseRepository:
    def __init__(self):
        self.db_url = settings.postgresql_url

    async def init(self):
        try:
            # Initialize Tortoise ORM
            await Tortoise.init(
                db_url=self.db_url, modules={"models": ["src.app.db.models"]}
            )
            # Generate the schema
            await Tortoise.generate_schemas()
            logger.info("Database initialized successfully.")
        except exceptions.DBConnectionError as e:
            logger.error(f"Failed to initialize the database: {e}")
            raise

    async def insert_initial_data(
        self, provider_name: str, initial_value: float
    ) -> int:
        try:
            data = await InitialData.create(
                provider_name=provider_name, initial_value=initial_value
            )
            logger.info(f"Inserted initial data: {provider_name}, {initial_value}")
            return data.id
        except exceptions.DBConnectionError as e:
            logger.error(f"Failed to insert initial data: {e}")
            raise

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
        except exceptions.DBConnectionError as e:
            logger.error(f"Failed to insert historical transaction: {e}")
            raise

    async def close(self) -> None:
        try:
            # Close the connection
            await Tortoise.close_connections()
            logger.info("Database connection closed successfully.")
        except exceptions.DBConnectionError as e:
            logger.error(f"Failed to close the database connection: {e}")
            raise
