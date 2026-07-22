"""create_tables

Revision ID: 8ab9b67eb978
Revises:
Create Date: 2026-07-12 16:12:04.152376
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "8ab9b67eb978"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organizer_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("base_price", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_location_id"), "events", ["location_id"], unique=False)
    op.create_index(op.f("ix_events_organizer_id"), "events", ["organizer_id"], unique=False)
    op.create_index(op.f("ix_events_starts_at"), "events", ["starts_at"], unique=False)
    op.create_table(
        "seats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("sector", sa.String(), nullable=False),
        sa.Column("row", sa.Integer(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("location_id", "sector", "row", "number", name="uq_seat_position"),
    )
    op.create_index(op.f("ix_seats_location_id"), "seats", ["location_id"], unique=False)
    op.create_index(op.f("ix_seats_sector"), "seats", ["sector"], unique=False)
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("payment_commission", sa.Integer(), nullable=False),
        sa.Column("protection_price", sa.Integer(), nullable=True),
        sa.Column("with_protection", sa.Boolean(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending_payment", "paid", "cancelled", "expired", name="booking_status"),
            server_default="pending_payment",
            nullable=False,
        ),
        sa.Column("reserved_until", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bookings_event_id"), "bookings", ["event_id"], unique=False)
    op.create_index(op.f("ix_bookings_reserved_until"), "bookings", ["reserved_until"], unique=False)
    op.create_index(op.f("ix_bookings_status"), "bookings", ["status"], unique=False)
    op.create_index(op.f("ix_bookings_user_id"), "bookings", ["user_id"], unique=False)
    op.create_table(
        "event_seats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("seat_id", sa.Integer(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("available", "reserved", "sold", name="seat_status"),
            server_default="available",
            nullable=False,
        ),
        sa.Column("reserved_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("booking_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["booking_id"],
            ["bookings.id"],
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
        ),
        sa.ForeignKeyConstraint(
            ["seat_id"],
            ["seats.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "seat_id", name="uq_event_seat"),
    )
    op.create_index(op.f("ix_event_seats_booking_id"), "event_seats", ["booking_id"], unique=False)
    op.create_index(op.f("ix_event_seats_event_id"), "event_seats", ["event_id"], unique=False)
    op.create_index(op.f("ix_event_seats_seat_id"), "event_seats", ["seat_id"], unique=False)
    op.create_index(op.f("ix_event_seats_status"), "event_seats", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_event_seats_status"), table_name="event_seats")
    op.drop_index(op.f("ix_event_seats_seat_id"), table_name="event_seats")
    op.drop_index(op.f("ix_event_seats_event_id"), table_name="event_seats")
    op.drop_index(op.f("ix_event_seats_booking_id"), table_name="event_seats")
    op.drop_table("event_seats")
    op.drop_index(op.f("ix_bookings_user_id"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_status"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_reserved_until"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_event_id"), table_name="bookings")
    op.drop_table("bookings")
    op.drop_index(op.f("ix_seats_sector"), table_name="seats")
    op.drop_index(op.f("ix_seats_location_id"), table_name="seats")
    op.drop_table("seats")
    op.drop_index(op.f("ix_events_starts_at"), table_name="events")
    op.drop_index(op.f("ix_events_organizer_id"), table_name="events")
    op.drop_index(op.f("ix_events_location_id"), table_name="events")
    op.drop_table("events")
    op.drop_table("locations")

    sa.Enum("pending_payment", "paid", "cancelled", "expired", name="booking_status").drop(op.get_bind())
    sa.Enum("available", "reserved", "sold", name="seat_status").drop(op.get_bind())
