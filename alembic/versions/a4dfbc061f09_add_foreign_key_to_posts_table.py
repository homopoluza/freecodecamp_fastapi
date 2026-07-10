"""add foreign key to posts table

Revision ID: a4dfbc061f09
Revises: 7092637578de
Create Date: 2026-07-10 19:57:14.392289

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4dfbc061f09'
down_revision: Union[str, Sequence[str], None] = '7092637578de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("posts", sa.Column("user_id", sa.Integer, nullable=False))
    op.create_foreign_key(
        constraint_name="posts_users_fk",
        source_table="posts",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
        ondelete="CASCADE"
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
    "posts_users_fk",
    table_name="posts",
    type_="foreignkey"
    )
    op.drop_column("posts", "user_id")
    pass
