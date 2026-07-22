from redis.asyncio import Redis


class RedisManager:
    def __init__(self, redis: Redis) -> None:
        self.client = redis

    async def close(self) -> None:
        await self.client.aclose()
