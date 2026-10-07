from pydantic import BaseModel


class GenerationTaskMessage(BaseModel):
    generation_id: str
