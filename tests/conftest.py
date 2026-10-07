import pytest

from tests.fakes.in_memory_services import (
    InMemoryBalanceCache,
    RecordingTaskPublisher,
    StubGenerationProvider,
)
from tests.fakes.in_memory_storage import InMemoryStorage
from tests.fakes.in_memory_unit_of_work import InMemoryUnitOfWork


@pytest.fixture
def storage() -> InMemoryStorage:
    return InMemoryStorage()


@pytest.fixture
def uow(storage: InMemoryStorage) -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork(storage)


@pytest.fixture
def balance_cache() -> InMemoryBalanceCache:
    return InMemoryBalanceCache()


@pytest.fixture
def task_publisher() -> RecordingTaskPublisher:
    return RecordingTaskPublisher()


@pytest.fixture
def provider() -> StubGenerationProvider:
    return StubGenerationProvider()
