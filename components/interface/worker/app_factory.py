from faststream import FastStream
from redis.asyncio import Redis

from components.application.use_cases.generation.process_generation import (
    ProcessGeneration,
)
from components.core.config.settings import Settings, get_settings
from components.core.logging.setup import setup_logging
from components.infrastructure.clients.generation.fake_generation_provider import (
    FakeGenerationProvider,
)
from components.infrastructure.stores.mysql.session_factory import (
    create_engine,
    create_session_factory,
)
from components.infrastructure.stores.mysql.unit_of_work import MySQLUnitOfWork
from components.infrastructure.stores.redis.balance_cache import RedisBalanceCache
from components.infrastructure.workers.rabbit.broker_factory import (
    build_generations_queue,
    create_rabbit_broker,
)
from components.infrastructure.workers.rabbit.messages.generation_task_message import (
    GenerationTaskMessage,
)


def create_worker_app(settings: Settings | None = None) -> FastStream:
    resolved = settings or get_settings()
    setup_logging(resolved.log_level)

    broker = create_rabbit_broker(resolved)
    app = FastStream(broker)
    engine = create_engine(resolved)
    session_factory = create_session_factory(engine)
    redis = Redis.from_url(resolved.redis_url, decode_responses=True)
    balance_cache = RedisBalanceCache(
        redis,
        ttl_seconds=resolved.balance_cache_ttl_seconds,
    )
    provider = FakeGenerationProvider()

    @broker.subscriber(build_generations_queue(resolved))
    async def handle_generation_task(message: GenerationTaskMessage) -> None:
        use_case = ProcessGeneration(
            uow=MySQLUnitOfWork(session_factory),
            provider=provider,
            balance_cache=balance_cache,
            max_attempts=resolved.provider_max_attempts,
            timeout_seconds=resolved.provider_timeout_seconds,
            retry_base_delay_seconds=resolved.provider_retry_base_delay_seconds,
        )
        await use_case.execute(message.generation_id)

    @app.after_shutdown
    async def dispose_resources() -> None:
        await redis.aclose()
        await engine.dispose()

    return app
