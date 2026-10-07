from redis.asyncio import Redis

from components.domain.protocols.billing.balance_cache import IBalanceCache


class RedisBalanceCache(IBalanceCache):
    _KEY_PREFIX = "balance:"

    def __init__(self, redis: Redis, ttl_seconds: int) -> None:
        self._redis = redis
        self._ttl_seconds = ttl_seconds

    async def get(self, user_id: str) -> int | None:
        value = await self._redis.get(self._key(user_id))
        return None if value is None else int(value)

    async def set(self, user_id: str, balance: int) -> None:
        await self._redis.set(self._key(user_id), balance, ex=self._ttl_seconds)

    async def invalidate(self, user_id: str) -> None:
        await self._redis.delete(self._key(user_id))

    def _key(self, user_id: str) -> str:
        return f"{self._KEY_PREFIX}{user_id}"
