from components.domain.entities.balance_transaction import BalanceTransaction
from components.domain.protocols.shared.unit_of_work import IUnitOfWork


class ListUserTransactions:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: str, *, limit: int) -> list[BalanceTransaction]:
        async with self._uow as uow:
            return await uow.transactions.list_by_user(user_id, limit=limit)
