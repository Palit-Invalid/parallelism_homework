from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from fastapi.websockets import WebSocket

from src.infrastructure.websocket.manager import (
    WebsocketManager,
    send_messages_to_client,
)

purchased_tickets = APIRouter(tags=["Вебсокет: Местоположения курьеров"])


@purchased_tickets.websocket("/ws/purchased_tickets")
@inject
async def get_courier_events(
    ws: WebSocket,
    ws_manager: FromDishka[WebsocketManager],
):
    async with ws_manager.connect(ws) as client:
        await send_messages_to_client(client)
