from datetime import datetime

from app.db import DBManager
from app.log import logger
from app.schemas.events import EventCreate, EventSeatRead
from app.services.base import BaseService


class EventsService(BaseService):
    def __init__(self, db: DBManager) -> None:
        self.db = db

    async def prepare_checkout(self) -> None:
        res = await self.db.events.get_one(id=1)
        logger.debug(res)
        logger.debug("prepare")
        await self.db.events.add_one(
            EventCreate(
                organizer_id=1,
                location_id=1,
                title="t",
                description="d",
                category="c",
                starts_at=datetime.now(),
                base_price=1000
            )
        )
        await self.db.commit()

    async def get_seats(self, event_id: int) -> list[EventSeatRead]:
        event = await self.db.events.get_one_with_seats(id=event_id)
        return event.seats
