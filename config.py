import os

from dotenv import load_dotenv
from redis import Redis

# Load environment variables from .env file
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "static/uploads"
    )
    PROFILE_PICS_FOLDER = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "static/profile_pics"
    )
    MAX_CONTENT_PATH = 50 * 1024 * 1024  # 50 MB max file size
    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "tiff",
        "tif",
        "svg",
        "mp4",
        "avi",
        "avchd",
        "mov",
        "flv",
        "wmv",
        "mp3",
        "m4a",
        "wav",
        "pdf",
        "txt",
        "html",
        "xls",
        "xlsx",
        "doc",
        "docs",
    }

    # Cache configuration
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.getenv("REDIS_URL")
    CACHE_DEFAULT_TIMEOUT = 300

    # Rate limiting configuration
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL")

    # Session configuration
    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

    # reCAPTCHA configuration
    RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")
    RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

    @staticmethod
    def init_app(app):
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            app.config["SESSION_REDIS"] = Redis.from_url(redis_url)
