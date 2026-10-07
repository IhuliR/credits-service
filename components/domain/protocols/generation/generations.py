from typing import Protocol

from components.domain.entities.generation import Generation
from components.domain.types.enums.generation.generation_status import GenerationStatus


class IGenerationRepository(Protocol):
    async def add(self, generation: Generation) -> None: ...

    async def get(self, generation_id: str) -> Generation | None: ...

    async def update_status(
        self,
        generation_id: str,
        status: GenerationStatus,
        *,
        result_url: str | None = None,
        error: str | None = None,
    ) -> None: ...
