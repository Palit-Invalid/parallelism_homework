"""add_event_views

Revision ID: f2814e0ffa40
Revises: 8ab9b67eb978
Create Date: 2026-07-22 09:57:30.225064
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f2814e0ffa40"
down_revision: Union[str, None] = "8ab9b67eb978"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "event_views",
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("views_count", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
        ),
        sa.PrimaryKeyConstraint("event_id"),
    )


def downgrade() -> None:
    op.drop_table("event_views")
