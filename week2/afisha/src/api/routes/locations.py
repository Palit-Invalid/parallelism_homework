from fastapi import APIRouter

from src.schemas.locations import LocationDetail, LocationRead
from src.schemas.seats import SeatRead

router = APIRouter(prefix="/locations")


@router.get("")
async def list_locations() -> list[LocationRead]:
    """Возвращает список площадок."""
    ...


@router.get("/{location_id}")
async def get_location(location_id: int) -> LocationDetail:
    """Возвращает площадку со схемой мест."""
    ...


@router.get("/{location_id}/seats")
async def list_location_seats(location_id: int) -> list[SeatRead]:
    """Возвращает все места площадки."""
    ...
