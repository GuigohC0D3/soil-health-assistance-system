"""Add cor_munsell column to analises_solo

Revision ID: 003
Revises: 002
Create Date: 2026-04-14 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "analises_solo",
        sa.Column("cor_munsell", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("analises_solo", "cor_munsell")
