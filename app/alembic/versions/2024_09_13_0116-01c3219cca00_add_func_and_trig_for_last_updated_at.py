"""add_func_and_trig_for_last_updated_at

Revision ID: 01c3219cca00
Revises: a3c98efde516
Create Date: 2024-09-13 01:16:28.732597

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = "01c3219cca00"
down_revision: Union[str, None] = "a3c98efde516"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        text(
            """
            CREATE OR REPLACE FUNCTION update_last_updated_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.last_updated_at = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """
        )
    )

    op.execute(
        text(
            """
            CREATE TRIGGER last_updated_trigger
            BEFORE UPDATE ON articles
            FOR EACH ROW
            EXECUTE FUNCTION update_last_updated_column();
            """
        )
    )

    op.execute(
        text(
            """
            CREATE TRIGGER last_updated_trigger
            BEFORE UPDATE ON comments
            FOR EACH ROW
            EXECUTE FUNCTION update_last_updated_column();
            """
        )
    )


def downgrade() -> None:
    op.execute(
        text(
            """
            DROP TRIGGER IF EXISTS last_updated_trigger ON comments;
            """
        )
    )
    op.execute(
        text(
            """
            DROP TRIGGER IF EXISTS last_updated_trigger ON articles;
            """
        )
    )
    op.execute(
        text(
            """
            DROP FUNCTION IF EXISTS update_last_updated_column;
            """
        )
    )
