import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your_secret_key"
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "postgresql://blogforum_user:bjeFv7tdR85Sp548mhpwjjeK5sHCypVT@dpg-cq9ltedds78s739fi3fg-a.ohio-postgres.render.com:5432/blogforum"
    )
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
    CACHE_REDIS_URL = os.environ.get("REDIS_URL") or "redis://localhost:6379/0"
    CACHE_DEFAULT_TIMEOUT = 300

    # Rate limiting configuration
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL") or "redis://localhost:6379/0"

    # Session configuration
    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = os.environ.get("REDIS_URL") or "redis://localhost:6379/0"
