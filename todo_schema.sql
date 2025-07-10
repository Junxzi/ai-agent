-- SQLite schema for ToDo tasks
-- Each record represents a single task

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    due_date TEXT,
    completed BOOLEAN NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
