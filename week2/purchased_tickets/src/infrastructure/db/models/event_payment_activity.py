from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.models.base import Base


class EventPaymentActivityModel(Base):
    __tablename__ = "event_payment_activity"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[UUID]
    event_id: Mapped[int] = mapped_column(index=True)
    payments_count: Mapped[int]
    tickets_count: Mapped[int]
    total_amount: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
