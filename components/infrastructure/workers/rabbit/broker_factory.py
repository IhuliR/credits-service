from faststream.rabbit import RabbitBroker, RabbitQueue

from components.core.config.settings import Settings


def create_rabbit_broker(settings: Settings) -> RabbitBroker:
    return RabbitBroker(settings.rabbit_url)


def build_generations_queue(settings: Settings) -> RabbitQueue:
    return RabbitQueue(settings.generations_queue, durable=True)
