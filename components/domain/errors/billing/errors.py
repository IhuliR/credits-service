from components.domain.errors.core.base import DomainError


class InsufficientCreditsError(DomainError):
    def __init__(self, *, user_id: str, required: int, available: int) -> None:
        super().__init__(
            f"Insufficient credits user_id={user_id} "
            f"required={required} available={available}"
        )
        self.user_id = user_id
        self.required = required
        self.available = available
