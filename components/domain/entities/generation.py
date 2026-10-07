from dataclasses import dataclass
from datetime import datetime

from components.domain.types.enums.generation.generation_status import GenerationStatus


@dataclass(slots=True)
class Generation:
    id: str
    user_id: str
    prompt: str
    status: GenerationStatus
    cost: int
    result_url: str | None = None
    error: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
