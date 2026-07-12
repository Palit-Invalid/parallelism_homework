import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastracture.db.models.base import Base


class SeatStatus(str, enum.Enum):
    available = "available"
    reserved = "reserved"
    sold = "sold"


class Event(Base):
    """Мероприятие с датой, площадкой и базовой ценой. Создается организатором.
    Например: Концерт Аллы Пугачевой, Мастер-класс по Python."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    organizer_id: Mapped[int] = mapped_column(index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), index=True)
    title: Mapped[str]
    description: Mapped[str | None]
    category: Mapped[str]
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    base_price: Mapped[int]


class EventSeat(Base):
    """Место конкретного мероприятия с ценой и статусом."""

    __tablename__ = "event_seats"
    __table_args__ = (UniqueConstraint("event_id", "seat_id", name="uq_event_seat"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id"), index=True)
    price: Mapped[int]
    status: Mapped[SeatStatus] = mapped_column(
        SAEnum(SeatStatus, name="seat_status"),
        default=SeatStatus.available,
        server_default=SeatStatus.available.value,
        index=True,
    )
    reserved_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    booking_id: Mapped[int | None] = mapped_column(
        ForeignKey("bookings.id"),
        index=True,
    )
