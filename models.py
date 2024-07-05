######IMPORTS########
from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

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
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    media_filename = db.Column(db.String(100), nullable=True)
    author = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    reactions = db.relationship("Reaction", backref="post", lazy="dynamic")
    tags = db.relationship(
        "Tag", secondary=post_tags, backref=db.backref("posts", lazy="dynamic")
    )

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


# Create Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    author = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Comment('{self.content}', '{self.date_posted}')"


# Create User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    avatar = db.Column(db.String(150), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    social_media = db.Column(db.String(500), nullable=True)
    role = db.Column(db.String(50), nullable=False, default="user")

    def is_admin(self):
        return self.role == "admin"

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', {self.role})"


# Create Media Model
class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    filetype = db.Column(db.String(20), nullable=False)
    date_uploaded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Media('{self.filename}', '{self.filetype}', '{self.date_uploaded}')"


# Create Tag Model
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<Tag {self.name}>"


# Create Reaction Model
class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    reaction = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"Reaction('{self.user_id}', '{self.post_id}', '{self.reaction}')"
