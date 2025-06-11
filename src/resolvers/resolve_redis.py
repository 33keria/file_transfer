import redis.asyncio as redis
from redis.asyncio import ConnectionPool
import structlog

from utils.route_utils import get_trace_id

logger = structlog.get_logger("resolve_redis")


class RedisOperator:
    def __init__(self, pool: ConnectionPool):
        self.pool = pool

    async def add_one(self, key: str):
        """
        对应key的值在原值基础上加1

        Args:
            key (str)

        Returns:
            res (int): key加值后的值
        """
        trace_id = await get_trace_id()
        logger.info(
            "对应key的值在原值基础上加1 input",
            key=key,
            trace_id=trace_id
        )
        client = redis.Redis.from_pool(self.pool)
        async with client.pipeline(transaction=True) as pipe:
            res_incr, res_get = await (pipe.incr(key).get(key).execute())
        logger.info(
            "对应key的值在原值基础上加1 res",
            trace_id=trace_id,
            res_incr=res_incr,
            res_get=res_get
        )
        return res_get

            