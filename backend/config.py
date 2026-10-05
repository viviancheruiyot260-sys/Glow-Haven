import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)


def _env_bool(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).lower() in ("1", "true", "yes")


def _build_mysql_uri() -> str:
    user = os.getenv("MYSQL_USER", "root")
    password = quote_plus(os.getenv("MYSQL_PASSWORD", ""))
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    database = os.getenv("MYSQL_DATABASE", "glow_haven")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


def _resolve_database_uri() -> str:
    explicit_uri = os.getenv("DATABASE_URI")
    if explicit_uri:
        return explicit_uri
    if _env_bool("USE_SQLITE", "0"):
        return f"sqlite:///{ROOT_DIR / 'glow_haven.db'}"
    return _build_mysql_uri()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)

    USE_SQLITE = _env_bool("USE_SQLITE", "0")

    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "glow_haven")

    SQLALCHEMY_DATABASE_URI = _resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    FRONTEND_DIR = ROOT_DIR / "frontend" / "dist"

    MPESA_ENV = os.getenv("MPESA_ENV", "sandbox").lower()
    MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "").strip()
    MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "").strip()
    _mpesa_shortcode = os.getenv("MPESA_SHORTCODE", "").strip()
    MPESA_SHORTCODE = _mpesa_shortcode or ("174379" if MPESA_ENV == "sandbox" else "")
    MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "").strip()
    MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "").strip()

    _cors_raw = os.getenv("CORS_ORIGINS", "*").strip()
    CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()] or ["*"]

    @classmethod
    def database_backend(cls) -> str:
        if cls.USE_SQLITE or cls.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
            return "sqlite"
        return "mysql"
