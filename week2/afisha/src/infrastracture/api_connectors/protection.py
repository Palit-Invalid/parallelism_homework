from pydantic import BaseModel
from datetime import datetime
from src.infrastracture.api_connectors.base import BaseHTTPConnector
from src.log import logger


class ProtectionCalculateResponse(BaseModel):
    available: bool
    price: int
    covered_amount: int
    description: str


class ProtectionConnector(BaseHTTPConnector):
    async def calculate(self, booking_id: int, ticket_amount: int, event_category: str) -> ProtectionCalculateResponse:
        data = {
            "booking_id": booking_id,
            "ticket_amount": ticket_amount,
            "event_category": event_category,
            "event_starts_at": datetime.now().isoformat(timespec="milliseconds"),
        }
        result = (await self._request(method="post", url="/protection/calculate", timeout=3, json=data)).json()
        return ProtectionCalculateResponse(
            available=result["available"],
            price=result["price"],
            covered_amount=result["covered_amount"],
            description=result["description"],
        )
