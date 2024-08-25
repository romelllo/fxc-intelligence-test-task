from tortoise import Tortoise, run_async

from src.app.db.models import HistoricalTransaction, InitialData
from src.app.settings import settings


class DatabaseRepository:
    def __init__(self):
        self.db_url = settings.postgresql_url

    async def init(self):
        # Initialize Tortoise ORM
        await Tortoise.init(
            db_url=self.db_url, modules={"models": ["src.app.db.models"]}
        )
        # Generate the schema
        await Tortoise.generate_schemas()

    async def insert_initial_data(
        self, provider_name: str, initial_value: float
    ) -> int:
        data = await InitialData.create(
            provider_name=provider_name, initial_value=initial_value
        )
        return data.id

    async def insert_historical_transaction(
        self,
        provider_id: int,
        transaction_value: float,
    ) -> int:
        provider_instance = await InitialData.get(id=provider_id)

        transaction = await HistoricalTransaction.create(
            provider_id=provider_instance, transaction_value=transaction_value
        )
        return transaction.id

    async def close(self) -> None:
        # Close the connection
        await Tortoise.close_connections()


# Entry point for asynchronous execution
async def main():
    repo = DatabaseRepository()

    await repo.init()

    # Insert initial data
    visa_id = await repo.insert_initial_data("Visa", 1000.00)

    # Insert a historical transaction
    await repo.insert_historical_transaction(visa_id, 600.00)

    await repo.close()


if __name__ == "__main__":
    run_async(main())
