from typing import Protocol


class IGenerationProvider(Protocol):
    async def generate(self, prompt: str) -> str:
        """Возвращает URL результата.

        Raises:
            ProviderTemporaryError: временный сбой, можно повторить.
            ProviderPermanentError: окончательный отказ.
        """
        ...
