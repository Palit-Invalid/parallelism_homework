from fastapi import APIRouter

from src.api.dependencies import CurrentUserId, EventsServiceDep, UserAddressDep
from src.schemas.bookings import BookingCreate
from src.schemas.events import EventRead, EventSeatRead
from src.schemas.base import CheckoutResponse

router = APIRouter(prefix="/events")


@router.get("")
async def list_events() -> list[EventRead]:
    """Возвращает список мероприятий для клиента."""
    ...


@router.get("/{event_id}")
async def get_event(event_service: EventsServiceDep, event_id: int, user_address: UserAddressDep) -> EventRead:
    """Возвращает описание мероприятия."""
    return await event_service.get_event(event_id=event_id, user_address=user_address)


@router.get("/{event_id}/seats")
async def list_event_seats(events_service: EventsServiceDep, event_id: int) -> list[EventSeatRead]:
    """Возвращает места на мероприятии с ценами и статусами."""
    return await events_service.get_seats(event_id=event_id)


@router.post("/{event_id}/checkout")
async def prepare_checkout(
    events_service: EventsServiceDep,
    event_id: int,
    payload: BookingCreate,
    user_id: CurrentUserId,
) -> CheckoutResponse:
    """Временно бронирует места за клиентом, возвращает итоговую стоимость
    и возможность страховки."""
    return await events_service.prepare_checkout(user_id=user_id, event_id=event_id, seat_ids=payload.seat_ids)
