from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastracture.db.models.base import Base

if TYPE_CHECKING:
    from src.infrastracture.db.models.events import EventSeat


class Seat(Base):
    """Место на площадке."""

    __tablename__ = "seats"
    __table_args__ = (UniqueConstraint("location_id", "sector", "row", "number", name="uq_seat_position"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), index=True)
    sector: Mapped[str] = mapped_column(index=True)
    row: Mapped[int]
    number: Mapped[int]
    x: Mapped[int]
    y: Mapped[int]

    event_seats: Mapped[list["EventSeat"]] = relationship(back_populates="seat")
