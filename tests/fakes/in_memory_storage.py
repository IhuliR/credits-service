from dataclasses import dataclass, field

from components.domain.entities.balance_transaction import BalanceTransaction
from components.domain.entities.generation import Generation
from components.domain.entities.purchase_event import PurchaseEvent


@dataclass
class InMemoryStorage:
    balances: dict[str, int] = field(default_factory=dict)
    generations: dict[str, Generation] = field(default_factory=dict)
    purchase_events: list[PurchaseEvent] = field(default_factory=list)
    transactions: list[BalanceTransaction] = field(default_factory=list)
