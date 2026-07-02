from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from app.core.config import DATABASE_PATH
from app.services.excel_store import ensure_excel_tables  # reuse DB directory setup


def ensure_news_tables() -> None:
    ensure_excel_tables()
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS news_articles (
                source_url TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                published_date TEXT NOT NULL,
                department TEXT,
                summary TEXT,
                content TEXT,
                collected_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS news_collection_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_date TEXT NOT NULL,
                collected INTEGER NOT NULL,
                skipped INTEGER NOT NULL,
                failed INTEGER NOT NULL,
                detail_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def save_news_articles(items: list[dict[str, object]], target_date: str) -> tuple[int, int]:
    ensure_news_tables()
    collected = 0
    skipped = 0
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DATABASE_PATH) as connection:
        for item in items:
            exists = connection.execute(
                "SELECT 1 FROM news_articles WHERE source_url = ?",
                (item["source_url"],),
            ).fetchone()
            if exists:
                skipped += 1
                continue
            connection.execute(
                """
                INSERT INTO news_articles (
                    source_url, title, published_date, department, summary, content, collected_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["source_url"],
                    item["title"],
                    item["published_date"],
                    item.get("department"),
                    item.get("summary"),
                    item.get("content"),
                    item.get("collected_at", now),
                    now,
                ),
            )
            collected += 1
        connection.execute(
            """
            INSERT INTO news_collection_jobs (
                target_date, collected, skipped, failed, detail_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (target_date, collected, skipped, 0, json.dumps(items, ensure_ascii=False), now),
        )
        connection.commit()
    return collected, skipped


def list_news_articles(target_date: str | None = None) -> list[dict[str, object]]:
    ensure_news_tables()
    sql = """
        SELECT title, published_date, source_url, department, summary, content, collected_at
        FROM news_articles
    """
    params: list[object] = []
    if target_date:
        sql += " WHERE published_date = ?"
        params.append(target_date)
    sql += " ORDER BY published_date DESC, collected_at DESC"
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(sql, params).fetchall()
    return [
        {
            "title": row[0],
            "published_date": row[1],
            "source_url": row[2],
            "department": row[3],
            "summary": row[4],
            "content": row[5],
            "collected_at": row[6],
        }
        for row in rows
    ]


def list_news_jobs() -> list[dict[str, object]]:
    ensure_news_tables()
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(
            """
            SELECT id, target_date, collected, skipped, failed, created_at
            FROM news_collection_jobs
            ORDER BY id DESC
            """
        ).fetchall()
    return [
        {
            "id": row[0],
            "target_date": row[1],
            "collected": row[2],
            "skipped": row[3],
            "failed": row[4],
            "created_at": row[5],
        }
        for row in rows
    ]
