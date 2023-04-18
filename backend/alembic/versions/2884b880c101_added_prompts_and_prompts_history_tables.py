"""Added prompts and prompts_history tables

Revision ID: 2884b880c101
Revises:
Create Date: 2023-04-17 12:45:09.345557

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2884b880c101"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "prompts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("prompt_text", sa.String(length=4096), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["prompts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_slug_is_active", "prompts", ["slug", "is_active"], unique=False)
    op.create_index(
        op.f("ix_prompts_parent_id"), "prompts", ["parent_id"], unique=False
    )
    op.create_index(op.f("ix_prompts_slug"), "prompts", ["slug"], unique=False)
    op.create_table(
        "prompts_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("prompt_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["prompt_id"],
            ["prompts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_prompts_history_prompt_id"),
        "prompts_history",
        ["prompt_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_prompts_history_prompt_id"), table_name="prompts_history")
    op.drop_table("prompts_history")
    op.drop_index(op.f("ix_prompts_slug"), table_name="prompts")
    op.drop_index(op.f("ix_prompts_parent_id"), table_name="prompts")
    op.drop_index("IX_slug_is_active", table_name="prompts")
    op.drop_table("prompts")
    # ### end Alembic commands ###
