from components.domain.entities.generation import Generation
from components.domain.types.enums.generation.generation_status import GenerationStatus
from components.infrastructure.stores.mysql.models.generation import Generations


def generation_to_domain(model: Generations) -> Generation:
    return Generation(
        id=model.id,
        user_id=model.user_id,
        prompt=model.prompt,
        status=GenerationStatus(model.status),
        cost=model.cost,
        result_url=model.result_url,
        error=model.error,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def generation_to_model(generation: Generation) -> Generations:
    return Generations(
        id=generation.id,
        user_id=generation.user_id,
        prompt=generation.prompt,
        status=generation.status.value,
        cost=generation.cost,
        result_url=generation.result_url,
        error=generation.error,
    )
