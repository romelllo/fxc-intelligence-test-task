from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_HOST: str
    FORWARD_RABBITMQ_PORT: int = 5672
    RABBITMQ_QUEUE_NAME: str

    KEYDB_HOST: str
    KEYDB_PORT: int = 6379

    @property
    def postgresql_url(self) -> str:
        return (
            f"postgres://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def keydb_url(self) -> str:
        return f"redis://{self.KEYDB_HOST}:{self.KEYDB_PORT}"


settings = Settings()
