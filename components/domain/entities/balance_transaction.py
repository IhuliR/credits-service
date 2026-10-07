from dataclasses import dataclass
from datetime import datetime

from components.domain.types.enums.billing.transaction_kind import TransactionKind


@dataclass(slots=True)
class BalanceTransaction:
    user_id: str
    amount: int
    kind: TransactionKind
    reference_id: str
    id: int | None = None
    created_at: datetime | None = None
