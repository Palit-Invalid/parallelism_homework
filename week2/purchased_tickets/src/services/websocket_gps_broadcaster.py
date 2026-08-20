from src.infrastructure.websocket.manager import WebsocketManager
from src.schemas.event_payment_activity import (
    EventPaymentActivityCreate,
    WSPaymentActivityEvents,
)


class WebsocketGPSBroadcaster:
    def __init__(self, ws_manager: WebsocketManager):
        self.ws_manager = ws_manager

    async def broadcast_purchased_tickets_events(
        self, events: list[EventPaymentActivityCreate]
    ):
        await self.ws_manager.broadcast(
            WSPaymentActivityEvents(type="purchased_tickets", items=events)
        )
