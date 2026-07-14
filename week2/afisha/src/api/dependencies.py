from typing import Annotated

from fastapi import Depends, Header

from src.config import config
from src.infrastracture.api_connectors.payment import PaymentConnector
from src.infrastracture.api_connectors.protection import ProtectionConnector
from src.infrastracture.db.manager import DBManager, session_maker
from src.services.events import EventsService
from src.services.organizers import OrganizerService


def get_current_user_id(x_user_id: Annotated[int, Header()]) -> int:
    return x_user_id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]


async def get_db():
    async with DBManager(session_maker=session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


def get_payment_connector() -> PaymentConnector:
    return PaymentConnector(base_url=config.PAYMENT_API_URL)


PaymentConnectorDep = Annotated[PaymentConnector, Depends(get_payment_connector)]


def get_protection_connector() -> ProtectionConnector:
    return ProtectionConnector(base_url=config.PROTECTION_API_URL)


ProtectionConnectorDep = Annotated[ProtectionConnector, Depends(get_protection_connector)]


def get_events_service(
    db: DBDep,
    payment_connector: PaymentConnectorDep,
    protection_connector: ProtectionConnectorDep,
) -> EventsService:
    return EventsService(
        db,
        payment_connector=payment_connector,
        protection_connector=protection_connector,
    )


EventsServiceDep = Annotated[EventsService, Depends(get_events_service)]


def get_organizer_service(db: DBDep) -> OrganizerService:
    return OrganizerService(db)


OrganizerServiceDep = Annotated[OrganizerService, Depends(get_organizer_service)]
