from taskiq import SimpleRetryMiddleware
from taskiq_redis import RedisStreamBroker

from src.config import config

broker_async = RedisStreamBroker(
    url=config.REDIS_URL,
    queue_name="async",
)

broker_sync = RedisStreamBroker(
    url=config.REDIS_URL,
    queue_name="sync",
).with_middlewares(
    SimpleRetryMiddleware(
        types_of_exceptions=(Exception,),
    ),
)
