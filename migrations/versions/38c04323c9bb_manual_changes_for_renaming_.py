from alembic import op
from sqlalchemy.engine.reflection import Inspector

# Revision identifiers, used by Alembic.
revision = "38c04323c9bb"
down_revision = "ee4bbaebb997"
branch_labels = None
depends_on = None


def upgrade():
    # Perform upgrade operations
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Get the list of foreign keys on the 'post' table
    foreign_keys = inspector.get_foreign_keys("post")
    fk_names = [fk["name"] for fk in foreign_keys]

    # Check if the foreign key constraint exists before dropping it
    if "fk_post_user_id_user" in fk_names:
        with op.batch_alter_table("post") as batch_op:
            batch_op.drop_constraint("fk_post_user_id_user", type_="foreignkey")


def downgrade():
    # Perform downgrade operations
    with op.batch_alter_table("post") as batch_op:
        batch_op.create_foreign_key("fk_post_user_id_user", "user", ["user_id"], ["id"])
