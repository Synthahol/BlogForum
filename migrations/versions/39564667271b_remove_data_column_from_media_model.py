"""Remove data column from Media model

Revision ID: 39564667271b
Revises: 2674e8fa0cda
Create Date: 2024-08-06 12:46:42.363205

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "39564667271b"
down_revision = "2674e8fa0cda"
branch_labels = None
depends_on = None


def upgrade():
    # Remove the `data` column from the `media` table
    with op.batch_alter_table("media") as batch_op:
        batch_op.drop_column("data")


def downgrade():
    # Add the `data` column back to the `media` table
    with op.batch_alter_table("media") as batch_op:
        batch_op.add_column(sa.Column("data", postgresql.BYTEA(), nullable=False))
