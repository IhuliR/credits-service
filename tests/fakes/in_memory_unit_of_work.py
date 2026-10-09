from copy import deepcopy
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
        self._snapshot: InMemoryStorage | None = None

    async def __aenter__(self) -> Self:
        self._snapshot = deepcopy(self.storage)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._snapshot is not None:
            self._restore_snapshot()

    async def commit(self) -> None:
        self.commits += 1
        self._snapshot = None

    async def rollback(self) -> None:
        if self._snapshot is not None:
            self._restore_snapshot()

    def _restore_snapshot(self) -> None:
        if self._snapshot is None:
            return
        self.storage.balances = self._snapshot.balances
        self.storage.generations = self._snapshot.generations
        self.storage.purchase_events = self._snapshot.purchase_events
        self.storage.transactions = self._snapshot.transactions
        self._snapshot = None
