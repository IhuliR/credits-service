from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from components.domain.protocols.shared.unit_of_work import IUnitOfWork
from components.infrastructure.stores.mysql.repositories.balance_transaction import (
    BalanceTransactionRepository,
)
from components.infrastructure.stores.mysql.repositories.generation import (
    GenerationRepository,
)
from components.infrastructure.stores.mysql.repositories.purchase_event import (
    PurchaseEventRepository,
)
from components.infrastructure.stores.mysql.repositories.user_balance import (
    UserBalanceRepository,
)


class MySQLUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        session = self._session_factory()
        self._session = session
        self.balances = UserBalanceRepository(session)
        self.generations = GenerationRepository(session)
        self.purchase_events = PurchaseEventRepository(session)
        self.transactions = BalanceTransactionRepository(session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            await self._session.close()
        finally:
            self._session = None

    async def commit(self) -> None:
        await self._require_session().commit()

    async def rollback(self) -> None:
        await self._require_session().rollback()

    def _require_session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Unit of work is not started")
        return self._session
