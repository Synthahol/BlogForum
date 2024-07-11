"""Manual changes for renaming relationships

Revision ID: 38c04323c9bb
Revises: ee4bbaebb997
Create Date: 2024-07-11 17:44:13.014243

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "38c04323c9bb"
down_revision = "ee4bbaebb997"
branch_labels = None
depends_on = None


def upgrade():
    # Rename the foreign key constraints if needed
    # Example for SQLite
    with op.batch_alter_table("post") as batch_op:
        batch_op.drop_constraint("fk_post_user_id_user", type_="foreignkey")
        batch_op.create_foreign_key("fk_post_user_id_user", "user", ["user_id"], ["id"])
    with op.batch_alter_table("comment") as batch_op:
        batch_op.drop_constraint("fk_comment_user_id_user", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_comment_user_id_user", "user", ["user_id"], ["id"]
        )


def downgrade():
    # Reverse the operations in upgrade
    with op.batch_alter_table("post") as batch_op:
        batch_op.drop_constraint("fk_post_user_id_user", type_="foreignkey")
        batch_op.create_foreign_key("fk_post_user_id_user", "user", ["user_id"], ["id"])
    with op.batch_alter_table("comment") as batch_op:
        batch_op.drop_constraint("fk_comment_user_id_user", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_comment_user_id_user", "user", ["user_id"], ["id"]
        )
