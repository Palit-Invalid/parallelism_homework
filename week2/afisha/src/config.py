from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 7432
    user: str = "postgres"
    password: SecretStr = SecretStr("postgres")
    database: str = "postgres"

    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20

    @property
    def url(self) -> str:
        print(self.user)
        return (
            f"postgresql+asyncpg://{self.user}:"
            f"{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.database}"
        )


class Config(BaseSettings):
    PAYMENT_API_URL: str = "http://localhost:9001"
    PROTECTION_API_URL: str = "http://localhost:9002"
    REDIS_URL: str = "redis://localhost:7379/0"
    BOOKING_TTL_MINUTES: int = 15

    db: DatabaseConfig = DatabaseConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


config = Config()
