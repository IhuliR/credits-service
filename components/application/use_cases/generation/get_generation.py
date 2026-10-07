from components.domain.entities.generation import Generation
from components.domain.errors.generation.errors import GenerationNotFoundError
from components.domain.protocols.shared.unit_of_work import IUnitOfWork


class GetGeneration:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, generation_id: str) -> Generation:
        async with self._uow as uow:
            generation = await uow.generations.get(generation_id)
        if generation is None:
            raise GenerationNotFoundError(generation_id)
        return generation
