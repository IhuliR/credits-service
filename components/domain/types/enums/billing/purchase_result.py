from enum import StrEnum


class PurchaseResult(StrEnum):
    PROCESSED = "processed"
    DUPLICATE = "duplicate"
