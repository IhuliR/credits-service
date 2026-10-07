from dataclasses import dataclass


@dataclass(slots=True)
class PurchaseEvent:
    event_id: str
    user_id: str
    product_id: str
    credits: int
