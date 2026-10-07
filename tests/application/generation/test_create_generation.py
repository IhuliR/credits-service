import pytest

from components.application.use_cases.generation.create_generation import (
    CreateGeneration,
)
from components.domain.errors.billing.errors import InsufficientCreditsError
from components.domain.types.enums.billing.transaction_kind import TransactionKind
from components.domain.types.enums.generation.generation_status import GenerationStatus


def make_use_case(uow, task_publisher, balance_cache) -> CreateGeneration:
    return CreateGeneration(
        uow=uow,
        task_publisher=task_publisher,
        balance_cache=balance_cache,
        generation_cost=10,
    )


async def test_debits_credits_and_publishes_task(
    uow, storage, task_publisher, balance_cache
) -> None:
    storage.balances["user-1"] = 25
    balance_cache.values["user-1"] = 25

    generation = await make_use_case(uow, task_publisher, balance_cache).execute(
        "user-1", "a cat in space"
    )

    assert generation.status == GenerationStatus.PENDING
    assert storage.balances["user-1"] == 15
    assert storage.generations[generation.id].cost == 10
    assert storage.transactions[-1].kind == TransactionKind.GENERATION_DEBIT
    assert storage.transactions[-1].amount == -10
    assert task_publisher.published == [generation.id]
    assert "user-1" not in balance_cache.values


async def test_insufficient_credits(
    uow, storage, task_publisher, balance_cache
) -> None:
    storage.balances["user-1"] = 5

    with pytest.raises(InsufficientCreditsError):
        await make_use_case(uow, task_publisher, balance_cache).execute(
            "user-1", "a cat in space"
        )

    assert storage.balances["user-1"] == 5
    assert storage.generations == {}
    assert task_publisher.published == []
