import json
from pathlib import Path

from rich.console import Console

from scheduler import db
from scheduler.models import Track

console = Console()


def tracks_from_json(json_path=None):
    """Import tracks from tracks.json into tracks table."""
    if json_path is None:
        json_path = Path(__file__).parent.parent / "database" / "tracks.json"
    with open(json_path, "r", encoding="utf-8") as f:
        tracks = json.load(f)
    conn = db.connect()
    cursor = conn.cursor()
    for track_dict in tracks:
        track = Track(**track_dict)
        cursor.execute(
            "INSERT OR REPLACE INTO tracks (title, category, total, completed) VALUES (?, ?, ?, ?)",
            (track.title, track.category, track.total, track.completed),
        )
    conn.commit()
    conn.close()
    console.print(
        f"✅ Imported {len(tracks)} tracks from {json_path} into tracks table.",
        style="green",
    )
