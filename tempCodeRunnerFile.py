import logging
import os
import re
from functools import wraps
from logging.handlers import RotatingFileHandler

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
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

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
from models import Comment, Post, Reaction, Tag, User, db
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

############## CONFIGURATIONS and INITIALIZATIONS ###############

# Load environment variables
load_dotenv()

# Create Flask instance and configure it
app = Flask(__name__)
app.config.from_object("config.Config")

# Initialize extensions
cache = Cache(app)
bcrypt = Bcrypt(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=app.config["RATELIMIT_STORAGE_URL"],
)
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login"

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


with app.app_context():
    db.create_all()


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
