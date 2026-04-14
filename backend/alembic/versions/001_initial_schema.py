"""Schema inicial

Revision ID: 001
Revises:
Create Date: 2026-04-14 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "papel",
            sa.Enum("produtor", "tecnico", "admin", name="userrole"),
            nullable=False,
            server_default="produtor",
        ),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("criado_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "propriedades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("area_hectares", sa.Float(), nullable=True),
        sa.Column("localizacao", sa.String(length=255), nullable=True),
        sa.Column("cidade", sa.String(length=100), nullable=True),
        sa.Column("estado", sa.String(length=2), nullable=True),
        sa.Column("proprietario_id", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["proprietario_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_propriedades_id"), "propriedades", ["id"], unique=False)

    op.create_table(
        "analises_solo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_amostra", sa.String(length=50), nullable=False),
        sa.Column("data_analise", sa.Date(), nullable=False),
        sa.Column("ph", sa.Float(), nullable=True),
        sa.Column("materia_organica", sa.Float(), nullable=True),
        sa.Column("fosforo", sa.Float(), nullable=True),
        sa.Column("potassio", sa.Float(), nullable=True),
        sa.Column("calcio", sa.Float(), nullable=True),
        sa.Column("magnesio", sa.Float(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("propriedade_id", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["propriedade_id"], ["propriedades.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analises_solo_id"), "analises_solo", ["id"], unique=False)

    op.create_table(
        "recomendacoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column(
            "prioridade",
            sa.Enum("alta", "media", "baixa", name="prioritylevel"),
            nullable=False,
            server_default="media",
        ),
        sa.Column("analise_id", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["analise_id"], ["analises_solo.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recomendacoes_id"), "recomendacoes", ["id"], unique=False)


def downgrade() -> None:
    op.drop_table("recomendacoes")
    op.drop_table("analises_solo")
    op.drop_table("propriedades")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS prioritylevel")
    op.execute("DROP TYPE IF EXISTS userrole")
