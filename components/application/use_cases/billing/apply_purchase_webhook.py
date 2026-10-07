import logging

from components.domain.entities.balance_transaction import BalanceTransaction
from components.domain.entities.purchase_event import PurchaseEvent
from components.domain.protocols.shared.unit_of_work import IUnitOfWork
from components.domain.types.enums.billing.purchase_result import PurchaseResult
from components.domain.types.enums.billing.transaction_kind import TransactionKind

logger = logging.getLogger(__name__)


class ApplyPurchaseWebhook:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, event: PurchaseEvent) -> PurchaseResult:
        async with self._uow as uow:
            if await uow.purchase_events.exists(event.event_id):
                logger.info("Duplicate purchase event event_id=%s", event.event_id)
                return PurchaseResult.DUPLICATE

            await uow.purchase_events.add(event)
            await uow.balances.increment(event.user_id, event.credits)
            await uow.transactions.add(
                BalanceTransaction(
                    user_id=event.user_id,
                    amount=event.credits,
                    kind=TransactionKind.PURCHASE,
                    reference_id=event.event_id,
                )
            )
            await uow.commit()

        logger.info(
            "Purchase applied event_id=%s user_id=%s credits=%s",
            event.event_id,
            event.user_id,
            event.credits,
        )
        return PurchaseResult.PROCESSED
