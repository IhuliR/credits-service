from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from components.core.config.settings import Settings, get_settings
from components.core.logging.setup import setup_logging
from components.interface.api.error_handlers import register_error_handlers
from components.interface.api.routers import generations, users, webhooks
from components.interface.composition.container_factory import create_container


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()
    setup_logging(resolved.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        container = await create_container(resolved)
        app.state.container = container
        try:
            yield
        finally:
            await container.close()

    app = FastAPI(title="credits-service", lifespan=lifespan)
    register_error_handlers(app)
    app.include_router(webhooks.router)
    app.include_router(generations.router)
    app.include_router(users.router)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
