from fastapi import APIRouter

from src.api.dependencies import CurrentUserId
from src.schemas.base import (
    PaymentCompleted,
    PaymentCreate,
)

router = APIRouter(prefix="/bookings")


@router.post("/{booking_id}/pay")
async def pay_booking(
    booking_id: int,
    payload: PaymentCreate,
    user_id: CurrentUserId,
) -> PaymentCompleted:  # ty: ignore
    """Принимает способ оплаты и флаг with_protection."""
    ...
