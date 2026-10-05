"""Startup diagnostics for environment and database connectivity."""

import sys

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config import ENV_PATH, Config
from extensions import db


def _checkmark(message: str) -> None:
    prefix = "✓"
    encoding = (sys.stdout.encoding or "").lower()
    if encoding and "utf" not in encoding:
        prefix = "[OK]"
    print(f"{prefix} {message}")


def run_startup_diagnostics(app) -> None:
    if ENV_PATH.is_file():
        _checkmark("Environment loaded")
    else:
        print("⚠ .env file not found — using process environment / defaults")
        _checkmark("Environment loaded")

    backend = Config.database_backend()
    if backend == "mysql":
        _checkmark(
            "MySQL configuration loaded "
            f"(host={Config.MYSQL_HOST}, port={Config.MYSQL_PORT}, "
            f"database={Config.MYSQL_DATABASE}, user={Config.MYSQL_USER})"
        )
    else:
        _checkmark("SQLite configuration loaded (USE_SQLITE=1)")

    with app.app_context():
        try:
            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            raise RuntimeError(
                "Database connection failed. Verify MySQL is running, the glow_haven "
                "database exists, and MYSQL_* values in .env are correct."
            ) from exc

    _checkmark("Database connection successful")
