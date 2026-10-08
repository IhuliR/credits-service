from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from components.domain.entities.purchase_event import PurchaseEvent
from components.domain.errors.billing.errors import DuplicatePurchaseEventError
from components.infrastructure.stores.mysql.repositories.purchase_event import (
    PurchaseEventRepository,
)


def make_event() -> PurchaseEvent:
    return PurchaseEvent(
        event_id="evt-1",
        user_id="user-1",
        product_id="credits_50",
        credits=50,
    )


def make_session(error: IntegrityError) -> AsyncSession:
    session = MagicMock()
    session.flush = AsyncMock(side_effect=error)
    return cast(AsyncSession, session)


async def test_translates_event_id_unique_violation() -> None:
    error = IntegrityError(
        "INSERT",
        {},
        Exception(
            1062,
            "Duplicate entry 'evt-1' for key "
            "'purchase_events.uq_purchase_events_event_id'",
        ),
    )
    repository = PurchaseEventRepository(make_session(error))

    with pytest.raises(DuplicatePurchaseEventError):
        await repository.add(make_event())


async def test_does_not_translate_other_integrity_violation() -> None:
    error = IntegrityError(
        "INSERT",
        {},
        Exception(1062, "Duplicate entry for key 'some_other_constraint'"),
    )
    repository = PurchaseEventRepository(make_session(error))

    with pytest.raises(IntegrityError) as raised:
        await repository.add(make_event())

    assert raised.value is error
