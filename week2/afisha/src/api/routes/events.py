from fastapi import APIRouter

from src.api.dependencies import CurrentUserId, EventsServiceDep
from src.schemas.bookings import BookingCreate
from src.schemas.events import EventRead, EventSeatRead

router = APIRouter(prefix="/events")


@router.get("")
async def list_events() -> list[EventRead]:
    """Возвращает список мероприятий для клиента."""
    ...


@router.get("/{event_id}")
async def get_event(event_id: int) -> EventRead:
    """Возвращает описание мероприятия."""
    ...


@router.get("/{event_id}/seats")
async def list_event_seats(
    events_service: EventsServiceDep, event_id: int
) -> list[EventSeatRead]:
    """Возвращает места на мероприятии с ценами и статусами."""
    return await events_service.get_seats(event_id=event_id)


@router.post("/{event_id}/checkout")
async def prepare_checkout(
    events_service: EventsServiceDep,
    event_id: int,
    payload: BookingCreate,
    user_id: CurrentUserId,
) -> None:
    """Временно бронирует места за клиентом, возвращает итоговую стоимость
    и возможность страховки."""
    await events_service.prepare_checkout(user_id=user_id, event_id=event_id, seat_ids=payload.seat_ids)
    # TODO: создать бронь для выбранных мест через SELECT FOR UPDATE, и посчитать базовую стоимость.
    # TODO: конкурентно запросить Payment API и Protection API для расчета checkout.
