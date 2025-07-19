import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Set, Tuple

from rich.console import Console

from scheduler import db
from scheduler.constants import (
    CATEGORY_WEIGHT,
    COMPLETION_THRESHOLD,
    DAYS_FOR_TRACK_ROTATION,
    MAX_APPEARANCES_PER_WEEK,
    MAX_DAILY_TRACKS,
    PROGRESS_WEIGHT,
    RECENCY_WEIGHT,
    ROTATION_WEIGHT,
)
from scheduler.helpers import deterministic_k

console = Console()


def get_all_tracks() -> List[Dict]:
    """Get all track statistics from database."""
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, category, total, completed, active
        FROM tracks
        ORDER BY title
    """)
    tracks = []
    for row in cursor.fetchall():
        tracks.append(
            {
                "title": row[0],
                "category": row[1],
                "total": row[2],
                "completed": row[3],
                "active": row[4],
            }
        )
    conn.close()
    return tracks


def get_active_tracks() -> List[Dict]:
    """Get active track statistics from database."""
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, category, total, completed, active
        FROM tracks
        WHERE active = 1
        ORDER BY title
    """)
    tracks = []
    for row in cursor.fetchall():
        tracks.append(
            {"title": row[0], "category": row[1], "total": row[2], "completed": row[3]}
        )
    conn.close()
    return tracks


def get_recent_history(days: int = DAYS_FOR_TRACK_ROTATION) -> Dict[str, int]:
    """Get track appearance counts in recent days."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT value as track, COUNT(*) as appearances
        FROM schedule, json_each(schedule.core)
        WHERE date BETWEEN ? AND ?
        GROUP BY value
    """,
        (start_date.isoformat(), end_date.isoformat()),
    )

    history = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return history


def get_track_last_appearance(track: str) -> int:
    """Get days since track last appeared in schedule."""
    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT MAX(date) as last_date
        FROM schedule, json_each(schedule.core)
        WHERE value = ?
    """,
        (track,),
    )

    result = cursor.fetchone()
    conn.close()

    if result[0]:
        last_date = datetime.strptime(result[0], "%Y-%m-%d").date()
        return (date.today() - last_date).days
    return 999


def calculate_track_score(
    track: Dict,
    history: Dict[str, int],
    today_str: str,
    selected_categories: Optional[Set[str]] = None,
) -> Tuple[Decimal, Dict]:
    """Calculate comprehensive score for track selection."""
    title = track["title"]
    category = track["category"]

    selected_categories = selected_categories or set()

    # 1. Progress Score (inverse of completion ratio)
    completion_ratio = Decimal(track["completed"]) / Decimal(track["total"])
    if completion_ratio >= COMPLETION_THRESHOLD:
        progress_score = Decimal("0")  # Completed tracks get lowest priority
    else:
        progress_score = Decimal("1") - completion_ratio

    # 2. Recency Score (days since last appearance)
    days_since = get_track_last_appearance(title)
    recency_score = min(Decimal(days_since) / Decimal("7"), Decimal("1"))

    # 3. Rotation Score (inverse of recent appearances)
    recent_appearances = history.get(title, 0)
    if recent_appearances >= MAX_APPEARANCES_PER_WEEK:
        rotation_score = Decimal("0")  # Maxed out for the week
    else:
        rotation_score = Decimal("1") - (
            Decimal(recent_appearances) / Decimal(MAX_APPEARANCES_PER_WEEK)
        )

    # 4. Category Diversity Score (pseudo-random based on deterministic seed)
    k_value = deterministic_k(today_str, title)
    category_score = Decimal(k_value % 1000) / Decimal("1000")  # Normalize to 0-1

    # 5. Category Diversity Bonus (boost for unused categories)
    diversity_bonus = (
        Decimal("0.5") if category not in selected_categories else Decimal("0")
    )

    # Combine scores with weights
    total_score = (
        progress_score * PROGRESS_WEIGHT
        + recency_score * RECENCY_WEIGHT
        + rotation_score * ROTATION_WEIGHT
        + category_score * CATEGORY_WEIGHT
        + diversity_bonus  # Flat bonus for category diversity
    )

    score_breakdown = {
        "progress": float(progress_score),
        "recency": float(recency_score),
        "rotation": float(rotation_score),
        "category": float(category_score),
        "diversity_bonus": float(diversity_bonus),
        "total": float(total_score),
        "completion_ratio": float(completion_ratio),
        "days_since_last": days_since,
        "recent_appearances": recent_appearances,
    }

    return total_score, score_breakdown


def generate_schedule(
    target_date: Optional[date] = None, force: bool = False
) -> Tuple[List[str], List[str], Dict]:
    """Generate schedule using Bitcoin-style deterministic selection."""
    if target_date is None:
        target_date = date.today()

    today_str = target_date.isoformat()

    # Check if schedule already exists
    if not force:
        conn = db.connect()
        cursor = conn.cursor()
        row = cursor.execute(
            "SELECT core, extra FROM schedule WHERE date = ?",
            (today_str,),
        ).fetchone()
        if row:
            core = json.loads(row[0])
            extra = json.loads(row[1])
            conn.close()
            return core, extra, {}
        conn.close()

    # Get all data needed for scoring
    tracks = get_active_tracks()
    history = get_recent_history()

    # Score all tracks once
    scored_tracks = []
    score_details = {}

    # Build category usage counts from recent history
    category_counts = {}
    track_lookup = {t["title"]: t["category"] for t in tracks}

    for track_title, appearances in history.items():
        if track_title in track_lookup:
            category = track_lookup[track_title]
            category_counts[category] = category_counts.get(category, 0) + appearances

    for track in tracks:
        # Treat frequently appearing categories as "overused" for diversity scoring
        overused_categories = {
            cat for cat, count in category_counts.items() if count >= 2
        }  # Adjust threshold as needed

        score, breakdown = calculate_track_score(
            track, history, today_str, overused_categories
        )
        scored_tracks.append((track["title"], score, track["category"]))
        score_details[track["title"]] = breakdown

    # Sort by score (descending) then by deterministic hash for tie-breaking
    def sort_key(item):
        title, score, _ = item
        k_value = deterministic_k(today_str, title)
        return (-score, k_value)

    scored_tracks.sort(key=sort_key)

    # Filter out ineligible tracks
    eligible_tracks = []
    for title, score, category in scored_tracks:
        # Skip if already completed
        if score_details[title]["completion_ratio"] >= float(COMPLETION_THRESHOLD):
            continue

        # Skip if maxed out appearances this week
        if score_details[title]["recent_appearances"] >= MAX_APPEARANCES_PER_WEEK:
            continue

        eligible_tracks.append(title)

    # Split tracks by ratio - core gets the majority, extra gets the rest
    total_tracks = min(
        len(eligible_tracks), MAX_DAILY_TRACKS + 2
    )  # Assuming 2 extra slots
    core_count = min(MAX_DAILY_TRACKS, total_tracks)

    # Split the eligible tracks
    core = eligible_tracks[:core_count]
    extra = eligible_tracks[core_count:total_tracks]

    # Store in database
    conn = db.connect()
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO schedule (date, core, extra) VALUES (?, ?, ?)",
            (today_str, json.dumps(core), json.dumps(extra)),
        )

    return core, extra, score_details
