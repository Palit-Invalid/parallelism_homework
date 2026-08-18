from sqlalchemy.dialects.postgresql import insert
from src.infrastracture.db.models import EventView
from src.infrastracture.db.repos.base import BaseRepository
from src.schemas.event_views import EventViewCreate, EventViewEdit, EventViewRead


class EventViewsRepository(BaseRepository[EventViewRead, EventViewCreate, EventViewEdit]):
    model = EventView
    schema = EventViewRead

    async def add_views_bulk(self, views_data: list[EventViewRead]):
        values = [data.model_dump() for data in views_data]
        stmt = insert(self.model).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["event_id"], set_={"views_count": EventView.views_count + stmt.excluded.views_count}
        )
        await self.session.execute(stmt)
