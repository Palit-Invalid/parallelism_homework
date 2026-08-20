from uuid import UUID

from pydantic import BaseModel


class EventPaymentActivityCreate(BaseModel):
    batch_id: UUID
    event_id: int
    payments_count: int
    tickets_count: int
    total_amount: int


class EventPaymentActivityGet(EventPaymentActivityCreate):
    id: int


class EventPaymentActivityEdit(BaseModel):
    batch_id: UUID | None = None
    event_id: int | None = None
    payments_count: int | None = None
    tickets_count: int | None = None
    total_amount: int | None = None


class WSPaymentActivityEvents(BaseModel):
    type: str = "payment_activity"
    items: list[EventPaymentActivityCreate]
