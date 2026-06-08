"""fix algorithm_metrics schema

Revision ID: 0002_algorithm_metrics
Revises: 0001_initial
Create Date: 2026-06-08 15:30:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_algorithm_metrics"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("algorithm_metrics")}
    indexes = {index["name"] for index in inspector.get_indexes("algorithm_metrics")}

    if "created_at" in columns and "recorded_at" not in columns:
        with op.batch_alter_table("algorithm_metrics") as batch_op:
            batch_op.alter_column(
                "created_at",
                new_column_name="recorded_at",
                existing_type=sa.DateTime(timezone=True),
                existing_nullable=False,
                existing_server_default=sa.func.now(),
            )

    if bind.dialect.name != "sqlite":
        op.alter_column(
            "algorithm_metrics",
            "id",
            existing_type=sa.Integer(),
            type_=sa.BigInteger(),
            existing_nullable=False,
            autoincrement=True,
        )

    if "ix_algorithm_metrics_operation" not in indexes:
        op.create_index("ix_algorithm_metrics_operation", "algorithm_metrics", ["operation"])
    if "ix_algorithm_metrics_recorded_at" not in indexes:
        op.create_index("ix_algorithm_metrics_recorded_at", "algorithm_metrics", ["recorded_at"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("algorithm_metrics")}
    indexes = {index["name"] for index in inspector.get_indexes("algorithm_metrics")}

    if "ix_algorithm_metrics_recorded_at" in indexes:
        op.drop_index("ix_algorithm_metrics_recorded_at", table_name="algorithm_metrics")
    if "ix_algorithm_metrics_operation" in indexes:
        op.drop_index("ix_algorithm_metrics_operation", table_name="algorithm_metrics")

    if bind.dialect.name != "sqlite":
        op.alter_column(
            "algorithm_metrics",
            "id",
            existing_type=sa.BigInteger(),
            type_=sa.Integer(),
            existing_nullable=False,
            autoincrement=True,
        )

    if "recorded_at" in columns and "created_at" not in columns:
        with op.batch_alter_table("algorithm_metrics") as batch_op:
            batch_op.alter_column(
                "recorded_at",
                new_column_name="created_at",
                existing_type=sa.DateTime(timezone=True),
                existing_nullable=False,
                existing_server_default=sa.func.now(),
            )
