from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from components.domain.entities.purchase_event import PurchaseEvent
from components.domain.protocols.billing.purchase_events import (
    IPurchaseEventRepository,
)
from components.infrastructure.stores.mysql.models.purchase_event import PurchaseEvents


class PurchaseEventRepository(IPurchaseEventRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(self, event_id: str) -> bool:
        found = await self._session.scalar(
            select(PurchaseEvents.id)
            .where(PurchaseEvents.event_id == event_id)
            .limit(1)
        )
        return found is not None

    async def add(self, event: PurchaseEvent) -> None:
        self._session.add(
            PurchaseEvents(
                event_id=event.event_id,
                user_id=event.user_id,
                product_id=event.product_id,
                credits=event.credits,
            )
        )
        await self._session.flush()
