from httpx import AsyncClient

class BaseHTTPConnector:
    def __init__(self, base_url: str) -> None:
        self._client = AsyncClient(base_url=base_url)
