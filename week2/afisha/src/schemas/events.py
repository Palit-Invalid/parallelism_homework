from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.infrastracture.db.models.events import SeatStatus
from src.schemas.bookings import BookingReadDB


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


class EventSeatEdit(BaseModel):
    event_id: int | None = None
    seat_id: int | None = None
    sector: str | None = None
    row: str | None = None
    number: int | None = None
    x: int | None = None
    y: int | None = None
    price: int | None = None
    status: SeatStatus | None = None
    reserved_until: datetime | None = None
    booking_id: int | None = None


class EventSeatRead(BaseModel):
    id: int
    event_id: int
    seat_id: int
    price: int
    status: SeatStatus
    reserved_until: datetime | None
    booking_id: int | None


class EventSeatReadWithBooking(EventSeatRead):
    booking: BookingReadDB


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


class EventWithSeats(BaseModel):
    id: int
    organizer_id: int
    location_id: int
    title: str
    description: str
    category: str
    starts_at: datetime
    base_price: int
    seats: list[EventSeatRead]


class EventSeatWithEvent(EventSeatRead):
    event: EventRead
