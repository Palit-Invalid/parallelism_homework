from fastapi import APIRouter

from src.api.dependencies import CurrentUserId, OrganizerServiceDep
from src.infrastracture.tasks.tasks import task_generate_event_dashboard_pdf
from src.schemas.base import EventDashboard
from src.schemas.events import EventCreate, EventRead

router = APIRouter(prefix="/organizer")


@router.get("/events")
async def list_organizer_events(organizer_id: CurrentUserId) -> list[EventRead]:  # ty: ignore
    """Возвращает список созданных событий текущего организатора."""


@router.post("/events")
async def create_event(payload: EventCreate, organizer_id: CurrentUserId) -> EventRead:  # ty: ignore
    """Создает мероприятие от лица текущего организатора."""


@router.get("/events/{event_id}/dashboard")
async def get_event_dashboard(
    event_id: int, organizer_id: CurrentUserId, organizer_service: OrganizerServiceDep
) -> EventDashboard:
    """Возвращает аналитические данные для дашборда по мероприятию."""
    dashboard = await organizer_service.get_dashboard(event_id=event_id, organizer_id=organizer_id)
    await task_generate_event_dashboard_pdf.kiq(dashboard=dashboard)
    return dashboard
