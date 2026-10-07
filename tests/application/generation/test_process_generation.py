from components.application.use_cases.generation.process_generation import (
    ProcessGeneration,
)
from components.domain.entities.generation import Generation
from components.domain.types.enums.generation.generation_status import GenerationStatus


def make_generation(status: GenerationStatus) -> Generation:
    return Generation(
        id="gen-1",
        user_id="user-1",
        prompt="a cat in space",
        status=status,
        cost=10,
    )


async def test_completes_pending_generation(uow, storage, provider) -> None:
    storage.generations["gen-1"] = make_generation(GenerationStatus.PENDING)

    await ProcessGeneration(uow, provider).execute("gen-1")

    generation = storage.generations["gen-1"]
    assert generation.status == GenerationStatus.COMPLETED
    assert generation.result_url == provider.result_url


async def test_skips_already_processed_generation(uow, storage, provider) -> None:
    storage.generations["gen-1"] = make_generation(GenerationStatus.COMPLETED)

    await ProcessGeneration(uow, provider).execute("gen-1")

    assert provider.prompts == []


async def test_missing_generation_is_ignored(uow, provider) -> None:
    await ProcessGeneration(uow, provider).execute("missing")

    assert provider.prompts == []
