import sqlite3
from pathlib import Path

from app.core.config import DATABASE_PATH


def check_database_connection() -> Path:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS health_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute("INSERT INTO health_checks DEFAULT VALUES")
        connection.commit()

    return DATABASE_PATH
