from httpx import AsyncClient, Response


class BaseHTTPConnector:
    def __init__(self, base_url: str) -> None:
        self._client = AsyncClient(base_url=base_url)

    async def _request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> Response:
        response = await self._client.request(method=method, url=url, **kwargs)
        response.raise_for_status()
        return response
