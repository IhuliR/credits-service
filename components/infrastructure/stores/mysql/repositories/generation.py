from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from components.domain.entities.generation import Generation
from components.domain.protocols.generation.generations import (
    IGenerationRepository,
)
from components.domain.types.enums.generation.generation_status import GenerationStatus
from components.infrastructure.stores.mysql.mappers.generation import (
    generation_to_domain,
    generation_to_model,
)
from components.infrastructure.stores.mysql.models.generation import Generations


class GenerationRepository(IGenerationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, generation: Generation) -> None:
        self._session.add(generation_to_model(generation))
        await self._session.flush()

    async def get(self, generation_id: str) -> Generation | None:
        model = await self._session.scalar(
            select(Generations).where(Generations.id == generation_id)
        )
        return None if model is None else generation_to_domain(model)

    async def update_status(
        self,
        generation_id: str,
        status: GenerationStatus,
        *,
        result_url: str | None = None,
        error: str | None = None,
    ) -> None:
        await self._session.execute(
            update(Generations)
            .where(Generations.id == generation_id)
            .values(status=status.value, result_url=result_url, error=error)
        )
