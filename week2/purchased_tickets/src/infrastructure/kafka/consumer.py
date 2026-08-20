from dishka import AsyncContainer, Scope
from faststream import AckPolicy
from faststream.kafka import KafkaBroker

from src.config import KafkaConfig
from src.infrastructure.kafka.schemas import TicketPurchasedEvent
from src.services.aggregation import PurchasedTicketsAggregationService
from src.services.websocket_gps_broadcaster import WebsocketGPSBroadcaster


def create_kafka_broker(config: KafkaConfig, container: AsyncContainer):
    broker = KafkaBroker(
        bootstrap_servers=config.BOOTSTRAP_SERVERS,
    )

    @broker.subscriber(
        config.TICKETS_TOPIC,
        batch=True,
        group_id=config.GROUP_ID,
        auto_offset_reset="earliest",
        ack_policy=AckPolicy.NACK_ON_ERROR,
        max_records=200,
        batch_timeout_ms=500,
    )
    async def process_gps_events(messages: list[TicketPurchasedEvent]):
        async with container(scope=Scope.REQUEST) as rq_container:
            tracking_service = await rq_container.get(
                PurchasedTicketsAggregationService
            )
            events = await tracking_service.process(messages)

            broadcaster_service = await rq_container.get(
                WebsocketGPSBroadcaster
            )
            await broadcaster_service.broadcast_purchased_tickets_events(events=events)

    return broker
