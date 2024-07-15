"""add autoincrement=True to models

Revision ID: b4137fcba888
Revises: eedda74ffed0
Create Date: 2024-07-15 17:19:15.324537

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b4137fcba888"
down_revision = "eedda74ffed0"
branch_labels = None
depends_on = None


def upgrade():
    # Ensure primary key constraints are added to tables
    op.create_primary_key("pk_post", "post", ["id"])
    op.create_primary_key("pk_user", "user", ["id"])
    op.create_primary_key("pk_tag", "tag", ["id"])
    op.create_primary_key("pk_comment", "comment", ["id"])
    op.create_primary_key("pk_media", "media", ["id"])
    op.create_primary_key("pk_reaction", "reaction", ["id"])

    with op.batch_alter_table("comment", schema=None) as batch_op:
        batch_op.alter_column(
            "id", existing_type=sa.INTEGER(), nullable=False, autoincrement=True
        )
        batch_op.alter_column("content", existing_type=sa.TEXT(), nullable=False)
        batch_op.alter_column(
            "date_posted", existing_type=postgresql.TIMESTAMP(), nullable=False
        )
        batch_op.alter_column("post_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("user_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.create_foreign_key("fk_comment_post_id", "post", ["post_id"], ["id"])
        batch_op.create_foreign_key("fk_comment_user_id", "user", ["user_id"], ["id"])

    with op.batch_alter_table("media", schema=None) as batch_op:
        batch_op.alter_column(
            "id", existing_type=sa.INTEGER(), nullable=False, autoincrement=True
        )
        batch_op.alter_column(
            "filename", existing_type=sa.VARCHAR(length=100), nullable=False
        )
        batch_op.alter_column(
            "filetype", existing_type=sa.VARCHAR(length=20), nullable=False
        )
        batch_op.alter_column(
            "date_uploaded", existing_type=postgresql.TIMESTAMP(), nullable=False
        )
        batch_op.alter_column("user_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.create_foreign_key("fk_media_user_id", "user", ["user_id"], ["id"])

    with op.batch_alter_table("post", schema=None) as batch_op:
        batch_op.alter_column(
            "id", existing_type=sa.INTEGER(), nullable=False, autoincrement=True
        )
        batch_op.alter_column(
            "title", existing_type=sa.VARCHAR(length=100), nullable=False
        )
        batch_op.alter_column(
            "date_posted", existing_type=postgresql.TIMESTAMP(), nullable=False
        )
        batch_op.alter_column("content", existing_type=sa.TEXT(), nullable=False)
        batch_op.alter_column("user_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.create_foreign_key("fk_post_user_id", "user", ["user_id"], ["id"])

    with op.batch_alter_table("post_tags", schema=None) as batch_op:
        batch_op.alter_column("post_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("tag_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.drop_index("sqlite_autoindex_post_tags_1")
        batch_op.create_foreign_key("fk_post_tags_post_id", "post", ["post_id"], ["id"])
        batch_op.create_foreign_key("fk_post_tags_tag_id", "tag", ["tag_id"], ["id"])

    with op.batch_alter_table("reaction", schema=None) as batch_op:
        batch_op.alter_column(
            "id", existing_type=sa.INTEGER(), nullable=False, autoincrement=True
        )
        batch_op.alter_column("user_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("post_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column(
            "reaction", existing_type=sa.VARCHAR(length=10), nullable=False
        )
        batch_op.create_foreign_key("fk_reaction_post_id", "post", ["post_id"], ["id"])
        batch_op.create_foreign_key("fk_reaction_user_id", "user", ["user_id"], ["id"])

    with op.batch_alter_table("tag", schema=None) as batch_op:
        batch_op.alter_column(
            "id", existing_type=sa.INTEGER(), nullable=False, autoincrement=True
        )
        batch_op.alter_column(
            "name", existing_type=sa.VARCHAR(length=30), nullable=False
        )
        batch_op.alter_column(
            "slug", existing_type=sa.VARCHAR(length=50), nullable=False
        )
        batch_op.drop_index("sqlite_autoindex_tag_1")
        batch_op.drop_index("sqlite_autoindex_tag_2")
        batch_op.create_unique_constraint("uq_tag_slug", ["slug"])
        batch_op.create_unique_constraint("uq_tag_name", ["name"])

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column(
            "id", existing_type=sa.INTEGER(), nullable=False, autoincrement=True
        )
        batch_op.alter_column(
            "username", existing_type=sa.VARCHAR(length=150), nullable=False
        )
        batch_op.alter_column(
            "email", existing_type=sa.VARCHAR(length=150), nullable=False
        )
        batch_op.alter_column(
            "password",
            existing_type=sa.VARCHAR(length=255),
            type_=sa.String(length=255),  # Ensure the correct length
            nullable=False,
        )
        batch_op.alter_column(
            "role", existing_type=sa.VARCHAR(length=50), nullable=False
        )
        batch_op.drop_index("sqlite_autoindex_user_1")
        batch_op.drop_index("sqlite_autoindex_user_2")
        batch_op.create_unique_constraint("uq_user_username", ["username"])
        batch_op.create_unique_constraint("uq_user_email", ["email"])

    # ### end Alembic commands ###


def downgrade():
    # Ensure primary key constraints are removed from tables
    op.drop_constraint("pk_post", "post", type_="primary")
    op.drop_constraint("pk_user", "user", type_="primary")
    op.drop_constraint("pk_tag", "tag", type_="primary")
    op.drop_constraint("pk_comment", "comment", type_="primary")
    op.drop_constraint("pk_media", "media", type_="primary")
    op.drop_constraint("pk_reaction", "reaction", type_="primary")

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_constraint("uq_user_email", type_="unique")
        batch_op.drop_constraint("uq_user_username", type_="unique")
        batch_op.create_index("sqlite_autoindex_user_2", ["username"], unique=False)
        batch_op.create_index("sqlite_autoindex_user_1", ["email"], unique=False)
        batch_op.alter_column(
            "role", existing_type=sa.VARCHAR(length=50), nullable=True
        )
        batch_op.alter_column(
            "password",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=128),
            nullable=True,
        )
        batch_op.alter_column(
            "email", existing_type=sa.VARCHAR(length=150), nullable=True
        )
        batch_op.alter_column(
            "username", existing_type=sa.VARCHAR(length=150), nullable=True
        )
        batch_op.alter_column(
            "id", existing_type=sa.INTEGER(), nullable=True, autoincrement=True
        )

    with op.batch_alter_table("tag", schema=None) as batch_op:
        batch_op.drop_constraint("uq_tag_name", type_="unique")
        batch_op.drop_constraint("uq_tag_slug", type_="unique")
        batch_op.create_index("sqlite_autoindex_tag_2", ["slug"], unique=False)
        batch_op.create_index("sqlite_autoindex_tag_1", ["name"], unique=False)
        batch_op.alter_column(
            "slug", existing_type=sa.VARCHAR(length=50), nullable=True
        )
        batch_op.alter_column(
            "name", existing_type=sa.VARCHAR(length=30), nullable=True
        )
        batch_op.alter_column(
            "id", existing_type=sa.INTEGER(), nullable=True, autoincrement=True
        )

    with op.batch_alter_table("reaction", schema=None) as batch_op:
        batch_op.drop_constraint("fk_reaction_user_id", type_="foreignkey")
        batch_op.drop_constraint("fk_reaction_post_id", type_="foreignkey")
        batch_op.alter_column(
            "reaction", existing_type=sa.VARCHAR(length=10), nullable=True
        )
        batch_op.alter_column("post_id", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("user_id", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column(
            "id", existing_type=sa.INTEGER(), nullable=True, autoincrement=True
        )

    with op.batch_alter_table("post_tags", schema=None) as batch_op:
        batch_op.drop_constraint("fk_post_tags_tag_id", type_="foreignkey")
        batch_op.drop_constraint("fk_post_tags_post_id", type_="foreignkey")
        batch_op.create_index(
            "sqlite_autoindex_post_tags_1", ["post_id", "tag_id"], unique=False
        )
        batch_op.alter_column("tag_id", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("post_id", existing_type=sa.INTEGER(), nullable=True)

    with op.batch_alter_table("post", schema=None) as batch_op:
        batch_op.drop_constraint("fk_post_user_id", type_="foreignkey")
        batch_op.alter_column("user_id", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("content", existing_type=sa.TEXT(), nullable=True)
        batch_op.alter_column(
            "date_posted", existing_type=postgresql.TIMESTAMP(), nullable=True
        )
        batch_op.alter_column(
            "title", existing_type=sa.VARCHAR(length=100), nullable=True
        )
        batch_op.alter_column(
            "id", existing_type=sa.INTEGER(), nullable=True, autoincrement=True
        )

    with op.batch_alter_table("media", schema=None) as batch_op:
        batch_op.drop_constraint("fk_media_user_id", type_="foreignkey")
        batch_op.alter_column("user_id", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column(
            "date_uploaded", existing_type=postgresql.TIMESTAMP(), nullable=True
        )
        batch_op.alter_column(
            "filetype", existing_type=sa.VARCHAR(length=20), nullable=True
        )
        batch_op.alter_column(
            "filename", existing_type=sa.VARCHAR(length=100), nullable=True
        )
        batch_op.alter_column(
            "id", existing_type=sa.INTEGER(), nullable=True, autoincrement=True
        )

    with op.batch_alter_table("comment", schema=None) as batch_op:
        batch_op.drop_constraint("fk_comment_post_id", type_="foreignkey")
        batch_op.drop_constraint("fk_comment_user_id", type_="foreignkey")
        batch_op.alter_column("user_id", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("post_id", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column(
            "date_posted", existing_type=postgresql.TIMESTAMP(), nullable=True
        )
        batch_op.alter_column("content", existing_type=sa.TEXT(), nullable=True)
        batch_op.alter_column(
            "id", existing_type=sa.INTEGER(), nullable=True, autoincrement=True
        )

    # ### end Alembic commands ###
