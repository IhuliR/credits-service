from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from components.domain.entities.balance_transaction import BalanceTransaction
from components.domain.protocols.billing.balance_transactions import (
    IBalanceTransactionRepository,
)
from components.infrastructure.stores.mysql.mappers.balance_transaction import (
    balance_transaction_to_domain,
    balance_transaction_to_model,
)
from components.infrastructure.stores.mysql.models.balance_transaction import (
    BalanceTransactions,
)


class BalanceTransactionRepository(IBalanceTransactionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, transaction: BalanceTransaction) -> None:
        self._session.add(balance_transaction_to_model(transaction))
        await self._session.flush()

    async def list_by_user(
        self,
        user_id: str,
        *,
        limit: int,
    ) -> list[BalanceTransaction]:
        result = await self._session.scalars(
            select(BalanceTransactions)
            .where(BalanceTransactions.user_id == user_id)
            .order_by(BalanceTransactions.id.desc())
            .limit(limit)
        )
        return [balance_transaction_to_domain(model) for model in result]
