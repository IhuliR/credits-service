import logging

from components.domain.protocols.generation.generation_provider import (
    IGenerationProvider,
)
from components.domain.protocols.shared.unit_of_work import IUnitOfWork
from components.domain.types.enums.generation.generation_status import GenerationStatus

logger = logging.getLogger(__name__)


class ProcessGeneration:
    def __init__(self, uow: IUnitOfWork, provider: IGenerationProvider) -> None:
        self._uow = uow
        self._provider = provider

    async def execute(self, generation_id: str) -> None:
        async with self._uow as uow:
            generation = await uow.generations.get(generation_id)
            if generation is None:
                logger.warning("Generation not found generation_id=%s", generation_id)
                return
            if generation.status != GenerationStatus.PENDING:
                logger.info(
                    "Skip generation generation_id=%s status=%s",
                    generation_id,
                    generation.status,
                )
                return
            await uow.generations.update_status(
                generation_id,
                GenerationStatus.PROCESSING,
            )
            await uow.commit()

        result_url = await self._provider.generate(generation.prompt)

        async with self._uow as uow:
            await uow.generations.update_status(
                generation_id,
                GenerationStatus.COMPLETED,
                result_url=result_url,
            )
            await uow.commit()

        logger.info("Generation completed generation_id=%s", generation_id)
