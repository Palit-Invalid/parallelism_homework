from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.infrastracture.db.models import Booking, Event, EventSeat
from src.infrastracture.db.models.bookings import BookingStatus
from src.infrastracture.db.models.events import SeatStatus
from src.infrastracture.db.repos.base import BaseRepository
from src.schemas.base import OccupancyDashboard, SalesDashboard
from src.schemas.events import (
    EventSeatCreate,
    EventSeatEdit,
    EventSeatRead,
    EventSeatReadWithBooking,
)


class EventSeatsRepository(BaseRepository[EventSeatRead, EventSeatCreate, EventSeatEdit]):
    model = EventSeat
    schema = EventSeatRead

    async def get_sales_stats_for_dashboard(self, event_id: int, organizer_id: int) -> SalesDashboard:
        query = (
            select(
                func.count(EventSeat.id),
                func.count(func.distinct(EventSeat.booking_id)),
                func.coalesce(func.sum(EventSeat.price), 0),
                func.coalesce(func.avg(EventSeat.price), 0),
            )
            .join(Event, EventSeat.event)
            .join(Booking, EventSeat.booking)
            .filter(
                Event.organizer_id == organizer_id,
                Event.id == event_id,
                EventSeat.status == SeatStatus.sold,
                Booking.status == BookingStatus.paid,
            )
        )

        result = (await self.session.execute(query)).one()
        return SalesDashboard(
            sold_tickets=result[0],
            paid_orders=result[1],
            revenue=result[2],
            average_order=int(result[3]),
        )

    async def get_occupancy_stats_for_dashboard(self, event_id: int, organizer_id: int) -> OccupancyDashboard:
        query = (
            select(
                func.count(EventSeat.id),
                func.count(EventSeat.id).filter(EventSeat.status == SeatStatus.available),
                func.count(EventSeat.id).filter(EventSeat.status == SeatStatus.reserved),
                func.count(EventSeat.id).filter(EventSeat.status == SeatStatus.sold),
            )
            .join(Event, EventSeat.event)
            .filter(
                Event.organizer_id == organizer_id,
                Event.id == event_id,
            )
        )

        result = (await self.session.execute(query)).one()
        return OccupancyDashboard(
            total=result[0],
            available=result[1],
            reserved=result[2],
            sold=result[3],
            occupancy_percent=(result[2] + result[3]) / result[0] * 100,
        )

    async def get_overdue(self) -> list[EventSeatReadWithBooking]:
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

        result = await self.session.execute(query)

        models = result.scalars().all()

        return [EventSeatReadWithBooking.model_validate(model, from_attributes=True) for model in models]
