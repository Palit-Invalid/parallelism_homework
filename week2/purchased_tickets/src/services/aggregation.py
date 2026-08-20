from uuid import uuid4

from src.infrastructure.db.manager import DBManager
from src.infrastructure.kafka.schemas import TicketPurchasedEvent
from src.log import logger
from src.schemas.event_payment_activity import EventPaymentActivityCreate


class PurchasedTicketsAggregationService:
    def __init__(self, db: DBManager) -> None:
        self.db = db

    async def process(self, messages: list[TicketPurchasedEvent]) -> list[EventPaymentActivityCreate]:
        insert_data = self._aggregate(messages=messages)

        await self.db.event_payment_activity.add_bulk(insert_data)
        await self.db.commit()

        return insert_data

    def _aggregate(self, messages: list[TicketPurchasedEvent]) -> list[EventPaymentActivityCreate]:
        aggregated_data: dict[int, EventPaymentActivityCreate] = {}
        batch_id = uuid4()

        for m in messages:
            logger.info("Processing event: %s", m)
            event = aggregated_data.get(m.event_id)
            if not event:
                aggregated_data[m.event_id] = EventPaymentActivityCreate(
                    batch_id=batch_id,
                    event_id=m.event_id,
                    payments_count=1,
                    tickets_count=m.tickets_count,
                    total_amount=m.total_amount,
                )
            else:
                event.payments_count += 1
                event.tickets_count += m.tickets_count
                m.total_amount += m.total_amount

        return list(aggregated_data.values())
