from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from src import db
from src.models.track import Track

console = Console()


def sync(
    json_path: Optional[Path] = typer.Argument(None),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show changes without applying them"
    ),
):
    """Sync tracks from JSON file to database, showing what will change."""

    if json_path is None:
        json_path = Path(__file__).parent / "database" / "tracks.json"
    tracks = Track.load_many_from_json(json_path)

    json_tracks = {track.title: track.__dict__ for track in tracks}

    conn = db.connect()
    cursor = conn.cursor()

    try:
        # Get current database state
        cursor.execute("SELECT title, category, total, completed FROM tracks")
        db_tracks = {
            row[0]: {
                "title": row[0],
                "category": row[1],
                "total": row[2],
                "completed": row[3],
            }
            for row in cursor.fetchall()
        }

        changes = []

        # Check for updates and new tracks
        for title, json_track in json_tracks.items():
            if title in db_tracks:
                db_track = db_tracks[title]
                track_changes = []

                for field in ["category", "total", "completed"]:
                    if json_track[field] != db_track[field]:
                        track_changes.append(
                            f"{field}: {db_track[field]} → {json_track[field]}"
                        )

                if track_changes:
                    changes.append(("UPDATE", title, track_changes))
            else:
                changes.append(("INSERT", title, []))

        # Check for deleted tracks
        for title in db_tracks:
            if title not in json_tracks:
                changes.append(("DELETE", title, []))

        # Display changes
        if changes:
            table = Table(title="Proposed Changes")
            table.add_column("Action", style="cyan")
            table.add_column("Track", style="magenta")
            table.add_column("Changes", style="yellow")

            for action, title, track_changes in changes:
                change_str = "; ".join(track_changes) if track_changes else "New track"
                table.add_row(action, title, change_str)

            console.print(table)

            if not dry_run:
                if typer.confirm("Apply these changes?"):
                    apply_changes(cursor, json_tracks, db_tracks)
                    conn.commit()
                    console.print("✅ Changes applied successfully", style="green")
                else:
                    console.print("❌ Changes cancelled", style="yellow")
            else:
                console.print("🔍 Dry run - no changes applied", style="blue")
        else:
            console.print(
                "✅ No changes needed - database is up to date", style="green"
            )

    finally:
        conn.close()


def apply_changes(cursor, json_tracks, db_tracks):
    """Apply the changes to the database."""
    for _, json_track in json_tracks.items():
        cursor.execute(
            "INSERT OR REPLACE INTO tracks (title, category, total, completed) VALUES (?, ?, ?, ?)",
            (
                json_track["title"],
                json_track["category"],
                json_track["total"],
                json_track["completed"],
            ),
        )

    # Delete tracks that are no longer in JSON
    for title in db_tracks:
        if title not in json_tracks:
            cursor.execute("DELETE FROM tracks WHERE title = ?", (title,))
