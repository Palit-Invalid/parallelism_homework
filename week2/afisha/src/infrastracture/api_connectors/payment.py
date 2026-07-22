from datetime import datetime

from httpx import HTTPStatusError
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

from src.infrastracture.api_connectors.base import BaseHTTPConnector


def is_exception_too_many_requests(exception: BaseException) -> bool:
    if not isinstance(exception, HTTPStatusError):
        return False

    if exception.response.status_code == 429:
        return True

    return False


class PaymentCalculateResponse(BaseModel):
    commission: int
    total: int
    payment_methods: list[str]
    expires_at: datetime


class PaymentConnector(BaseHTTPConnector):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(1),
        retry=retry_if_exception(is_exception_too_many_requests),
    )
    async def calculate(self, booking_id: int, amount: int, currency: str) -> PaymentCalculateResponse:
        data = {
            "booking_id": booking_id,
            "amount": amount,
            "currency": currency,
        }
        result = (await self._request(method="post", url="/payment/calculate", json=data)).json()
        return PaymentCalculateResponse(
            commission=result["commission"],
            total=result["total"],
            payment_methods=result["payment_methods"],
            expires_at=result["expires_at"],
        )
