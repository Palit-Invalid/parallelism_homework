from random import randint

from redis.asyncio import Redis
from redis.commands.core import EncodableT

from src.log import logger


class RedisManager:
    def __init__(self, redis: Redis) -> None:
        self.client = redis

    async def close(self) -> None:
        await self.client.aclose()

    async def set(self, name: str, value: EncodableT, ex: int):
        """Wrapper for redis set with TTL jitter"""
        ex_with_jitter = self._get_ttl_with_jitter(base_ttl=ex)
        logger.debug("Setting cache with jitter TTL. Base TTL - %d, with jitter - %d", ex, ex_with_jitter)
        await self.client.set(
            name=name,
            value=value,
            ex=ex_with_jitter,
        )

    def _get_ttl_with_jitter(self, base_ttl: int, jitter_percent: float = 0.1) -> int:
        jitter_range = int(base_ttl * jitter_percent)
        jitter = randint(-jitter_range, jitter_range)
        return max(1, base_ttl + jitter)
