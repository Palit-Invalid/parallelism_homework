from pydantic import BaseModel

class EventViewCreate(BaseModel):
    views_count: int

class EventViewRead(EventViewCreate):
    event_id: int

class EventViewEdit(EventViewCreate): ...
