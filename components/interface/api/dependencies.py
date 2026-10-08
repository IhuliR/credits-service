import hmac
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status

from components.application.use_cases.billing.apply_purchase_webhook import (
    ApplyPurchaseWebhook,
)
from components.application.use_cases.billing.get_user_balance import GetUserBalance
from components.application.use_cases.billing.list_user_transactions import (
    ListUserTransactions,
)
from components.application.use_cases.generation.create_generation import (
    CreateGeneration,
)
from components.application.use_cases.generation.get_generation import GetGeneration
from components.interface.composition.container import Container


def get_container(request: Request) -> Container:
    return request.app.state.container


ContainerDep = Annotated[Container, Depends(get_container)]


async def verify_webhook_secret(
    container: ContainerDep,
    x_webhook_secret: Annotated[str | None, Header()] = None,
) -> None:
    expected = container.settings.webhook_secret
    if x_webhook_secret is None or not hmac.compare_digest(x_webhook_secret, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret",
        )


def get_apply_purchase_webhook(container: ContainerDep) -> ApplyPurchaseWebhook:
    return ApplyPurchaseWebhook(
        uow=container.unit_of_work(),
        balance_cache=container.balance_cache(),
    )


def get_user_balance(container: ContainerDep) -> GetUserBalance:
    return GetUserBalance(
        uow=container.unit_of_work(),
        balance_cache=container.balance_cache(),
    )


def get_list_user_transactions(container: ContainerDep) -> ListUserTransactions:
    return ListUserTransactions(uow=container.unit_of_work())


def get_create_generation(container: ContainerDep) -> CreateGeneration:
    return CreateGeneration(
        uow=container.unit_of_work(),
        task_publisher=container.generation_task_publisher(),
        balance_cache=container.balance_cache(),
        generation_cost=container.settings.generation_cost,
    )


def get_generation(container: ContainerDep) -> GetGeneration:
    return GetGeneration(uow=container.unit_of_work())
