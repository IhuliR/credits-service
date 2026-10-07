from components.domain.protocols.billing.balance_cache import IBalanceCache
from components.domain.protocols.shared.unit_of_work import IUnitOfWork


class GetUserBalance:
    def __init__(self, uow: IUnitOfWork, balance_cache: IBalanceCache) -> None:
        self._uow = uow
        self._balance_cache = balance_cache

    async def execute(self, user_id: str) -> int:
        cached = await self._balance_cache.get(user_id)
        if cached is not None:
            return cached

        async with self._uow as uow:
            balance = await uow.balances.get(user_id)

        value = 0 if balance is None else balance.balance
        await self._balance_cache.set(user_id, value)
        return value
