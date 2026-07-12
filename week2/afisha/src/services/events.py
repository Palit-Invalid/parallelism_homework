from src.infrastracture.db.manager import DBManager
from src.infrastracture.db.models import EventSeat
from src.log import logger
from src.schemas.events import EventSeatEdit, SeatStatus
from src.services.base import BaseService
from src.domain.exceptions import ObjectLockedError
import asyncio

class EventsService(BaseService):
    def __init__(self, db: DBManager) -> None:
        self.db = db

    async def prepare_checkout(
        self, user_id: int, event_id: int, seat_ids: list[int]
    ) -> None:

        event_seats = await self.db.event_seats.get_filtered(
            EventSeat.event_id == event_id,
            EventSeat.seat_id.in_(seat_ids),
            lock=True,
        )
        # await asyncio.sleep(30)
        logger.debug("Received %d event seats for checkout", len(event_seats))

        await self.db.event_seats.edit(
            EventSeatEdit(status=SeatStatus.reserved),
            EventSeat.seat_id.in_(seat_ids),
        )

        logger.debug("Event seats were reserved: %s", event_seats)
        await self.db.commit()
