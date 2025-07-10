from __future__ import annotations

import datetime
from typing import List, Tuple

from .data_store import DataStore


class ReminderService:
    def __init__(self, store: DataStore):
        self.store = store

    def add_reminder(self, message: str, remind_at: str) -> int:
        cur = self.store.execute(
            "INSERT INTO reminders(message, remind_at) VALUES (?, ?)",
            (message, remind_at),
        )
        return cur.lastrowid

    def list_pending(self) -> List[Tuple[int, str, str]]:
        return self.store.fetchall(
            "SELECT id, message, remind_at FROM reminders WHERE sent = 0 ORDER BY remind_at"
        )

    def mark_sent(self, reminder_id: int) -> None:
        self.store.execute(
            "UPDATE reminders SET sent = 1 WHERE id = ?",
            (reminder_id,),
        )

    def due_reminders(self, now: datetime.datetime) -> List[Tuple[int, str]]:
        return self.store.fetchall(
            "SELECT id, message FROM reminders WHERE sent = 0 AND remind_at <= ?",
            (now.isoformat(),),
        )
