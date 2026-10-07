from pydantic import BaseModel, Field

from components.domain.types.enums.billing.purchase_result import PurchaseResult


class PurchaseWebhookRequest(BaseModel):
    event_id: str = Field(min_length=1, max_length=128)
    user_id: str = Field(min_length=1, max_length=64)
    product_id: str = Field(min_length=1, max_length=128)
    credits: int = Field(gt=0)


class PurchaseWebhookResponse(BaseModel):
    status: PurchaseResult
