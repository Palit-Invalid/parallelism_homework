from app.models.events import Event
from app.repos.base import BaseRepository
from app.schemas.events import EventCreate, EventRead


class EventsRepository(BaseRepository[EventRead, EventCreate]):
    model = Event
    schema = EventRead
