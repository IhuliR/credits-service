import asyncio
import hashlib
import random
import re
from collections import defaultdict

from components.domain.errors.provider.errors import (
    ProviderPermanentError,
    ProviderTemporaryError,
)
from components.domain.protocols.generation.generation_provider import (
    IGenerationProvider,
)


class FakeGenerationProvider(IGenerationProvider):
    """Имитация внешнего AI-провайдера. Не меняйте этот класс.

    Поведение задаётся маркером в тексте prompt:
    - `[fail]` — провайдер окончательно отказывает (ProviderPermanentError);
    - `[flaky:N]` — первые N вызовов с этим prompt падают с ProviderTemporaryError;
    - `[slow]` — провайдер зависает на 5 минут;
    - без маркера — успешный ответ за 0.1–0.5 секунды.

    Счётчик вызовов для `[flaky:N]` хранится в памяти процесса воркера.
    """

    _FAIL_MARKER = "[fail]"
    _SLOW_MARKER = "[slow]"
    _FLAKY_PATTERN = re.compile(r"\[flaky:(\d+)\]")

    def __init__(self, hang_seconds: float = 300.0) -> None:
        self._hang_seconds = hang_seconds
        self._calls: defaultdict[str, int] = defaultdict(int)

    async def generate(self, prompt: str) -> str:
        self._calls[prompt] += 1
        call_number = self._calls[prompt]

        if self._SLOW_MARKER in prompt:
            await asyncio.sleep(self._hang_seconds)

        if self._FAIL_MARKER in prompt:
            raise ProviderPermanentError("Request rejected by content policy")

        flaky = self._FLAKY_PATTERN.search(prompt)
        if flaky is not None and call_number <= int(flaky.group(1)):
            raise ProviderTemporaryError(
                f"Provider is temporarily unavailable, call={call_number}"
            )

        await asyncio.sleep(random.uniform(0.1, 0.5))
        digest = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        return f"https://cdn.example.com/results/{digest}.png"
