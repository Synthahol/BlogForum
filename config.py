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
        # Images
        "png",
        "jpg",
        "jpeg",
        "gif",
        "tiff",
        "tif",
        "svg",
        "bmp",
        "webp",
        "ico",
        # Videos
        "mp4",
        "avi",
        "avchd",
        "mov",
        "flv",
        "wmv",
        "mkv",
        # Audio
        "mp3",
        "m4a",
        "wav",
        "ogg",
        "flac",
        # Documents
        "pdf",
        "txt",
        "html",
        "xls",
        "xlsx",
        "doc",
        "docx",
        "odt",
        "ppt",
        "pptx",
        "rtf",
        "md",
        "epub",
        # Compressed
        "zip",
        "tar",
        "gz",
        "rar",
        "7z",
        "bz2",
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
    RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_SITE_KEY")
    RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

    @staticmethod
    def init_app(app):
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            app.config["SESSION_REDIS"] = Redis.from_url(redis_url)


print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
