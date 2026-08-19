from redis.asyncio import Redis

from src.config import config
from src.infrastracture.redis.manager import RedisManager

redis_manager = RedisManager(
    Redis.from_url(
        config.REDIS.url,
        decode_responses=True,
    )
)
