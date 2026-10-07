from components.domain.entities.balance_transaction import BalanceTransaction
from components.domain.types.enums.billing.transaction_kind import TransactionKind
from components.infrastructure.stores.mysql.models.balance_transaction import (
    BalanceTransactions,
)


def balance_transaction_to_domain(model: BalanceTransactions) -> BalanceTransaction:
    return BalanceTransaction(
        id=model.id,
        user_id=model.user_id,
        amount=model.amount,
        kind=TransactionKind(model.kind),
        reference_id=model.reference_id,
        created_at=model.created_at,
    )


def balance_transaction_to_model(
    transaction: BalanceTransaction,
) -> BalanceTransactions:
    return BalanceTransactions(
        user_id=transaction.user_id,
        amount=transaction.amount,
        kind=transaction.kind.value,
        reference_id=transaction.reference_id,
    )
