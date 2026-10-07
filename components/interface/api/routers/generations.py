from typing import Annotated

from fastapi import APIRouter, Depends, status

from components.application.use_cases.generation.create_generation import (
    CreateGeneration,
)
from components.application.use_cases.generation.get_generation import GetGeneration
from components.interface.api.dependencies import (
    get_create_generation,
    get_generation,
)
from components.interface.api.schemas.generations import (
    CreateGenerationRequest,
    CreateGenerationResponse,
    GenerationResponse,
)

router = APIRouter(prefix="/generations", tags=["generations"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=CreateGenerationResponse,
)
async def create_generation(
    body: CreateGenerationRequest,
    use_case: Annotated[CreateGeneration, Depends(get_create_generation)],
) -> CreateGenerationResponse:
    generation = await use_case.execute(user_id=body.user_id, prompt=body.prompt)
    return CreateGenerationResponse(id=generation.id, status=generation.status)


@router.get("/{generation_id}", response_model=GenerationResponse)
async def read_generation(
    generation_id: str,
    use_case: Annotated[GetGeneration, Depends(get_generation)],
) -> GenerationResponse:
    generation = await use_case.execute(generation_id)
    return GenerationResponse(
        id=generation.id,
        user_id=generation.user_id,
        status=generation.status,
        cost=generation.cost,
        result_url=generation.result_url,
        error=generation.error,
        created_at=generation.created_at,
        updated_at=generation.updated_at,
    )
