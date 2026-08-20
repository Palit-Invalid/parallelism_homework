from collections.abc import AsyncIterator

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from faststream.kafka import KafkaBroker

from src.config import Config, KafkaConfig
from src.infrastructure.db.manager import DBManager, session_maker
from src.infrastructure.kafka.consumer import create_kafka_broker
from src.infrastructure.websocket.manager import WebsocketManager
from src.services.aggregation import PurchasedTicketsAggregationService
from src.services.websocket_gps_broadcaster import WebsocketGPSBroadcaster


class ConfigProvider(Provider):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self._config = config

    @provide(scope=Scope.APP)
    def get_config(self) -> Config:
        return self._config

    @provide(scope=Scope.APP)
    def get_kafka_config(self) -> KafkaConfig:
        return self._config.KAFKA


class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_db(self) -> AsyncIterator[DBManager]:
        async with DBManager(session_maker) as db:
            yield db


class KafkaProvider(Provider):
    @provide(scope=Scope.APP)
    def get_kafka_broker(
        self,
        config: KafkaConfig,
        container: AsyncContainer,
    ) -> KafkaBroker:
        return create_kafka_broker(config, container)


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_agregation_service(
        self,
        db: DBManager,
    ) -> PurchasedTicketsAggregationService:
        return PurchasedTicketsAggregationService(db=db)

    @provide(scope=Scope.REQUEST)
    def get_ws_broadcaster(
        self,
        ws_manager: WebsocketManager,
    ) -> WebsocketGPSBroadcaster:
        return WebsocketGPSBroadcaster(ws_manager=ws_manager)


class WebsocketInfrastructureProvider(Provider):
    @provide(scope=Scope.APP)
    def get_ws_manager(self) -> WebsocketManager:
        return WebsocketManager()


def create_container(config: Config):
    return make_async_container(
        ConfigProvider(config=config),
        DatabaseProvider(),
        KafkaProvider(),
        ServiceProvider(),
        WebsocketInfrastructureProvider(),
    )
