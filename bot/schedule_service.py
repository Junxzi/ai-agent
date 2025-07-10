from __future__ import annotations

from typing import List, Tuple

from .data_store import DataStore


class ScheduleService:
    def __init__(self, store: DataStore):
        self.store = store

    def add_event(
        self,
        title: str,
        start_time: str,
        end_time: str | None = None,
        location: str | None = None,
        notes: str | None = None,
    ) -> int:
        cur = self.store.execute(
            """
            INSERT INTO events(title, start_time, end_time, location, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, start_time, end_time, location, notes),
        )
        return cur.lastrowid

    def list_events(self) -> List[Tuple]:
        return self.store.fetchall(
            "SELECT id, title, start_time, end_time, location, notes FROM events ORDER BY start_time"
        )
