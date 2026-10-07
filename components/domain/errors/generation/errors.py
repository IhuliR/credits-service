from components.domain.errors.core.base import DomainError


class GenerationNotFoundError(DomainError):
    def __init__(self, generation_id: str) -> None:
        super().__init__(f"Generation not found generation_id={generation_id}")
        self.generation_id = generation_id
