from typing import Protocol

from components.domain.entities.purchase_event import PurchaseEvent


class IPurchaseEventRepository(Protocol):
    async def exists(self, event_id: str) -> bool: ...

    async def add(self, event: PurchaseEvent) -> None: ...
