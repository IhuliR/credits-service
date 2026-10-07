from typing import Protocol

from components.domain.entities.user_balance import UserBalance


class IUserBalanceRepository(Protocol):
    async def get(self, user_id: str) -> UserBalance | None: ...

    async def set_balance(self, user_id: str, balance: int) -> None: ...

    async def increment(self, user_id: str, delta: int) -> None:
        """Прибавляет delta к балансу, создавая запись пользователя при необходимости."""
        ...
