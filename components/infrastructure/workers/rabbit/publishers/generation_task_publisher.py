from faststream.rabbit import RabbitBroker, RabbitQueue

from components.domain.protocols.generation.generation_task_publisher import (
    IGenerationTaskPublisher,
)
from components.infrastructure.workers.rabbit.messages.generation_task_message import (
    GenerationTaskMessage,
)


class RabbitGenerationTaskPublisher(IGenerationTaskPublisher):
    def __init__(self, broker: RabbitBroker, queue: RabbitQueue) -> None:
        self._broker = broker
        self._queue = queue

    async def publish(self, generation_id: str) -> None:
        message = GenerationTaskMessage(generation_id=generation_id)
        await self._broker.publish(
            message.model_dump(),
            queue=self._queue,
            persist=True,
        )
