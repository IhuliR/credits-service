"""make purchase event id unique

Revision ID: 0002_unique_purchase_event_id
Revises: 0001_initial
Create Date: 2026-10-08 00:00:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002_unique_purchase_event_id"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("ix_purchase_events_event_id", table_name="purchase_events")
    op.create_unique_constraint(
        "uq_purchase_events_event_id",
        "purchase_events",
        ["event_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_purchase_events_event_id",
        "purchase_events",
        type_="unique",
    )
    op.create_index(
        "ix_purchase_events_event_id",
        "purchase_events",
        ["event_id"],
        unique=False,
    )
