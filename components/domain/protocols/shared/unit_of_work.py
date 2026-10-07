from types import TracebackType
from typing import Protocol, Self

from components.domain.protocols.billing.balance_transactions import (
    IBalanceTransactionRepository,
)
from components.domain.protocols.billing.purchase_events import (
    IPurchaseEventRepository,
)
from components.domain.protocols.billing.user_balances import (
    IUserBalanceRepository,
)
from components.domain.protocols.generation.generations import (
    IGenerationRepository,
)


class IUnitOfWork(Protocol):
    """Одна транзакция БД. Всё, что не закоммичено до выхода из `async with`, откатывается."""

    balances: IUserBalanceRepository
    generations: IGenerationRepository
    purchase_events: IPurchaseEventRepository
    transactions: IBalanceTransactionRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
