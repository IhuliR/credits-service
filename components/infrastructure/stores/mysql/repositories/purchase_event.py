from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from components.domain.entities.purchase_event import PurchaseEvent
from components.domain.errors.billing.errors import DuplicatePurchaseEventError
from components.domain.protocols.billing.purchase_events import (
    IPurchaseEventRepository,
)
from components.infrastructure.stores.mysql.models.purchase_event import PurchaseEvents


class PurchaseEventRepository(IPurchaseEventRepository):
    _EVENT_ID_UNIQUE_CONSTRAINT = "uq_purchase_events_event_id"

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
        try:
            await self._session.flush()
        except IntegrityError as exc:
            if self._is_duplicate_event_id(exc):
                raise DuplicatePurchaseEventError(event.event_id) from exc
            raise

    def _is_duplicate_event_id(self, exc: IntegrityError) -> bool:
        error_args = getattr(exc.orig, "args", ())
        error_code = next(iter(error_args), None)
        return error_code == 1062 and self._EVENT_ID_UNIQUE_CONSTRAINT in str(
            error_args
        )
