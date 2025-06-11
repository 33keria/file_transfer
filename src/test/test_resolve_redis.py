from resolvers.resolve_redis import RedisOperator
from configs import settings


class TestRedisOperator:
    def test_case1(self):
        operator = RedisOperator(settings.REDIS_CONNECT_POOL)
        