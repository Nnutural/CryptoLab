"""initial schema — users, key_store, operation_logs, algorithm_metrics

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-06 00:00:00

Creates the four core tables described in design doc §4.3 plus the
append-only trigger on operation_logs (no UPDATE / DELETE permitted).
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ----- users -----
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(64), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("salt", sa.LargeBinary(), nullable=False),
        sa.Column("role", sa.String(16), nullable=False, server_default="user"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    # ----- key_store -----
    op.create_table(
        "key_store",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("key_type", sa.String(16), nullable=False),
        sa.Column("algorithm", sa.String(32), nullable=False),
        sa.Column("key_material_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("iv", sa.LargeBinary(), nullable=False),
        sa.Column("auth_tag", sa.LargeBinary(), nullable=False),
        sa.Column("label", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_key_store_user_id", "key_store", ["user_id"])
    op.create_index("ix_key_store_deleted_at", "key_store", ["deleted_at"])

    # ----- operation_logs -----
    op.create_table(
        "operation_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("trace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("operation", sa.String(64), nullable=False),
        sa.Column("algorithm", sa.String(32), nullable=True),
        sa.Column("key_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("input_hash", sa.String(64), nullable=True),
        sa.Column("output_hash", sa.String(64), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Double(), nullable=False),
        sa.Column("client_ip", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_operation_logs_trace_id", "operation_logs", ["trace_id"])
    op.create_index("ix_operation_logs_user_id", "operation_logs", ["user_id"])
    op.create_index("ix_operation_logs_operation", "operation_logs", ["operation"])
    op.create_index("ix_operation_logs_algorithm", "operation_logs", ["algorithm"])
    op.create_index("ix_operation_logs_created_at", "operation_logs", ["created_at"])

    # Append-only trigger: forbid UPDATE / DELETE on operation_logs.
    # Enforces design doc §4.1 ("不可变审计").
    op.execute(
        """
        CREATE OR REPLACE FUNCTION operation_logs_immutable()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'operation_logs is append-only; % is forbidden', TG_OP;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER operation_logs_no_update
        BEFORE UPDATE OR DELETE ON operation_logs
        FOR EACH ROW EXECUTE FUNCTION operation_logs_immutable();
        """
    )

    # ----- algorithm_metrics -----
    op.create_table(
        "algorithm_metrics",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("algorithm", sa.String(32), nullable=False),
        sa.Column("data_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("operation", sa.String(32), nullable=False),
        sa.Column("duration_ns", sa.BigInteger(), nullable=False),
        sa.Column("memory_kb", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_algorithm_metrics_algorithm", "algorithm_metrics", ["algorithm"])


def downgrade() -> None:
    op.drop_index("ix_algorithm_metrics_algorithm", table_name="algorithm_metrics")
    op.drop_table("algorithm_metrics")

    op.execute("DROP TRIGGER IF EXISTS operation_logs_no_update ON operation_logs;")
    op.execute("DROP FUNCTION IF EXISTS operation_logs_immutable();")
    op.drop_index("ix_operation_logs_created_at", table_name="operation_logs")
    op.drop_index("ix_operation_logs_algorithm", table_name="operation_logs")
    op.drop_index("ix_operation_logs_operation", table_name="operation_logs")
    op.drop_index("ix_operation_logs_user_id", table_name="operation_logs")
    op.drop_index("ix_operation_logs_trace_id", table_name="operation_logs")
    op.drop_table("operation_logs")

    op.drop_index("ix_key_store_deleted_at", table_name="key_store")
    op.drop_index("ix_key_store_user_id", table_name="key_store")
    op.drop_table("key_store")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
