from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.infrastracture.db.manager import DBManager
from src.infrastracture.db.models import Booking, EventSeat
from src.infrastracture.db.models.bookings import BookingStatus
from src.infrastracture.db.models.events import SeatStatus
from src.log import logger
from src.schemas.events import EventSeatEdit, EventSeatReadWithBooking
from src.services.base import BaseService


class BookingService(BaseService):
    def __init__(self, db: DBManager) -> None:
        self.db = db

    async def delete_overdue_bookings(self) -> None:
        overdue_event_seats = await self._get_overdue()

        logger.debug("OVERDUE EVENT SEATS: %s", overdue_event_seats)

        event_seats_ids = [event_seat.id for event_seat in overdue_event_seats]
        booking_ids = [event_seat.booking.id for event_seat in overdue_event_seats]

        await self.db.event_seats.edit(
            EventSeatEdit(status=SeatStatus.available, booking_id=None),
            EventSeat.id.in_(event_seats_ids),
        )
        await self.db.bookings.delete(
            Booking.id.in_(booking_ids),
        )

        await self.db.commit()

    async def _get_overdue(self) -> list[EventSeatReadWithBooking]:
        query = (
            select(EventSeat)
            .join(EventSeat.booking)
            .filter(
                Booking.status == BookingStatus.pending_payment,
                Booking.reserved_until < func.now(),
            )
            .options(selectinload(EventSeat.booking))
            .with_for_update(nowait=True)
        )

        result = await self.db.session.execute(query)

        models = result.scalars().all()

        return [EventSeatReadWithBooking.model_validate(model, from_attributes=True) for model in models]
