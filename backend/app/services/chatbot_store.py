from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import DATABASE_PATH, DATA_DIR

CHATBOT_UPLOAD_DIR = DATA_DIR / "chatbot_uploads"


def ensure_chatbot_tables() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHATBOT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chatbot_documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                original_path TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chatbot_chunks (
                chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                embedding_json TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chatbot_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                sources_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def save_uploaded_document(document_id: str, filename: str, file_type: str, source_path: Path) -> None:
    ensure_chatbot_tables()
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO chatbot_documents (
                document_id, filename, file_type, original_path, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (document_id, filename, file_type, str(source_path), "uploaded", now, now),
        )
        connection.commit()


def update_document_status(document_id: str, status: str) -> None:
    ensure_chatbot_tables()
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            "UPDATE chatbot_documents SET status = ?, updated_at = ? WHERE document_id = ?",
            (status, now, document_id),
        )
        connection.commit()


def list_documents() -> list[dict[str, object]]:
    ensure_chatbot_tables()
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(
            """
            SELECT d.document_id, d.filename, d.file_type, d.status, d.created_at, COUNT(c.chunk_id)
            FROM chatbot_documents d
            LEFT JOIN chatbot_chunks c ON c.document_id = d.document_id
            GROUP BY d.document_id, d.filename, d.file_type, d.status, d.created_at
            ORDER BY d.created_at DESC
            """
        ).fetchall()
    return [
        {
            "document_id": row[0],
            "filename": row[1],
            "file_type": row[2],
            "status": row[3],
            "created_at": row[4],
            "chunk_count": row[5],
        }
        for row in rows
    ]


def get_document(document_id: str) -> dict[str, object] | None:
    ensure_chatbot_tables()
    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            """
            SELECT document_id, filename, file_type, original_path, status, created_at, updated_at
            FROM chatbot_documents
            WHERE document_id = ?
            """,
            (document_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "document_id": row[0],
        "filename": row[1],
        "file_type": row[2],
        "original_path": row[3],
        "status": row[4],
        "created_at": row[5],
        "updated_at": row[6],
    }


def save_chunks(document_id: str, chunks: list[dict[str, object]]) -> int:
    ensure_chatbot_tables()
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("DELETE FROM chatbot_chunks WHERE document_id = ?", (document_id,))
        for index, chunk in enumerate(chunks):
            connection.execute(
                """
                INSERT INTO chatbot_chunks (
                    document_id, chunk_index, content, metadata_json, embedding_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    index,
                    str(chunk["content"]),
                    json.dumps(chunk.get("metadata", {}), ensure_ascii=False),
                    json.dumps(chunk.get("embedding"), ensure_ascii=False) if chunk.get("embedding") is not None else None,
                    now,
                ),
            )
        connection.commit()
    return len(chunks)


def update_chunk_embeddings(document_id: str, embeddings: list[list[float]]) -> int:
    ensure_chatbot_tables()
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(
            """
            SELECT chunk_id
            FROM chatbot_chunks
            WHERE document_id = ?
            ORDER BY chunk_index ASC
            """,
            (document_id,),
        ).fetchall()
        for row, embedding in zip(rows, embeddings, strict=False):
            connection.execute(
                "UPDATE chatbot_chunks SET embedding_json = ? WHERE chunk_id = ?",
                (json.dumps(embedding), row[0]),
            )
        connection.commit()
    return min(len(rows), len(embeddings))


def get_chunks(document_id: str | None = None) -> list[dict[str, object]]:
    ensure_chatbot_tables()
    sql = """
        SELECT chunk_id, document_id, chunk_index, content, metadata_json, embedding_json
        FROM chatbot_chunks
    """
    params: list[object] = []
    if document_id:
        sql += " WHERE document_id = ?"
        params.append(document_id)
    sql += " ORDER BY document_id ASC, chunk_index ASC"
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(sql, params).fetchall()
    return [
        {
            "chunk_id": row[0],
            "document_id": row[1],
            "chunk_index": row[2],
            "content": row[3],
            "metadata": json.loads(row[4]),
            "embedding": json.loads(row[5]) if row[5] else None,
        }
        for row in rows
    ]


def save_chat_message(question: str, answer: str, sources: list[dict[str, object]]) -> None:
    ensure_chatbot_tables()
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT INTO chatbot_messages (question, answer, sources_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (question, answer, json.dumps(sources, ensure_ascii=False), datetime.now(timezone.utc).isoformat()),
        )
        connection.commit()

