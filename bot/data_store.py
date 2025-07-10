import sqlite3
from pathlib import Path
from typing import Any, Iterable


class DataStore:
    """Simple SQLite wrapper for the bot services."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        """Create necessary tables if they don't exist."""
        root = Path(__file__).resolve().parent.parent
        with open(root / "todo_schema.sql", "r", encoding="utf-8") as f:
            self.conn.executescript(f.read())
        with open(root / "events_schema.sql", "r", encoding="utf-8") as f:
            self.conn.executescript(f.read())
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            remind_at TEXT NOT NULL,
            sent INTEGER NOT NULL DEFAULT 0
            )"""
        )
        self.conn.commit()

    def execute(self, query: str, params: Iterable[Any] = ()):
        cur = self.conn.execute(query, params)
        self.conn.commit()
        return cur

    def fetchall(self, query: str, params: Iterable[Any] = ()):
        cur = self.conn.execute(query, params)
        return cur.fetchall()

    def close(self):
        self.conn.close()
