"""add test column to posts table

Revision ID: bcde2265439a
Revises: ba7b921b1db4
Create Date: 2026-07-10 19:40:05.010564

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bcde2265439a'
down_revision: Union[str, Sequence[str], None] = 'ba7b921b1db4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("posts", sa.Column("test", sa.String, nullable=True))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("posts", "test")
    pass
