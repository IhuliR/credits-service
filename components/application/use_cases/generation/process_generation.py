import asyncio
import logging

from components.domain.entities.balance_transaction import BalanceTransaction
from components.domain.entities.generation import Generation
from components.domain.errors.provider.errors import (
    ProviderPermanentError,
    ProviderTemporaryError,
)
from components.domain.protocols.billing.balance_cache import IBalanceCache
from components.domain.protocols.generation.generation_provider import (
    IGenerationProvider,
)
from components.domain.protocols.shared.unit_of_work import IUnitOfWork
from components.domain.types.enums.billing.transaction_kind import TransactionKind
from components.domain.types.enums.generation.generation_status import GenerationStatus

logger = logging.getLogger(__name__)


class ProcessGeneration:
    _ERROR_MAX_LENGTH = 512

    def __init__(
        self,
        uow: IUnitOfWork,
        provider: IGenerationProvider,
        balance_cache: IBalanceCache,
        *,
        max_attempts: int,
        timeout_seconds: float,
        retry_base_delay_seconds: float,
    ) -> None:
        self._uow = uow
        self._provider = provider
        self._balance_cache = balance_cache
        self._max_attempts = max_attempts
        self._timeout_seconds = timeout_seconds
        self._retry_base_delay_seconds = retry_base_delay_seconds

    async def execute(self, generation_id: str) -> None:
        generation = await self._claim(generation_id)
        if generation is None:
            return

        for attempt in range(1, self._max_attempts + 1):
            try:
                async with asyncio.timeout(self._timeout_seconds):
                    result_url = await self._provider.generate(generation.prompt)
            except ProviderPermanentError as exc:
                await self._fail_generation(
                    generation_id,
                    error=f"Permanent provider error: {exc}",
                )
                return
            except ProviderTemporaryError as exc:
                error = f"Temporary provider error: {exc}"
            except TimeoutError:
                error = f"Provider timeout after {self._timeout_seconds:g} seconds"
            else:
                await self._complete_generation(generation_id, result_url)
                return

            if attempt == self._max_attempts:
                await self._fail_generation(
                    generation_id,
                    error=f"{error}; attempts exhausted ({self._max_attempts})",
                )
                return

            delay = self._retry_base_delay_seconds * (2 ** (attempt - 1))
            logger.warning(
                "Generation attempt failed generation_id=%s attempt=%s/%s "
                "retry_in=%s error=%s",
                generation_id,
                attempt,
                self._max_attempts,
                delay,
                error,
            )
            await asyncio.sleep(delay)

    async def _claim(self, generation_id: str) -> Generation | None:
        async with self._uow as uow:
            generation = await uow.generations.get_for_update(generation_id)
            if generation is None:
                logger.warning("Generation not found generation_id=%s", generation_id)
                return None
            if generation.status != GenerationStatus.PENDING:
                logger.info(
                    "Skip generation generation_id=%s status=%s",
                    generation_id,
                    generation.status,
                )
                return None
            await uow.generations.update_status(
                generation_id,
                GenerationStatus.PROCESSING,
            )
            await uow.commit()
            return generation

    async def _complete_generation(self, generation_id: str, result_url: str) -> None:
        async with self._uow as uow:
            await uow.generations.update_status(
                generation_id,
                GenerationStatus.COMPLETED,
                result_url=result_url,
            )
            await uow.commit()

        logger.info("Generation completed generation_id=%s", generation_id)

    async def _fail_generation(self, generation_id: str, *, error: str) -> None:
        error = error[: self._ERROR_MAX_LENGTH]

        async with self._uow as uow:
            generation = await uow.generations.get_for_update(generation_id)
            if generation is None:
                logger.warning("Generation not found generation_id=%s", generation_id)
                return
            if generation.status != GenerationStatus.PROCESSING:
                logger.info(
                    "Skip generation failure generation_id=%s status=%s",
                    generation_id,
                    generation.status,
                )
                return

            await uow.generations.update_status(
                generation_id,
                GenerationStatus.FAILED,
                error=error,
            )
            await uow.balances.increment(generation.user_id, generation.cost)
            await uow.transactions.add(
                BalanceTransaction(
                    user_id=generation.user_id,
                    amount=generation.cost,
                    kind=TransactionKind.GENERATION_REFUND,
                    reference_id=generation.id,
                )
            )
            await uow.commit()

        await self._balance_cache.invalidate(generation.user_id)
        logger.info(
            "Generation failed and refunded generation_id=%s user_id=%s error=%s",
            generation_id,
            generation.user_id,
            error,
        )
