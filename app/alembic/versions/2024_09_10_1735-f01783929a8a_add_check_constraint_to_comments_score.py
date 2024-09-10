"""add_check_constraint_to_comments_score

Revision ID: f01783929a8a
Revises: b65919a0ff75
Create Date: 2024-09-10 17:35:02.055914

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f01783929a8a"
down_revision: Union[str, None] = "b65919a0ff75"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        constraint_name="ScoreRestriction",
        table_name="comments",
        condition="score >= 1 AND score <=10",
    )


def downgrade() -> None:
    op.drop_constraint(
        constraint_name="ScoreRestriction",
        table_name="comments",
        type_="check",
    )
