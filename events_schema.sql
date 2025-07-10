-- SQLite schema for the user's event schedule
-- テーブル: events
-- イベントID、タイトル、日時、場所、備考を管理する

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- イベントID
    title TEXT NOT NULL,                  -- タイトル
    start_time TEXT NOT NULL,             -- 開始日時 (ISO8601形式)
    end_time TEXT,                        -- 終了日時 (任意)
    location TEXT,                        -- 場所 (任意)
    notes TEXT,                           -- 備考・メモ (任意)
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP -- 作成日時
);
