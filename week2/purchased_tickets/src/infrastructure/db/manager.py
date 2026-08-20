from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from types import TracebackType

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config import config
from src.infrastructure.db.repos import EventPaymentActivityRepository

engine = create_async_engine(
    config.DB.url,
    pool_pre_ping=True,
    echo=config.DB.ECHO,
    pool_size=config.DB.POOL_SIZE,
    max_overflow=config.DB.MAX_OVERFLOW,
)
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

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator["DBManager"]:
        db = DBManager(self.session_maker)
        async with db as db:
            try:
                yield db
                await db.commit()
            except:
                await db.rollback()
                raise

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    @property
    def event_payment_activity(self) -> EventPaymentActivityRepository:
        return EventPaymentActivityRepository(self.session)
