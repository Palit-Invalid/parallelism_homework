from src.infrastracture.db.models import EventSeat
from src.infrastracture.db.repos.base import BaseRepository
from src.schemas.events import (
    EventSeatCreate,
    EventSeatEdit,
    EventSeatRead,
)


class EventSeatsRepository(BaseRepository[EventSeatRead, EventSeatCreate, EventSeatEdit]):
    model = EventSeat
    schema = EventSeatRead
