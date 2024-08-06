import os

from dotenv import load_dotenv
from redis import Redis

# Load environment variables from .env file
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PROFILE_PICS_FOLDER = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "static/profile_pics"
    )
    UPLOAD_FOLDER = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "static/uploads"
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
        "bmp",
        "webp",
        "ico",
        "mp4",
        "avi",
        "avchd",
        "mov",
        "flv",
        "wmv",
        "mkv",
        "mp3",
        "m4a",
        "wav",
        "ogg",
        "flac",
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
        "zip",
        "tar",
        "gz",
        "rar",
        "7z",
        "bz2",
    }

    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.getenv("REDIS_URL")
    CACHE_DEFAULT_TIMEOUT = 300

    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL")

    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

    RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_SITE_KEY")
    RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

    @staticmethod
    def init_app(app):
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            app.config["SESSION_REDIS"] = Redis.from_url(redis_url)


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL")


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    print(f"Using ProductionConfig with DATABASE_URL: {SQLALCHEMY_DATABASE_URI}")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}

current_env = os.getenv(
    "FLASK_ENV", "development"
).strip()  # Ensure no extra spaces or comments
current_config = config[current_env]
print(f"Current environment: {current_env}")
print(f"DATABASE_URL: {current_config.SQLALCHEMY_DATABASE_URI}")
