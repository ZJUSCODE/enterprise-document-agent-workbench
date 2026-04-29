"""add rag chunks

Revision ID: 0002_rag_chunks
Revises: 0001_initial
Create Date: 2026-04-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_rag_chunks"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "rag_chunks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("file_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("document_type", sa.String(length=64), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["document_files.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["workflow_tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rag_chunks_file_id", "rag_chunks", ["file_id"])
    op.create_index("ix_rag_chunks_task_id", "rag_chunks", ["task_id"])
    op.create_index("ix_rag_chunks_document_type", "rag_chunks", ["document_type"])


def downgrade() -> None:
    op.drop_table("rag_chunks")
