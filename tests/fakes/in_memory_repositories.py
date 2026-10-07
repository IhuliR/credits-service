from dataclasses import replace

from components.domain.entities.balance_transaction import BalanceTransaction
from components.domain.entities.generation import Generation
from components.domain.entities.purchase_event import PurchaseEvent
from components.domain.entities.user_balance import UserBalance
from components.domain.types.enums.generation.generation_status import GenerationStatus
from tests.fakes.in_memory_storage import InMemoryStorage


class InMemoryUserBalanceRepository:
    def __init__(self, storage: InMemoryStorage) -> None:
        self._storage = storage

    async def get(self, user_id: str) -> UserBalance | None:
        if user_id not in self._storage.balances:
            return None
        return UserBalance(user_id=user_id, balance=self._storage.balances[user_id])

    async def set_balance(self, user_id: str, balance: int) -> None:
        if user_id in self._storage.balances:
            self._storage.balances[user_id] = balance

    async def increment(self, user_id: str, delta: int) -> None:
        self._storage.balances[user_id] = self._storage.balances.get(user_id, 0) + delta


class InMemoryGenerationRepository:
    def __init__(self, storage: InMemoryStorage) -> None:
        self._storage = storage

    async def add(self, generation: Generation) -> None:
        self._storage.generations[generation.id] = replace(generation)

    async def get(self, generation_id: str) -> Generation | None:
        generation = self._storage.generations.get(generation_id)
        return None if generation is None else replace(generation)

    async def update_status(
        self,
        generation_id: str,
        status: GenerationStatus,
        *,
        result_url: str | None = None,
        error: str | None = None,
    ) -> None:
        generation = self._storage.generations.get(generation_id)
        if generation is None:
            return
        generation.status = status
        generation.result_url = result_url
        generation.error = error


class InMemoryPurchaseEventRepository:
    def __init__(self, storage: InMemoryStorage) -> None:
        self._storage = storage

    async def exists(self, event_id: str) -> bool:
        return any(e.event_id == event_id for e in self._storage.purchase_events)

    async def add(self, event: PurchaseEvent) -> None:
        self._storage.purchase_events.append(event)


class InMemoryBalanceTransactionRepository:
    def __init__(self, storage: InMemoryStorage) -> None:
        self._storage = storage

    async def add(self, transaction: BalanceTransaction) -> None:
        self._storage.transactions.append(transaction)

    async def list_by_user(
        self,
        user_id: str,
        *,
        limit: int,
    ) -> list[BalanceTransaction]:
        items = [t for t in self._storage.transactions if t.user_id == user_id]
        return list(reversed(items))[:limit]
