from dataclasses import dataclass

from faststream.rabbit import RabbitBroker
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from components.core.config.settings import Settings
from components.infrastructure.stores.mysql.unit_of_work import MySQLUnitOfWork
from components.infrastructure.stores.redis.balance_cache import RedisBalanceCache
from components.infrastructure.workers.rabbit.broker_factory import (
    build_generations_queue,
)
from components.infrastructure.workers.rabbit.publishers.generation_task_publisher import (
    RabbitGenerationTaskPublisher,
)


@dataclass(slots=True)
class Container:
    settings: Settings
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    redis: Redis
    broker: RabbitBroker

    def unit_of_work(self) -> MySQLUnitOfWork:
        return MySQLUnitOfWork(self.session_factory)

    def balance_cache(self) -> RedisBalanceCache:
        return RedisBalanceCache(
            self.redis,
            ttl_seconds=self.settings.balance_cache_ttl_seconds,
        )

    def generation_task_publisher(self) -> RabbitGenerationTaskPublisher:
        return RabbitGenerationTaskPublisher(
            self.broker,
            build_generations_queue(self.settings),
        )

    async def close(self) -> None:
        await self.broker.stop()
        await self.redis.aclose()
        await self.engine.dispose()
