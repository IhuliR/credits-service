from typing import Protocol

from components.domain.entities.balance_transaction import BalanceTransaction


class IBalanceTransactionRepository(Protocol):
    async def add(self, transaction: BalanceTransaction) -> None: ...

    async def list_by_user(
        self,
        user_id: str,
        *,
        limit: int,
    ) -> list[BalanceTransaction]: ...
