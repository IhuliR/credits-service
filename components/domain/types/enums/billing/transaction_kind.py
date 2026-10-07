from enum import StrEnum


class TransactionKind(StrEnum):
    PURCHASE = "purchase"
    GENERATION_DEBIT = "generation_debit"
    GENERATION_REFUND = "generation_refund"
