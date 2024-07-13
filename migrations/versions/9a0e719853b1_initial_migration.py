import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "9a0e719853b1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Get the connection and the inspector
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Check if the 'post' table already exists
    if "post" not in inspector.get_table_names():
        op.create_table(
            "post",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=100), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("author", sa.String(length=100), nullable=False),
            sa.Column("date_posted", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    # Check if the 'user' table already exists
    if "user" not in inspector.get_table_names():
        op.create_table(
            "user",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("username", sa.String(length=150), nullable=False),
            sa.Column("password", sa.String(length=150), nullable=False),
            sa.Column("email", sa.String(length=150), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
            sa.UniqueConstraint("email", name="uq_user_email"),
            sa.UniqueConstraint("username"),
        )


def downgrade():
    # Drop tables if they exist
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    if "user" in inspector.get_table_names():
        op.drop_table("user")

    if "post" in inspector.get_table_names():
        op.drop_table("post")
