######### IMPORTS #############
import logging
import os
import re
from functools import wraps
from logging.handlers import RotatingFileHandler

from flask import (
    Flask,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_migrate import Migrate
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from config import Config
from forms import (
    CommentForm,
    LoginForm,
    PostForm,
    RegistrationForm,
    TagForm,
    UpdateProfileForm,
)
from models import Comment, Post, Tag, User, db
from utils import (
    allowed_file,
    read_docx,
    read_ods,
    read_odt,
    read_rtf,
    sanitize_and_render_markdown,
    save_file,
    save_media,
)

##############CONFIGURATIONS ###############

# Main application
app = Flask(__name__)
app.config.from_object(Config)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = "login"

# Configure logging
if not app.debug:
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


########### DEFINE FUNCTIONS ##################


# Define login manager function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Define admin required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


# Define slugify for SEO purposes
def slugify(string):
    string = re.sub(r"[^\w\s-]", "", string).strip().lower()
    return re.sub(r"[-\s]+", "-", string)


######### ROUTES #############


# Pagination routing
@app.route("/", methods=["GET"])
@app.route("/page/<int:page>", methods=["GET"])
def home(page=1):
    per_page = 10
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template("home.html", posts=posts)


# Signup page routing
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created!", "success")
        return redirect(url_for("login"))
    return render_template("signup.html", form=form)


##############Login/Logout###############


# Login Routing
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")
    return render_template("login.html", form=form)


# Logout Route
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


############## ALL POST ROUTINGS ###############


# New_Post routing
@app.route("/new_post", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        filename = None
        if form.media.data:
            filename = save_media(form.media.data)

        # Create the post object
        post = Post(
            title=form.title.data,
            content=form.content.data,
            media_filename=filename,
            author=current_user.username,
        )

        # Handle tags
        tag_names = [name.strip() for name in form.tags.data.split(",")]
        tags = []
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if tag is None:
                tag = Tag(name=name)
                db.session.add(tag)
            tags.append(tag)
        post.tags = tags

        db.session.add(post)
        db.session.commit()

        current_app.logger.info(f"Post created: {post.title}")

        return redirect(url_for("home"))

    return render_template("add.html", form=form)


# Upload_File Routing
@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = save_file(file)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            content = ""
            try:
                if filename.endswith(".docx"):
                    content = read_docx(file_path)
                elif filename.endswith(".odt"):
                    content = read_odt(file_path)
                elif filename.endswith(".ods"):
                    content = read_ods(file_path)
                elif filename.endswith(".rtf"):
                    content = read_rtf(file_path)
            except ImportError as e:
                flash(str(e))
            flash(content)
            return redirect(url_for("upload_file", filename=filename))
    return render_template("upload.html")


# View_Post page routing
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    sanitized_content = sanitize_and_render_markdown(post.content)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to be logged in to comment.", "danger")
            return redirect(url_for("login"))
        comment = Comment(
            content=form.comment.data, author=current_user.username, post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been added.", "success")
        return redirect(url_for("view_post", post_id=post.id))
    comments = (
        Comment.query.filter_by(post_id=post.id)
        .order_by(Comment.date_posted.desc())
        .all()
    )
    return render_template(
        "view_post.html",
        post=post,
        form=form,
        comments=comments,
        content=sanitized_content,
    )


# Update_post routing
@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.username != post.author and not current_user.is_admin():
        flash("You do not have permission to edit this post.", "danger")
        return redirect(url_for("home"))

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


# Delete post routing
@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.username != post.author and not current_user.is_admin():
        flash("You do not have permission to delete this post.", "danger")
        return redirect(url_for("home"))

    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted!", "success")
    return redirect(url_for("home"))


# Comment delete routing
@app.route("/admin/delete_comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user.username != comment.author and not current_user.is_admin():
        flash("You do not have permission to delete this comment.", "danger")
        return redirect(url_for("view_post", post_id=comment.post_id))
    db.session.delete(comment)
    db.session.commit()
    flash("Comment has been deleted.", "success")
    return redirect(url_for("view_post", post_id=comment.post_id))


@app.route("/profile/<username>", methods=["POST", "GET"])
@login_required  # ensure user is logged in
def profile(username):
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.avatar.data:
            avatar_file = secure_filename(form.avatar.data.filename)
            form.avatar.data.save(
                os.path.join(app.config["UPLOAD_FOLDER"], avatar_file)
            )
            current_user.avatar = avatar_file
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        current_user.social_media = form.social_media.data
        db.session.commit()
        flash("Your profile has been updated!", "success")
        return redirect(url_for("profile", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.bio.data = current_user.bio
        form.social_media.data = current_user.social_media

    user = User.query.filter_by(username=username).first_or_404()
    posts = (
        Post.query.filter_by(author=user.username)
        .order_by(Post.date_posted.desc())
        .all()
    )
    comments = (
        Comment.query.filter_by(author=user.username)
        .order_by(Comment.date_posted.desc())
        .all()
    )
    return render_template(
        "profile.html", user=user, form=form, posts=posts, comments=comments
    )


##################TAGGING AND SEO#################


# define tags
@app.route("/tag/<slug>")
def tag(slug):
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get("page", 1, type=int)
    posts = (
        Post.query.filter(Post.tags.any(Tag.slug == slug))
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=5)
    )
    return render_template("tag.html", tag=tag, posts=posts)


# define managing tags routing
@app.route("/admin/tags", methods=["GET", "POST"])
@login_required
def manage_tags():
    if current_user.role != "admin":
        abort(403)
    tags = Tag.query.all()
    return render_template("admin_tags", tags=tags)


# Create new tags
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


# Edit tags
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


# Delete tags
@app.route("/admin/tags/delete/<int:tag_id>", methods=["POST"])
@login_required
def delete_tag(tag_id):
    if not current_user.is_admin:
        abort(403)
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash("Tag deleted successfully", "success")
    return redirect(url_for("manage_tags"))


###############SEND IT################
if __name__ == "__main__":
    app.run(debug=True)
