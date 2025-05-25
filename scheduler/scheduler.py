import datetime
import hashlib
import json
import random
import sqlite3
from typing import List, Tuple

from scheduler import db
from scheduler.db import get_connection

# def generate_schedule() -> Tuple[List[str], List[str]]:
#     """Generate today's track schedule, including carried-over tracks, and write to daily_schedule."""
#     today = datetime.date.today()
#     iso_year, iso_week, _ = today.isocalendar()
#     week_key = f"{iso_year}-{iso_week}"
#     conn = db.get_connection()
#     cursor = conn.cursor()

#     # Get all tracks
#     cursor.execute("SELECT title FROM track_stats")
#     all_tracks = [row[0] for row in cursor.fetchall()]
#     if not all_tracks:
#         return [], []

#     # Get carried-over tracks from previous day
#     prev_date = today - datetime.timedelta(days=1)
#     cursor.execute(
#         "SELECT track FROM progress_log WHERE date=? AND carried_over=1",
#         (prev_date.isoformat(),),
#     )
#     carried_over = [row[0] for row in cursor.fetchall()]

#     # Remove carried-over from pool to avoid duplicates
#     available_tracks = [t for t in all_tracks if t not in carried_over]

#     # Stable shuffle based on ISO week
#     def stable_sample(pool, n):
#         pool = sorted(pool)
#         h = hashlib.sha256((week_key + str(pool)).encode()).hexdigest()
#         indices = sorted(range(len(pool)), key=lambda i: h[i % len(h)])
#         return [pool[i] for i in indices[:n]]

#     main_needed = max(0, 4 - len(carried_over))
#     main_tracks = carried_over + stable_sample(available_tracks, main_needed)
#     remaining_tracks = [t for t in available_tracks if t not in main_tracks]
#     optional_tracks = stable_sample(remaining_tracks, 2)

#     # Write to daily_schedule
#     cursor.execute(
#         "REPLACE INTO daily_schedule (date, main_tracks, optional_tracks) VALUES (?, ?, ?)",
#         (today.isoformat(), ",".join(main_tracks), ",".join(optional_tracks)),
#     )
#     conn.commit()
#     conn.close()
#     return main_tracks, optional_tracks




MAIN_TRACK_COUNT = 4
OPTIONAL_TRACK_COUNT = 2
CARRY_FORWARD_LOOKBACK_DAYS = 3


def get_all_tracks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM track_stats")
    tracks = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tracks


def get_weekly_usage():
    start = (datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())).isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT value AS track, COUNT(*) as uses
        FROM daily_schedule, json_each(daily_schedule.main_tracks)
        WHERE date >= ?
        GROUP BY value
    """, (start,))
    counts = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return counts


def get_recent_carried_over():
    today = datetime.date.today()
    window_start = (today - datetime.timedelta(days=CARRY_FORWARD_LOOKBACK_DAYS)).isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT track FROM progress_log
        WHERE carried_over = 1 AND date >= ?
    """, (window_start,))
    carried = [row[0] for row in cursor.fetchall()]
    conn.close()
    return carried

def generate_schedule(force: bool = False):
    today = datetime.date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    if not force:
        row = cursor.execute("SELECT main_tracks, optional_tracks FROM daily_schedule WHERE date = ?", (today,)).fetchone()
        if row:
            main = json.loads(row[0])
            optional = json.loads(row[1])
            carried = get_recent_carried_over()
            conn.close()
            return main, optional, carried

    all_tracks = get_all_tracks()
    usage = get_weekly_usage()
    carried = get_recent_carried_over()

    tracks_sorted = sorted(all_tracks, key=lambda t: (usage.get(t, 0), t))

    # Fully deterministic selection based on sorted data + fixed seed
    seed = int(datetime.date.today().strftime("%G%V%u"))
    rng = random.Random(seed)
    rng.shuffle(tracks_sorted)

    filtered_tracks = [t for t in tracks_sorted if t not in carried]
    main = filtered_tracks[:MAIN_TRACK_COUNT]
    optional = filtered_tracks[MAIN_TRACK_COUNT:MAIN_TRACK_COUNT + OPTIONAL_TRACK_COUNT]

    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO daily_schedule (date, main_tracks, optional_tracks) VALUES (?, ?, ?)",
            (today, json.dumps(main), json.dumps(optional))
        )

    return main, optional, carried
