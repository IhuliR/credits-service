from typing import Annotated

from fastapi import APIRouter, Depends

from components.application.use_cases.billing.apply_purchase_webhook import (
    ApplyPurchaseWebhook,
)
from components.domain.entities.purchase_event import PurchaseEvent
from components.interface.api.dependencies import (
    get_apply_purchase_webhook,
    verify_webhook_secret,
)
from components.interface.api.schemas.webhooks import (
    PurchaseWebhookRequest,
    PurchaseWebhookResponse,
)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post(
    "/purchase",
    response_model=PurchaseWebhookResponse,
    dependencies=[Depends(verify_webhook_secret)],
)
async def purchase_webhook(
    body: PurchaseWebhookRequest,
    use_case: Annotated[ApplyPurchaseWebhook, Depends(get_apply_purchase_webhook)],
) -> PurchaseWebhookResponse:
    result = await use_case.execute(
        PurchaseEvent(
            event_id=body.event_id,
            user_id=body.user_id,
            product_id=body.product_id,
            credits=body.credits,
        )
    )
    return PurchaseWebhookResponse(status=result)
