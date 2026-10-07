from types import TracebackType
from typing import Self

from tests.fakes.in_memory_repositories import (
    InMemoryBalanceTransactionRepository,
    InMemoryGenerationRepository,
    InMemoryPurchaseEventRepository,
    InMemoryUserBalanceRepository,
)
from tests.fakes.in_memory_storage import InMemoryStorage


class InMemoryUnitOfWork:
    """In-memory реализация IUnitOfWork для юнит-тестов use case'ов."""

    def __init__(self, storage: InMemoryStorage) -> None:
        self.storage = storage
        self.balances = InMemoryUserBalanceRepository(storage)
        self.generations = InMemoryGenerationRepository(storage)
        self.purchase_events = InMemoryPurchaseEventRepository(storage)
        self.transactions = InMemoryBalanceTransactionRepository(storage)
        self.commits = 0

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        return None
