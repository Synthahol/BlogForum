"""Adjust foreign key constraints to cascade deletes

Revision ID: 050dff5a6573
Revises: 6bbafb875f35
Create Date: 2024-07-29 14:03:56.539691

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "050dff5a6573"
down_revision = "6bbafb875f35"
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing constraints
    op.drop_constraint("post_tags_post_id_fkey", "post_tags", type_="foreignkey")
    op.drop_constraint("post_tags_tag_id_fkey", "post_tags", type_="foreignkey")

    # Create new constraints with cascading deletes
    op.create_foreign_key(
        "post_tags_post_id_fkey",
        "post_tags",
        "post",
        ["post_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "post_tags_tag_id_fkey",
        "post_tags",
        "tag",
        ["tag_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    # Drop cascading constraints
    op.drop_constraint("post_tags_post_id_fkey", "post_tags", type_="foreignkey")
    op.drop_constraint("post_tags_tag_id_fkey", "post_tags", type_="foreignkey")

    # Re-create original constraints
    op.create_foreign_key(
        "post_tags_post_id_fkey",
        "post_tags",
        "post",
        ["post_id"],
        ["id"],
        ondelete="NO ACTION",
    )
    op.create_foreign_key(
        "post_tags_tag_id_fkey",
        "post_tags",
        "tag",
        ["tag_id"],
        ["id"],
        ondelete="NO ACTION",
    )
