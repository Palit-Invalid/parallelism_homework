from fastapi import APIRouter

from app.api.routes.bookings import router as bookings_router
from app.api.routes.events import router as events_router
from app.api.routes.locations import router as locations_router
from app.api.routes.organizer import router as organizer_router

__all__ = ("main_router")


main_router = APIRouter()
main_router.include_router(bookings_router)
main_router.include_router(events_router)
main_router.include_router(locations_router)
main_router.include_router(organizer_router)
