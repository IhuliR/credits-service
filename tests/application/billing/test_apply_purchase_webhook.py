from components.application.use_cases.billing.apply_purchase_webhook import (
    ApplyPurchaseWebhook,
)
from components.domain.entities.purchase_event import PurchaseEvent
from components.domain.types.enums.billing.purchase_result import PurchaseResult
from components.domain.types.enums.billing.transaction_kind import TransactionKind


def make_event(event_id: str = "evt-1", credits: int = 50) -> PurchaseEvent:
    return PurchaseEvent(
        event_id=event_id,
        user_id="user-1",
        product_id="credits_50",
        credits=credits,
    )


async def test_new_event_credits_balance(uow, storage) -> None:
    result = await ApplyPurchaseWebhook(uow).execute(make_event())

    assert result == PurchaseResult.PROCESSED
    assert storage.balances["user-1"] == 50
    assert [t.kind for t in storage.transactions] == [TransactionKind.PURCHASE]
    assert uow.commits == 1


async def test_repeated_event_is_ignored(uow, storage) -> None:
    use_case = ApplyPurchaseWebhook(uow)

    await use_case.execute(make_event())
    result = await use_case.execute(make_event())

    assert result == PurchaseResult.DUPLICATE
    assert storage.balances["user-1"] == 50
    assert len(storage.transactions) == 1
