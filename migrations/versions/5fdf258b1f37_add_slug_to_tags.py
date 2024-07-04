"""Add slug to tags

Revision ID: 5fdf258b1f37
Revises: 3262f90847c7
Create Date: 2024-07-04 15:00:00.000000

"""

import re

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5fdf258b1f37"
down_revision = "3262f90847c7"
branch_labels = None
depends_on = None


def slugify(string):
    string = re.sub(r"[^\w\s-]", "", string).strip().lower()
    return re.sub(r"[-\s]+", "-", string)


def upgrade():
    connection = op.get_bind()

    # Check if the new_tag table already exists
    existing_tables = connection.execute(
        sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='new_tag'")
    ).fetchall()

    if not existing_tables:
        # Create a new table with the desired schema
        op.create_table(
            "new_tag",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=30), nullable=False, unique=True),
            sa.Column("slug", sa.String(length=50), nullable=False, unique=True),
        )

        # Copy data from the old table to the new table
        tags = connection.execute(sa.text("SELECT id, name FROM tag")).fetchall()
        for tag in tags:
            slug = slugify(tag[1])  # Use index 1 to get the name from the tuple
            connection.execute(
                sa.text(
                    "INSERT INTO new_tag (id, name, slug) VALUES (:id, :name, :slug)"
                ),
                {
                    "id": tag[0],
                    "name": tag[1],
                    "slug": slug,
                },  # Use index 0 for id, 1 for name
            )

        # Drop the old table
        op.drop_table("tag")

        # Rename the new table to replace the old one
        op.rename_table("new_tag", "tag")


def downgrade():
    connection = op.get_bind()

    # Create the original table schema
    op.create_table(
        "old_tag",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=30), nullable=False, unique=True),
    )

    # Copy data back from the new table to the original schema
    tags = connection.execute(sa.text("SELECT id, name, slug FROM tag")).fetchall()
    for tag in tags:
        connection.execute(
            sa.text("INSERT INTO old_tag (id, name) VALUES (:id, :name)"),
            {"id": tag[0], "name": tag[1]},
        )

    # Drop the new table
    op.drop_table("tag")

    # Rename the old table back to its original name
    op.rename_table("old_tag", "tag")
