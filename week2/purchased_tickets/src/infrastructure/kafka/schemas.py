from datetime import datetime

from pydantic import BaseModel


class TicketPurchasedEvent(BaseModel):
    payment_id: str
    event_id: int
    tickets_count: int
    total_amount: int
    paid_at: datetime
