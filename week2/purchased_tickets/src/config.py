from functools import cached_property

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    HOST: str = "localhost"
    PORT: int = 7432
    USER: str = "purchased_tickets"
    PASS: SecretStr = SecretStr("purchased_tickets")
    NAME: str = "purchased_tickets"

    ECHO: bool = False
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20

    @cached_property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASS.get_secret_value()}@{self.HOST}:{self.PORT}/{self.NAME}"


class KafkaConfig(BaseModel):
    BOOTSTRAP_SERVERS: str = "localhost:9092"
    TICKETS_TOPIC: str = "tickets.purchased"
    GROUP_ID: str = "tickets.purchased"


class Config(BaseSettings):
    BOOKING_TTL_MINUTES: int = 15

    DB: DatabaseConfig = DatabaseConfig()
    KAFKA: KafkaConfig = KafkaConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


config = Config()
