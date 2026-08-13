from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from src.infrastracture.api_connectors.protection import ProtectionCalculateResponse, ProtectionConnector
from src.infrastracture.db.manager import DBManager
from src.infrastracture.db.models import Booking, EventSeat
from src.infrastracture.db.models.bookings import BookingStatus
from src.infrastracture.db.models.events import SeatStatus
from src.log import logger
from src.schemas.bookings import BookingEditDB
from src.schemas.events import EventSeatEdit
from src.services.base import BaseService


class BookingService(BaseService):
    def __init__(self, db: DBManager, protection_connector: ProtectionConnector) -> None:
        self.db = db
        self.protection_connector = protection_connector

    async def delete_overdue_bookings(self) -> None:
        overdue_event_seats = await self.db.event_seats.get_overdue()

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

    async def add_protection(self, booking_id: int, ticket_amount: int, event_category: str):
        @retry(stop=stop_after_attempt(2), wait=wait_exponential_jitter(1))
        async def calculate_protection() -> ProtectionCalculateResponse:
            return await self.protection_connector.calculate(
                booking_id=booking_id, ticket_amount=ticket_amount, event_category=event_category
            )

        protection_data = await calculate_protection()
        logger.debug("PROTECTION DATA: %s", protection_data)

        booking = await self.db.bookings.get_one_or_none(
            Booking.id == booking_id,
            Booking.status == BookingStatus.pending_payment,
            for_update=True,
        )
        if not booking:
            logger.warning(
                "Unable to add protection because booking with id '%d' isn't found or already paid", booking_id
            )
            return

        await self.db.bookings.edit(
            BookingEditDB(
                protection_price=protection_data.price,
                with_protection=True,
            )
        )

        await self.db.commit()
