import logging
import os
import re
from functools import wraps
from io import BytesIO
from logging.handlers import RotatingFileHandler

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_migrate import Migrate
from flask_wtf.csrf import generate_csrf
from redis import Redis
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from config import config
from extensions import db
from forms import (
    ChangePasswordForm,
    CommentForm,
    LoginForm,
    PostForm,
    ReactionForm,
    RegistrationForm,
    TagForm,
    UpdateProfileForm,
)
from models import Comment, Media, Post, Reaction, Tag, User
from utils import (
    allowed_file,
    delete_media_file,
    sanitize_and_render_markdown,
    save_media,
)

# Load environment variables
load_dotenv()

# Get the current environment
current_env = os.getenv("FLASK_ENV", "development")

# Create Flask instance and configure it
app = Flask(__name__)
app.config.from_object(config[current_env])
config[current_env].init_app(app)

# Initialize extensions
cache = Cache(app)
bcrypt = Bcrypt(app)
limiter = Limiter(
    key_func=get_remote_address, storage_uri=app.config["RATELIMIT_STORAGE_URL"]
)
limiter.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Initialize the SQLAlchemy instance
db.init_app(app)

# Ensure profile pics folder exists
os.makedirs(app.config["PROFILE_PICS_FOLDER"], exist_ok=True)

# Clear existing logs
if not app.debug:
    log_dir = "logs"
    if os.path.exists(log_dir):
        for log_file in os.listdir(log_dir):
            file_path = os.path.join(log_dir, log_file)
            if os.path.isfile(file_path):
                open(file_path, "w").close()

    # Configure logging
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler("logs/blog.log", maxBytes=10240, backupCount=10)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Blog startup")

# Test the database connection
try:
    from sqlalchemy import create_engine

    DATABASE_URI = app.config["SQLALCHEMY_DATABASE_URI"]
    engine = create_engine(DATABASE_URI)
    connection = engine.connect()
    print("Connection to the database was successful.")
    connection.close()
except Exception as e:
    print(f"Error connecting to the database: {e}")
    logging.error(f"Error connecting to the database: {e}")

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error creating tables: {e}")
        logging.error(f"Error creating tables: {e}")

# Conditionally test Redis connection
redis_url = app.config.get("CACHE_REDIS_URL")
if redis_url:
    try:
        redis_client = Redis.from_url(redis_url)
        redis_client.ping()  # Simple ping to test connection
        print("Connected to Redis successfully.")
        logging.info("Connected to Redis successfully.")
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        logging.error(f"Error connecting to Redis: {e}")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def slugify(string):
    return re.sub(r"[-\s]+", "-", re.sub(r"[^\w\s-]", "", string).strip().lower())


def generate_unique_slug(name):
    slug = slugify(name)
    original_slug = slug
    count = 1
    while Tag.query.filter_by(slug=slug).first():
        slug = f"{original_slug}-{count}"
        count += 1
    return slug


######### ROUTES #############


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part", "danger")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file", "danger")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            media_id = save_media(file, current_user.id)  # Save file to the database

            flash("File successfully uploaded", "success")
            return redirect(url_for("uploaded_file", media_id=media_id))
    return render_template("upload.html")


@app.route("/uploads/<int:media_id>")
def uploaded_file(media_id):
    media = Media.query.get_or_404(media_id)
    return send_file(
        BytesIO(media.file_data),
        attachment_filename=media.filename,
        mimetype=media.filetype,
    )


@app.route("/search")
def search_results():
    query = request.args.get("q")
    results = Post.query.filter(
        (Post.title.ilike(f"%{query}%")) | (Post.content.ilike(f"%{query}%"))
    ).all()
    return render_template("search_results.html", query=query, results=results)


@app.route("/", methods=["GET"])
@app.route("/page/<int:page>", methods=["GET"])
def home(page=1):
    per_page = 10
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template("home.html", posts=posts)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()

    # Print the site key to verify it's being passed correctly
    print(f"RECAPTCHA_SITE_KEY: {app.config['RECAPTCHA_PUBLIC_KEY']}")

    if form.validate_on_submit():
        recaptcha_response = request.form.get("g-recaptcha-response")

        if not recaptcha_response:
            flash("reCAPTCHA verification failed. Please try again.", "danger")
            return render_template(
                "signup.html", form=form, site_key=app.config["RECAPTCHA_PUBLIC_KEY"]
            )

        data = {
            "secret": app.config["RECAPTCHA_PRIVATE_KEY"],
            "response": recaptcha_response,
        }
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)
        result = r.json()

        if result.get("success"):
            try:
                hashed_password = generate_password_hash(form.password.data)
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    password=hashed_password,
                )
                db.session.add(user)
                db.session.commit()
                flash("Your account has been created!", "success")
                return redirect(url_for("login"))
            except IntegrityError:
                db.session.rollback()
                flash(
                    "An error occurred. It's likely the username or email already exists.",
                    "danger",
                )
        else:
            flash("reCAPTCHA verification failed. Please try again.", "danger")

    return render_template(
        "signup.html", form=form, site_key=app.config["RECAPTCHA_PUBLIC_KEY"]
    )


@app.route("/change_password", methods=["POST", "GET"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.old_password.data):
            flash("Old password is incorrect.", "danger")
        else:
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Your password has been updated!", "success")
            return redirect(url_for("profile"))  # Assuming there is a profile route
    return render_template("change_password.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully.", "success")
            # Clear cache after login
            cache.clear()
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    # Clear cache after logout
    cache.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/new_post", methods=["GET", "POST"])
@login_required
@limiter.limit("10 per minute")
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # Sanitize title and content
        sanitized_title = sanitize_and_render_markdown(form.title.data)
        sanitized_content = sanitize_and_render_markdown(form.content.data)

        # Create the post object
        post = Post(
            title=sanitized_title,
            content=sanitized_content,
            author=current_user,
        )

        # Handle tags
        tag_names = [name.strip() for name in form.tags.data.split(",")]
        tags = []
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if tag is None:
                slug = generate_unique_slug(name)
                tag = Tag(name=name, slug=slug)
                db.session.add(tag)  # Add new tag to session
            tags.append(tag)
        post.tags = tags

        db.session.add(post)  # Add post to session
        db.session.flush()  # Flush to get the post ID

        # Handle media file
        if form.media.data:
            save_media(form.media.data, current_user.id, post.id)

        try:
            db.session.commit()
            # Clear the cache for the home page after a new post is created
            cache.clear()
        except IntegrityError:
            db.session.rollback()
            current_app.logger.error(
                f"Integrity error while creating post: {post.title}"
            )
            flash(
                "An error occurred while creating the post. Please try again.", "danger"
            )
            return redirect(url_for("new_post"))

        current_app.logger.info(f"Post created: {post.title}")

        return redirect(url_for("home"))

    return render_template("add.html", form=form)


@app.route("/post/<int:post_id>", methods=["GET"])
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    sanitized_content = sanitize_and_render_markdown(post.content)
    comment_form = CommentForm()
    reaction_form = ReactionForm()
    reaction_form.post_id.data = post_id  # Explicitly set the post_id
    comments = (
        Comment.query.filter_by(post_id=post.id)
        .order_by(Comment.date_posted.desc())
        .all()
    )
    return render_template(
        "view_post.html",
        title=post.title,
        post=post,
        form=comment_form,
        reaction_form=reaction_form,
        comments=comments,
        content=sanitized_content,
        csrf_token=generate_csrf(),
    )


@app.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        comment = Comment(
            content=comment_form.comment.data,
            author=current_user,
            post_id=post.id,
            user_id=current_user.id,
        )
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been added.", "success")

        # Clear cache for the view_post page
        try:
            cache.delete_memoized(view_post, post_id)
        except Exception as cache_error:
            app.logger.error(f"Error clearing cache for post {post_id}: {cache_error}")

    return redirect(url_for("view_post", post_id=post.id))


@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Check if the current user is the author of the post or an admin
    if current_user.username == post.author.username or current_user.is_admin():
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash("Your post has been updated!", "success")
            return redirect(url_for("view_post", post_id=post.id))

        form.title.data = post.title
        form.content.data = post.content
        return render_template(
            "update.html", title="Update Post", form=form, post_id=post.id
        )
    else:
        flash("You do not have permission to edit this post.", "danger")
        return redirect(url_for("home"))


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.username == post.author.username or current_user.is_admin():
        try:
            # Delete associated media files from filesystem
            for media in post.media:
                delete_media_file(media.filename)

            db.session.delete(post)
            db.session.commit()
            try:
                # Clear cache after deletion
                cache.delete_memoized(view_post, post_id)
                cache.delete_memoized(home)  # Clear the cache for the home page
            except Exception as cache_error:
                app.logger.error(
                    f"Error clearing cache for post {post_id}: {cache_error}"
                )
            flash("Your post has been deleted.", "success")
        except Exception as db_error:
            db.session.rollback()
            app.logger.error(f"Error deleting post {post_id}: {db_error}")
            flash(f"An error occurred: {db_error}", "danger")
    else:
        flash("You do not have permission to delete this post.", "danger")

    return redirect(url_for("home"))


@app.route("/admin/delete_comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    # Check if the current user is the author of the comment or an admin
    if current_user.username == comment.author.username or current_user.is_admin():
        db.session.delete(comment)
        db.session.commit()
        try:
            # Clear cache after deletion
            cache.delete_memoized(view_post, comment.post_id)
        except Exception as cache_error:
            app.logger.error(
                f"Error clearing cache for comment {comment_id}: {cache_error}"
            )
        flash("Comment has been deleted.", "success")
    else:
        flash("You do not have permission to delete this comment.", "danger")

    return redirect(url_for("view_post", post_id=comment.post_id))


@app.route("/profile/<username>", methods=["POST", "GET"])
@login_required
def profile(username):
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.avatar.data:
            avatar_file = secure_filename(form.avatar.data.filename)
            avatar_path = os.path.join(app.config["PROFILE_PICS_FOLDER"], avatar_file)
            form.avatar.data.save(avatar_path)
            current_user.avatar = avatar_file  # Only store the filename, not the path
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash("Your profile has been updated!", "success")
        return redirect(url_for("profile", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.bio.data = current_user.bio

    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).all()
    comments = (
        Comment.query.filter_by(author=user).order_by(Comment.date_posted.desc()).all()
    )
    return render_template(
        "profile.html", user=user, form=form, posts=posts, comments=comments
    )


@app.route("/tag/<slug>")
@cache.cached(timeout=60)
def tag(slug):
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get("page", 1, type=int)
    posts = (
        Post.query.filter(Post.tags.any(Tag.slug == slug))
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=5)
    )
    return render_template("tag.html", tag=tag, posts=posts)


@app.route("/admin/tags", methods=["GET", "POST"])
@login_required
def manage_tags():
    if current_user.role != "admin":
        abort(403)
    tags = Tag.query.all()
    return render_template("admin_tags", tags=tags)


@app.route("/admin/tags/new", methods=["POST", "GET"])
@login_required
def new_tag():
    if current_user.role != "admin":
        abort(403)
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag(name=form.name.data, slug=slugify(form.name.data))
        db.session.add(tag)
        db.session.commit()
        flash("Tag created successfully", "success")
        return redirect(url_for("manage_tags"))
    return render_template("new_tag.html", form=form)


@app.route("/admin/tags/edit/<int:tag_id>", methods=["GET", "POST"])
@login_required
def edit_tag(tag_id):
    if not current_user.is_admin:
        abort(403)
    tag = Tag.query.get_or_404(tag_id)
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        tag.name = form.name.data
        tag.slug = slugify(form.name.data)
        db.session.commit()
        flash("Tag updated successfully", "success")
        return redirect(url_for("manage_tags"))
    elif request.method == "GET":
        form.name.data = tag.name
    return render_template("edit_tag.html", form=form)


@app.route("/admin/tags/delete/<int:tag_id>", methods=["POST"])
@login_required
def delete_tag(tag_id):
    if not current_user.is_admin:
        abort(403)
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    # Clear cache after deletion
    cache.delete_memoized(tag, tag_id)
    flash("Tag deleted successfully", "success")
    return redirect(url_for("manage_tags"))


@app.route("/react", methods=["POST"])
@login_required
@limiter.limit("10 per minute")
def react():
    form = ReactionForm()
    if form.validate_on_submit():
        try:
            post_id = int(form.post_id.data)
        except (ValueError, TypeError):
            post_id = None
            flash("Invalid post ID.", "danger")
            return redirect(url_for("home"))

        existing_reaction = Reaction.query.filter_by(
            user_id=current_user.id, post_id=post_id
        ).first()
        if existing_reaction:
            existing_reaction.reaction = (
                form.reaction_type.data
            )  # Ensure this matches the form field name
        else:
            reaction = Reaction(
                user_id=current_user.id,
                post_id=post_id,
                reaction=form.reaction_type.data,
            )  # Ensure this matches the form field name
            db.session.add(reaction)
        db.session.commit()
        return jsonify(
            status="success",
            likeCount=Reaction.query.filter_by(
                post_id=post_id, reaction="like"
            ).count(),
            dislikeCount=Reaction.query.filter_by(
                post_id=post_id, reaction="dislike"
            ).count(),
        )
    else:
        flash("Failed to process your reaction.", "danger")
        return jsonify(status="error", message=form.errors)


if __name__ == "__main__":
    app.run(debug=False)
