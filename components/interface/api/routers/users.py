from typing import Annotated

from fastapi import APIRouter, Depends, Query

from components.application.use_cases.billing.get_user_balance import GetUserBalance
from components.application.use_cases.billing.list_user_transactions import (
    ListUserTransactions,
)
from components.interface.api.dependencies import (
    get_list_user_transactions,
    get_user_balance,
)
from components.interface.api.schemas.users import (
    BalanceResponse,
    TransactionResponse,
    TransactionsResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}/balance", response_model=BalanceResponse)
async def read_balance(
    user_id: str,
    use_case: Annotated[GetUserBalance, Depends(get_user_balance)],
) -> BalanceResponse:
    balance = await use_case.execute(user_id)
    return BalanceResponse(user_id=user_id, balance=balance)


@router.get("/{user_id}/transactions", response_model=TransactionsResponse)
async def read_transactions(
    user_id: str,
    use_case: Annotated[ListUserTransactions, Depends(get_list_user_transactions)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> TransactionsResponse:
    transactions = await use_case.execute(user_id, limit=limit)
    return TransactionsResponse(
        items=[
            TransactionResponse(
                amount=transaction.amount,
                kind=transaction.kind,
                reference_id=transaction.reference_id,
                created_at=transaction.created_at,
            )
            for transaction in transactions
        ]
    )
