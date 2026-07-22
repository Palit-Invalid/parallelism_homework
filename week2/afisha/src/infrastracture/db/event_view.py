import asyncio


from src.infrastracture.db.manager import DBManager
from src.infrastracture.redis.manager import RedisManager
from src.log import logger


class EventViewCounter:
    LIMIT_VIEWS_IN_MEMORY = 10
    SAVE_VIEWS_AFTER_TIMEOUT = 5
    DUPLICATE_VIEW_TTL = 300

    def __init__(self, db: DBManager, redis: RedisManager) -> None:
        self.db = db
        self.redis = redis
        self._queue = asyncio.Queue()

    async def start(self):
        self._task = asyncio.create_task(self._flush_views())

    async def stop(self):
        self._task.cancel()
        await self._task

    async def add_event_view(self, event_id: int, address: str):
        await self._queue.put((event_id, address))

    async def _flush_views(self):
        views: dict[str, int] = {}
        while True:
            try:
                logger.debug("VIEWS: %s", views)
                event_id, address = await asyncio.wait_for(self._queue.get(), timeout=self.SAVE_VIEWS_AFTER_TIMEOUT)
                is_new_view = await self.redis.client.set(
                    name=f"event:{event_id}:views:address:{address}",
                    value=1,
                    ex=self.DUPLICATE_VIEW_TTL,
                    nx=True,
                )
                if is_new_view:
                    logger.debug("View from address %s for event %d not counted yet", address, event_id)
                    views[event_id] = views.get(event_id, 0) + 1
                else:
                    logger.debug("View from address %s for event %d already counted", address, event_id)
            except asyncio.TimeoutError:
                if views:
                    logger.debug("Add views after timeout %s", views)
                    await self._update_views_in_db(views)
                    views = {}
                else:
                    logger.debug("Now views in queue")

            if sum(views.values()) >= self.LIMIT_VIEWS_IN_MEMORY:
                logger.debug("Update views count after %d views", self.LIMIT_VIEWS_IN_MEMORY)
                await self._update_views_in_db(views)
                views = {}

    async def _update_views_in_db(self, views: dict):
        for event_id, views_count in views.items():
            await self.db.event_views.add_views(event_id=event_id, views_count=views_count)

        await self.db.commit()
