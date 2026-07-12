from src.infrastracture.db.models import Event
from src.infrastracture.db.repos.base import BaseRepository
from src.schemas.events import EventCreate, EventRead


class EventsRepository(BaseRepository[EventRead, EventCreate, EventCreate]):
    model = Event
    schema = EventRead
