from sqlalchemy.dialects.postgresql import insert
from src.infrastracture.db.models import EventView
from src.infrastracture.db.repos.base import BaseRepository
from src.schemas.event_views import EventViewCreate, EventViewEdit, EventViewRead


class EventViewsRepository(BaseRepository[EventViewRead, EventViewCreate, EventViewEdit]):
    model = EventView
    schema = EventViewRead

    async def add_views(self, event_id: int, views_count: int):
        stmt = (
            insert(self.model)
            .values(event_id=event_id, views_count=views_count)
            .on_conflict_do_update(
                index_elements=["event_id"],
                set_={
                    "views_count": EventView.views_count + views_count
                }
            )
        )
        await self.session.execute(stmt)
