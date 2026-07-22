import asyncio

from sqlalchemy.exc import NoResultFound

from src.domain.exceptions import ObjectNotFound
from src.infrastracture.db.manager import DBManager
from src.infrastracture.db.models import Event
from src.log import logger
from src.schemas.base import EventDashboard, OccupancyDashboard, SalesDashboard
from src.services.base import BaseService


class OrganizerService(BaseService):
    def __init__(self, db: DBManager) -> None:
        self.db = db

    async def _get_sales_stats_for_dashboard(self, event_id: int, organizer_id: int) -> SalesDashboard:
        async with self.db.transaction() as db:
            return await db.event_seats.get_sales_stats_for_dashboard(event_id=event_id, organizer_id=organizer_id)

    async def _get_occupancy_stats_for_dashboard(self, event_id: int, organizer_id: int) -> OccupancyDashboard:
        async with self.db.transaction() as db:
            return await db.event_seats.get_occupancy_stats_for_dashboard(event_id=event_id, organizer_id=organizer_id)

    async def get_dashboard(self, event_id: int, organizer_id: int) -> EventDashboard:
        try:
            async with asyncio.TaskGroup() as tg:
                sales_task = tg.create_task(
                    self._get_sales_stats_for_dashboard(event_id=event_id, organizer_id=organizer_id)
                )
                occupancy_task = tg.create_task(
                    self._get_occupancy_stats_for_dashboard(event_id=event_id, organizer_id=organizer_id)
                )
                event_task = tg.create_task(
                    self.db.events.get_one(Event.id == event_id, Event.organizer_id == organizer_id)
                )
            sales = sales_task.result()
            occupancy = occupancy_task.result()
            event = event_task.result()
        except* Exception as exc_group:
            for exc in exc_group.exceptions:
                if isinstance(exc, NoResultFound):
                    raise ObjectNotFound
            raise

        logger.debug("Getting dashboard data\nSales: %s\nOccupancy: %s\nEvent: %s", sales, occupancy, event)

        return EventDashboard(
            event_title=event.title,
            starts_at=event.starts_at,
            sales=sales,
            occupancy=occupancy,
        )
