import asyncio
from datetime import datetime, timezone

from src.domain.exceptions import SeatsNotAvailable
from src.infrastracture.api_connectors.payment import PaymentConnector
from src.infrastracture.api_connectors.protection import ProtectionConnector
from src.infrastracture.db.manager import DBManager
from src.infrastracture.db.models import Booking, Event, EventSeat, Seat
from src.log import logger
from src.schemas.base import (
    CheckoutBooking,
    CheckoutResponse,
    PaymentQuote,
    ProtectionQuote,
)
from src.schemas.bookings import (
    BookingCreateDB,
    BookingEditDB,
    BookingReadDB,
    BookingStatus,
)
from src.schemas.events import EventRead, EventSeatEdit, EventSeatRead, SeatStatus
from src.schemas.seats import SeatRead
from src.services.base import BaseService


class EventsService(BaseService):
    def __init__(
        self,
        db: DBManager,
        payment_connector: PaymentConnector,
        protection_connector: ProtectionConnector,
    ) -> None:
        self.db = db
        self.payment_connector = payment_connector
        self.protection_connector = protection_connector

    async def _get_event_for_checkout(self, event_id: int) -> EventRead:
        async with self.db.transaction() as db:
            event = await db.events.get_one(Event.id == event_id)
        logger.debug("Event for checkout: %s", event)
        return event

    async def _get_event_seats_for_checkout(self, event_id: int, seat_ids: list[int]) -> list[EventSeatRead]:
        async with self.db.transaction() as db:
            event_seats = await db.event_seats.get_filtered(
                EventSeat.event_id == event_id,
                EventSeat.seat_id.in_(seat_ids),
                EventSeat.status == SeatStatus.available,
                for_update=True,
            )
        logger.debug("Event seats for checkout: %s", event_seats)
        return event_seats

    async def _get_seats_for_checkout(self, seat_ids: list[int]) -> list[SeatRead]:
        async with self.db.transaction() as db:
            seats = await db.seats.get_filtered(Seat.id.in_(seat_ids))
        return seats

    async def _reserve_event_seats_for_checkout(self, seat_ids: list[int]) -> None:
        async with self.db.transaction() as db:
            await db.event_seats.edit(
                EventSeatEdit(status=SeatStatus.reserved),
                EventSeat.seat_id.in_(seat_ids),
            )
        logger.debug("Reserve event_seats with ids: %s", seat_ids)

    async def _create_dummy_booking_for_checkout(self, event_id: int, user_id: int, amount: int) -> BookingReadDB:
        async with self.db.transaction() as db:
            booking_data = BookingCreateDB(
                event_id=event_id,
                user_id=user_id,
                amount=amount,
                payment_commission=0,
                with_protection=False,
                status=BookingStatus.pending_payment,
                reserved_until=datetime.now(tz=timezone.utc),
            )
            return await db.bookings.add_one(data=booking_data)

    async def _reserve_event_seats(self, booking_id: int, reserved_until: datetime, seat_ids: list[int]) -> None:
        async with self.db.transaction() as db:
            data = EventSeatEdit(
                status=SeatStatus.reserved,
                reserved_until=reserved_until,
                booking_id=booking_id,
            )
            await db.event_seats.edit(data, EventSeat.seat_id.in_(seat_ids))

    async def _finalize_booking(
        self,
        booking_id: int,
        amount: int,
        payment_commission: int,
        protection_price: int | None,
        with_protection: bool,
        reserved_until: datetime,
    ):
        async with self.db.transaction() as db:
            data = BookingEditDB(
                amount=amount,
                payment_commission=payment_commission,
                protection_price=protection_price,
                with_protection=with_protection,
                reserved_until=reserved_until,
            )
            await db.bookings.edit(data, Booking.id == booking_id)

    async def prepare_checkout(self, user_id: int, event_id: int, seat_ids: list[int]) -> CheckoutResponse:
        try:
            async with asyncio.TaskGroup() as tg:
                # Split queries because we have to block event_seats but not events and seats
                event_task = tg.create_task(self._get_event_for_checkout(event_id=event_id))
                event_seat_task = tg.create_task(
                    self._get_event_seats_for_checkout(event_id=event_id, seat_ids=seat_ids)
                )
                seats_task = tg.create_task(self._get_seats_for_checkout(seat_ids=seat_ids))
            event = event_task.result()
            event_seats = event_seat_task.result()
            seats = seats_task.result()
        except* Exception as exc_group:
            for exc in exc_group.exceptions:
                print(f"{exc=}")
            raise

        if len(seat_ids) != len(event_seats):
            raise SeatsNotAvailable

        try:
            async with asyncio.TaskGroup() as tg:
                reserve_event_seat_task = tg.create_task(self._reserve_event_seats_for_checkout(seat_ids=seat_ids))
                # Create dummy booking to get its ID
                booking_task = tg.create_task(
                    self._create_dummy_booking_for_checkout(event_id=event_id, user_id=user_id, amount=0)
                )

            _ = reserve_event_seat_task.result()
            booking = booking_task.result()
        except* Exception as exc_group:
            for exc in exc_group.exceptions:
                print(f"{exc=}")
            raise

        payment_data, protection_data = await asyncio.gather(
            self.payment_connector.calculate(
                booking_id=booking.id,
                amount=event.base_price * len(seat_ids),
                currency="rub",
            ),
            self.protection_connector.calculate(
                booking_id=booking.id,
                ticket_amount=event.base_price,
                event_category=event.category,
            ),
            return_exceptions=True,
        )

        if isinstance(payment_data, BaseException):
            logger.warning("Unable to calculate payment date: %s", payment_data)
            raise

        logger.debug("Payment data: %s", payment_data)

        if isinstance(protection_data, BaseException):
            logger.warning("Unable to calculate protection: %s", protection_data)
            protection_price = 0
            with_protection = False
            protection = None
        else:
            protection_price = protection_data.price
            with_protection = True
            protection = ProtectionQuote(
                available=protection_data.available,
                price=protection_data.price,
                covered_amount=protection_data.covered_amount,
                description=protection_data.description,
            )
            logger.debug("Protection data: %s", protection_data)

        async with asyncio.TaskGroup() as tg:
            reserve_event_seats_task = tg.create_task(
                self._reserve_event_seats(
                    booking_id=booking.id,
                    reserved_until=payment_data.expires_at,
                    seat_ids=seat_ids,
                )
            )
            finalize_booking_task = tg.create_task(
                self._finalize_booking(
                    booking_id=booking.id,
                    amount=payment_data.total,
                    payment_commission=payment_data.commission,
                    protection_price=protection_price,
                    with_protection=with_protection,
                    reserved_until=payment_data.expires_at,
                )
            )

        # Wait until finish all processes
        _, _ = reserve_event_seats_task.result(), finalize_booking_task.result()

        await self.db.commit()

        return CheckoutResponse(
            booking=CheckoutBooking(
                id=booking.id,
                event_title=event.title,
                starts_at=event.starts_at,
                seats=[seat.model_dump() for seat in seats],
                base_amount=event.base_price,
                payment_commission=payment_data.commission,
                protection_price=protection_price,
                with_protection=with_protection,
                reserved_until=datetime.now(),  # Fix
            ),
            payment=PaymentQuote(
                commission=payment_data.commission,
                total=payment_data.total,
                payment_methods=payment_data.payment_methods,
                expires_at=payment_data.expires_at,
            ),
            protection=protection,
        )
