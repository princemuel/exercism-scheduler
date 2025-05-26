import sqlite3

from scheduler.constants import DATABASE_PATH, SCHEMA_PATH


def initialize():
    conn = sqlite3.connect(DATABASE_PATH)
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.close()


def connect():
    return sqlite3.connect(DATABASE_PATH)
