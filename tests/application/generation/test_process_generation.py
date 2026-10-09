import asyncio
from unittest.mock import AsyncMock, call, patch

import pytest

from components.application.use_cases.generation.process_generation import (
    ProcessGeneration,
)
from components.domain.entities.generation import Generation
from components.domain.errors.provider.errors import (
    ProviderPermanentError,
    ProviderTemporaryError,
)
from components.domain.types.enums.billing.transaction_kind import TransactionKind
from components.domain.types.enums.generation.generation_status import GenerationStatus


class ScriptedProvider:
    def __init__(self, outcomes: list[str | Exception]) -> None:
        self._outcomes = outcomes
        self.prompts: list[str] = []

    async def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        outcome = self._outcomes[len(self.prompts) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class HangingProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def generate(self, prompt: str) -> str:
        self.calls += 1
        await asyncio.Event().wait()
        raise AssertionError("unreachable")


def make_generation(status: GenerationStatus) -> Generation:
    return Generation(
        id="gen-1",
        user_id="user-1",
        prompt="a cat in space",
        status=status,
        cost=10,
    )


def make_use_case(
    uow,
    provider,
    balance_cache,
    *,
    max_attempts: int = 3,
    timeout_seconds: float = 0.05,
    retry_base_delay_seconds: float = 0,
) -> ProcessGeneration:
    return ProcessGeneration(
        uow=uow,
        provider=provider,
        balance_cache=balance_cache,
        max_attempts=max_attempts,
        timeout_seconds=timeout_seconds,
        retry_base_delay_seconds=retry_base_delay_seconds,
    )


def assert_single_refund(storage) -> None:
    refunds = [
        transaction
        for transaction in storage.transactions
        if transaction.kind == TransactionKind.GENERATION_REFUND
    ]
    assert len(refunds) == 1
    assert refunds[0].amount == 10
    assert refunds[0].reference_id == "gen-1"


async def test_completes_pending_generation(
    uow, storage, provider, balance_cache
) -> None:
    storage.generations["gen-1"] = make_generation(GenerationStatus.PENDING)

    await make_use_case(uow, provider, balance_cache).execute("gen-1")

    generation = storage.generations["gen-1"]
    assert generation.status == GenerationStatus.COMPLETED
    assert generation.result_url == provider.result_url
    assert provider.prompts == ["a cat in space"]
    assert uow.generations.for_update_calls == ["gen-1"]


async def test_retries_temporary_error_then_completes(
    uow, storage, balance_cache
) -> None:
    storage.generations["gen-1"] = make_generation(GenerationStatus.PENDING)
    provider = ScriptedProvider(
        [
            ProviderTemporaryError("temporarily unavailable"),
            "https://cdn.example.com/result.png",
        ]
    )

    with patch(
        "components.application.use_cases.generation.process_generation.asyncio.sleep",
        new_callable=AsyncMock,
    ) as sleep:
        await make_use_case(
            uow,
            provider,
            balance_cache,
            retry_base_delay_seconds=0.5,
        ).execute("gen-1")

    assert storage.generations["gen-1"].status == GenerationStatus.COMPLETED
    assert len(provider.prompts) == 2
    sleep.assert_awaited_once_with(0.5)
    assert storage.transactions == []


async def test_permanent_error_fails_and_refunds_without_retry(
    uow, storage, balance_cache
) -> None:
    storage.generations["gen-1"] = make_generation(GenerationStatus.PENDING)
    storage.balances["user-1"] = 0
    balance_cache.values["user-1"] = 0
    provider = ScriptedProvider([ProviderPermanentError("content rejected")])

    await make_use_case(uow, provider, balance_cache).execute("gen-1")

    generation = storage.generations["gen-1"]
    assert generation.status == GenerationStatus.FAILED
    assert generation.error == "Permanent provider error: content rejected"
    assert storage.balances["user-1"] == 10
    assert_single_refund(storage)
    assert len(provider.prompts) == 1
    assert "user-1" not in balance_cache.values


async def test_long_error_is_truncated_before_refund_transaction(
    uow, storage, balance_cache
) -> None:
    storage.generations["gen-1"] = make_generation(GenerationStatus.PENDING)
    storage.balances["user-1"] = 0
    provider = ScriptedProvider([ProviderPermanentError("x" * 600)])

    await make_use_case(uow, provider, balance_cache).execute("gen-1")

    generation = storage.generations["gen-1"]
    assert generation.error is not None
    assert len(generation.error) == 512
    assert generation.error.startswith("Permanent provider error: ")
    assert storage.balances["user-1"] == 10
    assert_single_refund(storage)


async def test_exhausted_temporary_errors_fail_and_refund_once(
    uow, storage, balance_cache
) -> None:
    storage.generations["gen-1"] = make_generation(GenerationStatus.PENDING)
    storage.balances["user-1"] = 0
    provider = ScriptedProvider(
        [
            ProviderTemporaryError("temporary 1"),
            ProviderTemporaryError("temporary 2"),
            ProviderTemporaryError("temporary 3"),
        ]
    )

    with patch(
        "components.application.use_cases.generation.process_generation.asyncio.sleep",
        new_callable=AsyncMock,
    ) as sleep:
        await make_use_case(
            uow,
            provider,
            balance_cache,
            retry_base_delay_seconds=0.5,
        ).execute("gen-1")

    generation = storage.generations["gen-1"]
    assert generation.status == GenerationStatus.FAILED
    assert generation.error is not None
    assert "attempts exhausted (3)" in generation.error
    assert storage.balances["user-1"] == 10
    assert_single_refund(storage)
    assert len(provider.prompts) == 3
    assert sleep.await_args_list == [call(0.5), call(1.0)]


async def test_timeouts_are_retried_then_fail_and_refund(
    uow, storage, balance_cache
) -> None:
    storage.generations["gen-1"] = make_generation(GenerationStatus.PENDING)
    storage.balances["user-1"] = 0
    provider = HangingProvider()

    await make_use_case(
        uow,
        provider,
        balance_cache,
        max_attempts=2,
        timeout_seconds=0.001,
    ).execute("gen-1")

    generation = storage.generations["gen-1"]
    assert generation.status == GenerationStatus.FAILED
    assert generation.error is not None
    assert "Provider timeout" in generation.error
    assert storage.balances["user-1"] == 10
    assert_single_refund(storage)
    assert provider.calls == 2


async def test_repeated_delivery_of_failed_generation_does_not_refund_twice(
    uow, storage, balance_cache
) -> None:
    storage.generations["gen-1"] = make_generation(GenerationStatus.PENDING)
    storage.balances["user-1"] = 0
    provider = ScriptedProvider([ProviderPermanentError("content rejected")])
    use_case = make_use_case(uow, provider, balance_cache)

    await use_case.execute("gen-1")
    await use_case.execute("gen-1")

    assert storage.balances["user-1"] == 10
    assert_single_refund(storage)
    assert len(provider.prompts) == 1


async def test_processing_generation_is_not_claimed_again(
    uow, storage, provider, balance_cache
) -> None:
    storage.generations["gen-1"] = make_generation(GenerationStatus.PROCESSING)

    await make_use_case(uow, provider, balance_cache).execute("gen-1")

    assert provider.prompts == []
    assert storage.generations["gen-1"].status == GenerationStatus.PROCESSING


async def test_refund_transaction_is_rolled_back_when_commit_fails(
    uow, storage, balance_cache
) -> None:
    storage.generations["gen-1"] = make_generation(GenerationStatus.PENDING)
    storage.balances["user-1"] = 0
    balance_cache.values["user-1"] = 0
    provider = ScriptedProvider([ProviderPermanentError("content rejected")])
    successful_commit = uow.commit
    commit_calls = 0

    async def fail_refund_commit() -> None:
        nonlocal commit_calls
        commit_calls += 1
        if commit_calls == 2:
            raise RuntimeError("commit failed")
        await successful_commit()

    uow.commit = fail_refund_commit

    with pytest.raises(RuntimeError, match="commit failed"):
        await make_use_case(uow, provider, balance_cache).execute("gen-1")

    assert storage.generations["gen-1"].status == GenerationStatus.PROCESSING
    assert storage.balances["user-1"] == 0
    assert storage.transactions == []
    assert balance_cache.values["user-1"] == 0


async def test_skips_already_processed_generation(
    uow, storage, provider, balance_cache
) -> None:
    storage.generations["gen-1"] = make_generation(GenerationStatus.COMPLETED)

    await make_use_case(uow, provider, balance_cache).execute("gen-1")

    assert provider.prompts == []


async def test_missing_generation_is_ignored(uow, provider, balance_cache) -> None:
    await make_use_case(uow, provider, balance_cache).execute("missing")

    assert provider.prompts == []
