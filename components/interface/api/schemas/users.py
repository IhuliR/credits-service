from datetime import datetime

from pydantic import BaseModel

from components.domain.types.enums.billing.transaction_kind import TransactionKind


class BalanceResponse(BaseModel):
    user_id: str
    balance: int


class TransactionResponse(BaseModel):
    amount: int
    kind: TransactionKind
    reference_id: str
    created_at: datetime | None


class TransactionsResponse(BaseModel):
    items: list[TransactionResponse]
