import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastracture.db.models.base import Base

if TYPE_CHECKING:
    from src.infrastracture.db.models.events import EventSeat


class BookingStatus(str, enum.Enum):
    pending_payment = "pending_payment"
    paid = "paid"
    cancelled = "cancelled"
    expired = "expired"


class Booking(Base):
    """Бронь пользователя на выбранные места."""

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    user_id: Mapped[int] = mapped_column(index=True)
    amount: Mapped[int]  # суммарная стоимость всех выбранных мест
    payment_commission: Mapped[int]
    protection_price: Mapped[int | None]
    with_protection: Mapped[bool]
    status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus, name="booking_status"),
        default=BookingStatus.pending_payment,
        server_default=BookingStatus.pending_payment.value,
        index=True,
    )
    reserved_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    event_seats: Mapped[list["EventSeat"]] = relationship(back_populates="booking")
