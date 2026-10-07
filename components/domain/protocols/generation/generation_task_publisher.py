from typing import Protocol


class IGenerationTaskPublisher(Protocol):
    async def publish(self, generation_id: str) -> None: ...
