from datetime import datetime

from pydantic import BaseModel, Field

from components.domain.types.enums.generation.generation_status import GenerationStatus


class CreateGenerationRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=64)
    prompt: str = Field(min_length=1, max_length=2000)


class CreateGenerationResponse(BaseModel):
    id: str
    status: GenerationStatus


class GenerationResponse(BaseModel):
    id: str
    user_id: str
    status: GenerationStatus
    cost: int
    result_url: str | None
    error: str | None
    created_at: datetime | None
    updated_at: datetime | None
