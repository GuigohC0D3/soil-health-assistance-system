"""Add teor_argila column to analises_solo

Revision ID: 002
Revises: 001
Create Date: 2026-04-14 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "analises_solo",
        sa.Column("teor_argila", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("analises_solo", "teor_argila")
