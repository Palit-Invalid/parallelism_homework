from typing import Annotated

from fastapi import Depends, Header

from src.infrastracture.db.manager import DBManager, session_maker
from src.services.events import EventsService


def get_current_user_id(x_user_id: Annotated[int, Header()]) -> int:
    return x_user_id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]


async def get_db():
    async with DBManager(session_maker=session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


def get_events_service(db: DBDep) -> EventsService:
    return EventsService(db)

EventsServiceDep = Annotated[EventsService, Depends(get_events_service)]
