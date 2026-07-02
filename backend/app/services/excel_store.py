from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from app.core.config import DATABASE_PATH


def ensure_excel_tables() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS excel_workbooks (
                file_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS excel_sheets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                sheet_name TEXT NOT NULL,
                columns_json TEXT NOT NULL,
                rows_json TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                FOREIGN KEY(file_id) REFERENCES excel_workbooks(file_id) ON DELETE CASCADE
            )
            """
        )
        connection.commit()


def _records_to_json(frame: pd.DataFrame) -> str:
    return json.dumps(frame.where(pd.notna(frame), None).to_dict(orient="records"), ensure_ascii=False)


def _columns_to_json(frame: pd.DataFrame) -> str:
    return json.dumps([str(column) for column in frame.columns], ensure_ascii=False)


def store_excel_workbook(
    file_id: str,
    path: Path,
    filename: str,
) -> dict[str, object]:
    ensure_excel_tables()
    created_at = datetime.now(timezone.utc).isoformat()
    excel_file = pd.ExcelFile(path, engine="openpyxl")
    sheet_summaries: list[dict[str, object]] = []

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO excel_workbooks (file_id, filename, created_at)
            VALUES (?, ?, ?)
            """,
            (file_id, filename, created_at),
        )

        connection.execute("DELETE FROM excel_sheets WHERE file_id = ?", (file_id,))

        for sheet_name in excel_file.sheet_names:
            frame = excel_file.parse(sheet_name=sheet_name)
            columns_json = _columns_to_json(frame)
            rows_json = _records_to_json(frame)
            connection.execute(
                """
                INSERT INTO excel_sheets (
                    file_id, sheet_name, columns_json, rows_json, row_count
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (file_id, sheet_name, columns_json, rows_json, len(frame)),
            )
            sheet_summaries.append(
                {
                    "sheet_name": sheet_name,
                    "columns": json.loads(columns_json),
                    "rows": json.loads(rows_json),
                    "row_count": len(frame),
                }
            )

        connection.commit()

    return {
        "file_id": file_id,
        "filename": filename,
        "created_at": created_at,
        "sheets": sheet_summaries,
    }


def list_excel_workbooks(filename: str | None = None, sheet_name: str | None = None) -> list[dict[str, object]]:
    ensure_excel_tables()
    query = [
        """
        SELECT
            w.file_id,
            w.filename,
            w.created_at,
            COUNT(s.id) AS sheet_count,
            GROUP_CONCAT(s.sheet_name, '||') AS sheet_names,
            SUM(s.row_count) AS row_count
        FROM excel_workbooks w
        JOIN excel_sheets s ON s.file_id = w.file_id
        """
    ]
    params: list[object] = []
    filters: list[str] = []
    if filename:
        filters.append("w.filename LIKE ?")
        params.append(f"%{filename}%")
    if sheet_name:
        filters.append("s.sheet_name LIKE ?")
        params.append(f"%{sheet_name}%")
    if filters:
        query.append("WHERE " + " AND ".join(filters))
    query.append("GROUP BY w.file_id, w.filename, w.created_at")
    query.append("ORDER BY w.created_at DESC")

    sql = "\n".join(query)
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(sql, params).fetchall()

    return [
        {
            "file_id": row[0],
            "filename": row[1],
            "created_at": row[2],
            "sheet_count": row[3],
            "sheet_names": row[4].split("||") if row[4] else [],
            "row_count": row[5] or 0,
        }
        for row in rows
    ]


def get_excel_workbook(file_id: str) -> dict[str, object] | None:
    ensure_excel_tables()
    with sqlite3.connect(DATABASE_PATH) as connection:
        workbook = connection.execute(
            """
            SELECT file_id, filename, created_at
            FROM excel_workbooks
            WHERE file_id = ?
            """,
            (file_id,),
        ).fetchone()
        if workbook is None:
            return None
        sheets = connection.execute(
            """
            SELECT sheet_name, columns_json, rows_json, row_count
            FROM excel_sheets
            WHERE file_id = ?
            ORDER BY id ASC
            """,
            (file_id,),
        ).fetchall()

    sheet_payloads = []
    for sheet_name, columns_json, rows_json, row_count in sheets:
        sheet_payloads.append(
            {
                "sheet_name": sheet_name,
                "columns": json.loads(columns_json),
                "rows": json.loads(rows_json),
                "row_count": row_count,
            }
        )

    return {
        "file_id": workbook[0],
        "filename": workbook[1],
        "created_at": workbook[2],
        "sheet_count": len(sheet_payloads),
        "sheets": sheet_payloads,
    }


def delete_excel_workbook(file_id: str) -> bool:
    ensure_excel_tables()
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("DELETE FROM excel_sheets WHERE file_id = ?", (file_id,))
        cursor = connection.execute("DELETE FROM excel_workbooks WHERE file_id = ?", (file_id,))
        connection.commit()
        return cursor.rowcount > 0


def delete_all_excel_workbooks() -> int:
    ensure_excel_tables()
    with sqlite3.connect(DATABASE_PATH) as connection:
        sheet_count = connection.execute("DELETE FROM excel_sheets").rowcount
        workbook_count = connection.execute("DELETE FROM excel_workbooks").rowcount
        connection.commit()
    return workbook_count or sheet_count or 0
