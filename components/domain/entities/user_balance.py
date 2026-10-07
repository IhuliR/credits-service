from dataclasses import dataclass


@dataclass(slots=True)
class UserBalance:
    user_id: str
    balance: int
