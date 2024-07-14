from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index
from werkzeug.security import check_password_hash, generate_password_hash

# Make database connection
db = SQLAlchemy()

# Create a table for many-to-many relationship between posts and tags
post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


# Create Post Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    media_filename = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    author = db.relationship("User", back_populates="posts")
    reactions = db.relationship(
        "Reaction", back_populates="post", lazy="dynamic", cascade="all, delete-orphan"
    )
    tags = db.relationship("Tag", secondary=post_tags, back_populates="tagged_posts")
    comments = db.relationship(
        "Comment", back_populates="post", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


# Create Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    author = db.relationship("User", back_populates="comments")
    post = db.relationship("Post", back_populates="comments")

    def __repr__(self):
        return f"Comment('{self.content}', '{self.date_posted}')"


# Create User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    avatar = db.Column(
        db.String(255), nullable=True, default="static/profile_pics/default.jpg"
    )
    bio = db.Column(db.Text, nullable=True)
    role = db.Column(db.String(50), nullable=False, default="user")
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    posts = db.relationship(
        "Post", back_populates="author", lazy=True, cascade="all, delete-orphan"
    )
    comments = db.relationship(
        "Comment", back_populates="author", lazy=True, cascade="all, delete-orphan"
    )
    media = db.relationship(
        "Media", back_populates="uploader", lazy=True, cascade="all, delete-orphan"
    )
    reactions = db.relationship(
        "Reaction", back_populates="user", lazy=True, cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_username_email", "username", "email"),)

    def is_admin(self):
        return self.role == "admin"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"


# Create Media Model
class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(100), nullable=False)
    filetype = db.Column(db.String(20), nullable=False)
    date_uploaded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    uploader = db.relationship("User", back_populates="media")

    def __repr__(self):
        return f"Media('{self.filename}', '{self.filetype}', '{self.date_uploaded}')"


# Create Tag Model
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)
    tagged_posts = db.relationship("Post", secondary=post_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.name}>"


# Create Reaction Model
class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    reaction = db.Column(db.String(10), nullable=False)
    user = db.relationship("User", back_populates="reactions")
    post = db.relationship("Post", back_populates="reactions")

    def __repr__(self):
        return f"Reaction('{self.user_id}', '{self.post_id}', '{self.reaction}')"
