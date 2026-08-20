import asyncio
import secrets
from datetime import datetime
from random import randint

from faststream.kafka import KafkaBroker, KafkaPublishMessage
from pydantic import BaseModel

from src.config import KafkaConfig


class TicketPurchasedMessage(BaseModel):
    payment_id: str
    event_id: int
    tickets_count: int
    total_amount: int
    paid_at: datetime


class TicketsPurchasedSimulationService:
    def __init__(self, config: KafkaConfig, broker: KafkaBroker) -> None:
        self._config = config
        self._broker = broker
        self._publish_concurrency = 100
        self._task = None

    async def start(self) -> None:
        async def _start():
            while True:
                await self.run_simulation()
                await asyncio.sleep(10)

        self._task = asyncio.create_task(_start())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()

    async def run_simulation(self) -> None:
        payloads = [
            TicketPurchasedMessage(
                payment_id=secrets.token_hex(8),
                event_id=randint(1, 5),
                tickets_count=randint(1, 10),
                total_amount=randint(1000, 10000),
                paid_at=datetime.now(),
            )
            for _ in range(5)
        ]
        await self._publish_payloads(payloads=payloads)

    async def _publish_payloads(self, payloads: list[TicketPurchasedMessage]) -> None:
        for start in range(0, len(payloads), self._publish_concurrency):
            chunk = payloads[start : start + self._publish_concurrency]

            await self._broker.publish_batch(
                *[
                    KafkaPublishMessage(
                        body=event,
                        key=event.event_id.to_bytes(),
                    )
                    for event in chunk
                ],
                topic=self._config.TICKETS_TOPIC,
            )
