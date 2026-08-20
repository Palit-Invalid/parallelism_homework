from src.infrastructure.db.models import EventPaymentActivityModel
from src.infrastructure.db.repos.base import BaseRepository
from src.schemas.event_payment_activity import (
    EventPaymentActivityCreate,
    EventPaymentActivityEdit,
    EventPaymentActivityGet,
)


class EventPaymentActivityRepository(
    BaseRepository[EventPaymentActivityGet, EventPaymentActivityCreate, EventPaymentActivityEdit]
):
    model = EventPaymentActivityModel
    schema = EventPaymentActivityGet
