class InMemoryBalanceCache:
    def __init__(self) -> None:
        self.values: dict[str, int] = {}

    async def get(self, user_id: str) -> int | None:
        return self.values.get(user_id)

    async def set(self, user_id: str, balance: int) -> None:
        self.values[user_id] = balance

    async def invalidate(self, user_id: str) -> None:
        self.values.pop(user_id, None)


class RecordingTaskPublisher:
    def __init__(self) -> None:
        self.published: list[str] = []

    async def publish(self, generation_id: str) -> None:
        self.published.append(generation_id)


class StubGenerationProvider:
    def __init__(self, result_url: str = "https://cdn.example.com/r.png") -> None:
        self.result_url = result_url
        self.prompts: list[str] = []

    async def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.result_url
