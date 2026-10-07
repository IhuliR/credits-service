from sqlalchemy import select, update
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from components.domain.entities.user_balance import UserBalance
from components.domain.protocols.billing.user_balances import (
    IUserBalanceRepository,
)
from components.infrastructure.stores.mysql.models.user_balance import UserBalances


class UserBalanceRepository(IUserBalanceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, user_id: str) -> UserBalance | None:
        model = await self._session.scalar(
            select(UserBalances).where(UserBalances.user_id == user_id)
        )
        if model is None:
            return None
        return UserBalance(user_id=model.user_id, balance=model.balance)

    async def set_balance(self, user_id: str, balance: int) -> None:
        await self._session.execute(
            update(UserBalances)
            .where(UserBalances.user_id == user_id)
            .values(balance=balance)
        )

    async def increment(self, user_id: str, delta: int) -> None:
        stmt = mysql_insert(UserBalances).values(user_id=user_id, balance=delta)
        stmt = stmt.on_duplicate_key_update(balance=UserBalances.balance + delta)
        await self._session.execute(stmt)
