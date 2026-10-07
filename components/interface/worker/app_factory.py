import logging

from faststream import FastStream

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
from components.infrastructure.workers.rabbit.broker_factory import (
    build_generations_queue,
    create_rabbit_broker,
)
from components.infrastructure.workers.rabbit.messages.generation_task_message import (
    GenerationTaskMessage,
)

logger = logging.getLogger(__name__)


def create_worker_app(settings: Settings | None = None) -> FastStream:
    resolved = settings or get_settings()
    setup_logging(resolved.log_level)

    broker = create_rabbit_broker(resolved)
    app = FastStream(broker)
    engine = create_engine(resolved)
    session_factory = create_session_factory(engine)
    provider = FakeGenerationProvider()

    @broker.subscriber(build_generations_queue(resolved))
    async def handle_generation_task(message: GenerationTaskMessage) -> None:
        use_case = ProcessGeneration(
            uow=MySQLUnitOfWork(session_factory),
            provider=provider,
        )
        try:
            await use_case.execute(message.generation_id)
        except Exception:
            logger.exception(
                "Generation processing failed generation_id=%s",
                message.generation_id,
            )

    @app.after_shutdown
    async def dispose_engine() -> None:
        await engine.dispose()

    return app
