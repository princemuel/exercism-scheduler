import json
import os
import sqlite3
from pathlib import Path

from scheduler.models import Track

DB_FILE = ".scheduler.db"
DB_DIR = Path.cwd() / "database"
DB_PATH = DB_DIR / DB_FILE

DATABASE_URL = f"sqlite:///{DB_PATH}"

# Ensure the directory exists
os.makedirs(DB_DIR, exist_ok=True)

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS track_stats (
    title TEXT PRIMARY KEY,
    category TEXT,
    total INTEGER,
    completed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS daily_schedule (
    date TEXT PRIMARY KEY,
    main_tracks TEXT CHECK(json_valid(main_tracks)),
    optional_tracks TEXT CHECK(json_valid(optional_tracks))
);

CREATE TABLE IF NOT EXISTS progress_log (
    date TEXT,
    track TEXT,
    completed INTEGER,
    carried_over INTEGER DEFAULT 0,
    PRIMARY KEY (date, track),
    FOREIGN KEY (date) REFERENCES daily_schedule(date) ON DELETE CASCADE,
    FOREIGN KEY (track) REFERENCES track_stats(title) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_progress_log_date ON progress_log(date);
CREATE INDEX IF NOT EXISTS idx_progress_log_track ON progress_log(track);
"""


def init_db():
    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.executescript(CREATE_TABLES_SQL)
    conn.close()


def get_connection():
    return sqlite3.connect(DB_PATH)


def import_tracks_from_json(json_path=None):
    """Import tracks from tracks.json into track_stats table."""
    if json_path is None:
        json_path = Path(__file__).parent.parent / "database" / "tracks.json"
    with open(json_path, "r", encoding="utf-8") as f:
        tracks = json.load(f)
    conn = get_connection()
    cursor = conn.cursor()
    for track_dict in tracks:
        track = Track(**track_dict)
        cursor.execute(
            "REPLACE INTO track_stats (title, category, total, completed) VALUES (?, ?, ?, ?)",
            (track.title, track.category, track.total, track.completed),
        )
    conn.commit()
    conn.close()
