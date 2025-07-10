from __future__ import annotations

from typing import List, Tuple

from .data_store import DataStore


class TodoService:
    def __init__(self, store: DataStore):
        self.store = store

    def add_task(self, description: str, due: str | None = None) -> int:
        cur = self.store.execute(
            "INSERT INTO tasks(description, due_date, created_at) VALUES (?, ?, datetime('now'))",
            (description, due),
        )
        return cur.lastrowid

    def list_tasks(self) -> List[Tuple[int, str, str, int]]:
        return self.store.fetchall(
            "SELECT id, description, due_date, completed FROM tasks ORDER BY id"
        )

    def list_pending_tasks(self) -> List[Tuple[int, str, str]]:
        """Return only incomplete tasks."""
        return self.store.fetchall(
            "SELECT id, description, due_date FROM tasks WHERE completed = 0 ORDER BY id"
        )

    def complete_task(self, task_id: int) -> None:
        self.store.execute(
            "UPDATE tasks SET completed = 1 WHERE id = ?",
            (task_id,),
        )

    def delete_task(self, task_id: int) -> None:
        self.store.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
