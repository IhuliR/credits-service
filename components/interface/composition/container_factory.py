from redis.asyncio import Redis

from components.core.config.settings import Settings
from components.infrastructure.stores.mysql.session_factory import (
    create_engine,
    create_session_factory,
)
from components.infrastructure.workers.rabbit.broker_factory import (
    build_generations_queue,
    create_rabbit_broker,
)
from components.interface.composition.container import Container


async def create_container(settings: Settings) -> Container:
    engine = create_engine(settings)
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    broker = create_rabbit_broker(settings)
    await broker.connect()
    await broker.declare_queue(build_generations_queue(settings))
    return Container(
        settings=settings,
        engine=engine,
        session_factory=create_session_factory(engine),
        redis=redis,
        broker=broker,
    )
