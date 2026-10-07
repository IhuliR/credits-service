"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-01 12:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_balances",
        sa.Column("user_id", sa.String(64), primary_key=True),
        sa.Column("balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "generations",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("cost", sa.Integer(), nullable=False),
        sa.Column("result_url", sa.String(512), nullable=True),
        sa.Column("error", sa.String(512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_generations_user_id", "generations", ["user_id"])
    op.create_index("ix_generations_status", "generations", ["status"])

    op.create_table(
        "purchase_events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("event_id", sa.String(128), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("product_id", sa.String(128), nullable=False),
        sa.Column("credits", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_purchase_events_event_id", "purchase_events", ["event_id"])

    op.create_table(
        "balance_transactions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("reference_id", sa.String(128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_balance_transactions_user_id",
        "balance_transactions",
        ["user_id"],
    )
    op.create_index(
        "ix_balance_transactions_kind_reference",
        "balance_transactions",
        ["kind", "reference_id"],
    )


def downgrade() -> None:
    op.drop_table("balance_transactions")
    op.drop_table("purchase_events")
    op.drop_table("generations")
    op.drop_table("user_balances")
