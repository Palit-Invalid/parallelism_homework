from datetime import datetime

from pydantic import BaseModel, Field

from src.infrastracture.db.models.bookings import BookingStatus


class BookingCreate(BaseModel):
    seat_ids: list[int] = Field(min_length=1)


class BookingCreateDB(BaseModel):
    event_id: int
    user_id: int
    amount: int
    payment_commission: int
    protection_price: int | None = None
    with_protection: bool
    status: BookingStatus
    reserved_until: datetime


class BookingEditDB(BaseModel):
    event_id: int | None = None
    user_id: int | None = None
    amount: int | None = None
    payment_commission: int | None = None
    protection_price: int | None = None
    with_protection: bool | None = None
    status: BookingStatus | None = None
    reserved_until: datetime | None = None


class BookingReadDB(BookingCreateDB):
    id: int
