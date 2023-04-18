"""Restructured revision table

Revision ID: 1bda0f0b5860
Revises: 93a96fad9c69
Create Date: 2023-04-18 00:11:58.099341

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1bda0f0b5860"
down_revision = "93a96fad9c69"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "prompts", sa.Column("current_revision_id", sa.Integer(), nullable=True)
    )
    op.create_index(
        op.f("ix_prompts_current_revision_id"),
        "prompts",
        ["current_revision_id"],
        unique=False,
    )
    op.create_foreign_key(
        None, "prompts", "prompts_revisions", ["current_revision_id"], ["id"]
    )
    op.drop_index("ix_prompts_versions_prompt_id", table_name="prompts_revisions")
    op.drop_constraint(
        "prompts_versions_prompt_id_fkey", "prompts_revisions", type_="foreignkey"
    )
    op.drop_column("prompts_revisions", "prompt_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "prompts_revisions",
        sa.Column("prompt_id", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.create_foreign_key(
        "prompts_versions_prompt_id_fkey",
        "prompts_revisions",
        "prompts",
        ["prompt_id"],
        ["id"],
    )
    op.create_index(
        "ix_prompts_versions_prompt_id",
        "prompts_revisions",
        ["prompt_id"],
        unique=False,
    )
    op.drop_constraint(None, "prompts", type_="foreignkey")
    op.drop_index(op.f("ix_prompts_current_revision_id"), table_name="prompts")
    op.drop_column("prompts", "current_revision_id")
    # ### end Alembic commands ###
