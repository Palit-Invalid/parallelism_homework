from types import TracebackType

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config import config
from src.infrastracture.db.repos import EventSeatsRepository, EventsRepository

engine = create_async_engine(config.db.url, pool_pre_ping=True)
session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


class DBManager:
    def __init__(self, session_maker: async_sessionmaker) -> None:
        self.session_maker = session_maker

    async def __aenter__(self):
        self.session = self.session_maker()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        ecx_tb: TracebackType | None = None,
    ):
        await self.session.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    @property
    def events(self) -> EventsRepository:
        return EventsRepository(self.session)

    @property
    def event_seats(self) -> EventSeatsRepository:
        return EventSeatsRepository(self.session)
