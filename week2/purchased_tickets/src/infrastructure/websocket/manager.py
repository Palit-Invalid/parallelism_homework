import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from uuid import uuid4

from fastapi import WebSocket
from pydantic import BaseModel

from src.log import logger


@dataclass(frozen=True)
class WebsocketClient:
    ws: WebSocket
    queue: asyncio.Queue[BaseModel]


class WebsocketManager:
    def __init__(self):
        self._clients: dict[str, WebsocketClient] = {}

    @asynccontextmanager
    async def connect(self, ws: WebSocket):
        await ws.accept()

        client_id = uuid4().hex
        client = WebsocketClient(
            ws=ws,
            queue=asyncio.Queue(),
        )
        self._clients[client_id] = client

        try:
            yield client
        finally:
            self._clients.pop(client_id)

    async def broadcast(self, message: BaseModel):
        for client in self._clients.values():
            await client.queue.put(message)


async def send_messages_to_client(client: WebsocketClient):
    while True:
        message = await client.queue.get()

        try:
            await asyncio.wait_for(
                client.ws.send_json(message.model_dump_json()),
                timeout=2,
            )
        except TimeoutError as ex:
            logger.error("WebSocket send timeout after 2s: %s", ex)
