from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.infrastracture.db.models.events import SeatStatus


class EventSeatCreate(BaseModel):
    event_id: int
    seat_id: int
    sector: str
    row: str
    number: int
    x: int
    y: int
    price: int
    status: SeatStatus
    reserved_until: datetime | None
    booking_id: int | None


class EventSeatRead(BaseModel):
    id: int
    event_id: int
    seat_id: int
    price: int
    status: SeatStatus
    reserved_until: datetime | None
    booking_id: int | None


class EventSeatEdit(BaseModel):
    price: int | None = None
    status: SeatStatus | None = None
    reserved_until: datetime | None = None


class EventCreate(BaseModel):
    location_id: int
    organizer_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    category: str = Field(min_length=1, max_length=100)
    starts_at: datetime
    base_price: int = Field(gt=0)


class EventRead(EventCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
