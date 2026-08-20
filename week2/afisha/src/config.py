from functools import cached_property

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    HOST: str = "localhost"
    PORT: int = 7432
    USER: str = "afisha"
    PASS: SecretStr = SecretStr("afisha")
    NAME: str = "afisha"

    ECHO: bool = False
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20

    @cached_property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASS.get_secret_value()}@{self.HOST}:{self.PORT}/{self.NAME}"


class RedisConfig(BaseModel):
    HOST: str = "localhost"
    PORT: int = 7379
    DB_NUMBER: int = 0

    @cached_property
    def url(self) -> str:
        return f"redis://{self.HOST}:{self.PORT}/{self.DB_NUMBER}"


class PaymentConfig(BaseModel):
    HOST: str = "localhost"
    PROTO: str = "http"
    PORT: int = 9001

    @cached_property
    def url(self) -> str:
        return f"{self.PROTO}://{self.HOST}:{self.PORT}"


class ProtectionConfig(PaymentConfig):
    PORT: int = 9002


class KafkaConfig(BaseModel):
    BOOTSTRAP_SERVERS: str = "localhost:9092"
    TICKETS_TOPIC: str = "tickets.purchased"


class Config(BaseSettings):
    BOOKING_TTL_MINUTES: int = 15

    DB: DatabaseConfig = DatabaseConfig()
    REDIS: RedisConfig = RedisConfig()
    PAYMENT: PaymentConfig = PaymentConfig()
    PROTECTION: ProtectionConfig = ProtectionConfig()
    KAFKA: KafkaConfig = KafkaConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


config = Config()
