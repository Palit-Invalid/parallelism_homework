from taskiq import SimpleRetryMiddleware, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import RedisStreamBroker

from src.config import config

broker_async = RedisStreamBroker(
    url=config.REDIS.url,
    queue_name="async",
)

broker_sync = RedisStreamBroker(
    url=config.REDIS.url,
    queue_name="sync",
).with_middlewares(
    SimpleRetryMiddleware(
        types_of_exceptions=(Exception,),
    ),
)

scheduler = TaskiqScheduler(
    broker=broker_async,
    sources=[LabelScheduleSource(broker=broker_async)],
)
