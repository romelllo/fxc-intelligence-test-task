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
        logger.info("Database initialized successfully")

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
    async def get_initial_data(self) -> dict[int, float]:
        initial_data = await InitialData.all()
        initial_data_dict = {
            data.id: float(data.initial_value) for data in initial_data
        }
        return initial_data_dict

    @with_retry()
    async def get_provider_names(self) -> dict[int, str]:
        initial_data = await InitialData.all()
        provider_dict = {data.id: data.provider_name for data in initial_data}
        return provider_dict

    @with_retry()
    async def insert_historical_transaction(
        self,
        provider_id: int,
        transaction_value: float,
    ) -> int:
        try:
            provider_instance = await InitialData.get(id=provider_id)

            transaction = await HistoricalTransaction.create(
                provider_id=provider_instance, transaction_value=transaction_value
            )
            logger.info(
                f"Inserted historical transaction: {transaction_value} for provider {provider_instance.provider_name}"
            )
            return transaction.id
        except exceptions.DoesNotExist:
            logger.error(f"Provider with ID {provider_id} does not exist")
            raise

    @with_retry()
    async def get_historical_transactions_by_provider(self) -> dict[int, float]:
        historical_transactions = await HistoricalTransaction.all()
        historical_data_dict = {}

        for transaction in historical_transactions:
            provider_id = transaction.provider_id_id
            if provider_id in historical_data_dict:
                historical_data_dict[provider_id] += float(
                    transaction.transaction_value
                )
            else:
                historical_data_dict[provider_id] = float(transaction.transaction_value)

        return historical_data_dict

    @with_retry()
    async def close(self) -> None:
        await Tortoise.close_connections()
        logger.info("Database connection closed successfully")


async def fill_db(repo: DatabaseRepository) -> None:
    # Insert initial data
    visa_id = await repo.insert_initial_data("Visa", 1000.00)
    mastercard_id = await repo.insert_initial_data("Mastercard", 2000.00)

    # Insert historical transactions
    await repo.insert_historical_transaction(visa_id, 100.00)
    await repo.insert_historical_transaction(visa_id, 200.00)
    await repo.insert_historical_transaction(mastercard_id, -200.00)

    logger.info("Filled DB tables with initial values")
