from datetime import date

import typer
from rich.console import Console

from scheduler import db

console = Console()


def log(
    track: str = typer.Argument(help="Track title to log progress for"),
    status: str = typer.Option(
        "completed", help="Status: completed, in_progress, not_started"
    ),
    exercises: int = typer.Option(
        1, help="Number of exercises completed (only for completed status)"
    ),
):
    """Log daily progress for a track."""
    today_str = date.today().isoformat()

    # Validate status
    valid_statuses = ["not_started", "in_progress", "completed"]
    if status not in valid_statuses:
        console.print(
            f"❌ Invalid status. Must be one of: {', '.join(valid_statuses)}",
            style="red",
        )
        return

    try:
        conn = db.connect()
        with conn:
            # Check if already logged today
            cursor = conn.execute(
                "SELECT status FROM logs WHERE date = ? AND track = ?",
                (today_str, track),
            )
            existing = cursor.fetchone()

            if existing:
                # Update existing entry, don't increment again
                old_status = existing[0]
                conn.execute(
                    "UPDATE logs SET status = ? WHERE date = ? AND track = ?",
                    (status, today_str, track),
                )

                # Handle track completion count changes
                if old_status != "completed" and status == "completed":
                    # Changing from not-completed to completed - increment
                    conn.execute(
                        "UPDATE tracks SET completed = completed + ? WHERE title = ?",
                        (exercises, track),
                    )
                elif old_status == "completed" and status != "completed":
                    # Changing from completed to not-completed - decrement
                    conn.execute(
                        "UPDATE tracks SET completed = completed - ? WHERE title = ? AND completed >= ?",
                        (exercises, track, exercises),
                    )

                # Display update message
                if status == "pending":
                    console.print(
                        f"📝 Updated {track}: 📤 carried over (status: {status})",
                        style="yellow",
                    )
                elif status == "completed":
                    console.print(
                        f"📝 Updated {track}: ✅ completed ({exercises} exercises)",
                        style="green",
                    )
                elif status == "in_progress":
                    console.print(f"📝 Updated {track}: 🔄 in progress", style="blue")
                else:  # not_started
                    console.print(f"📝 Updated {track}: ⭕ not started", style="gray")

            else:
                # New entry, safe to insert and increment
                conn.execute(
                    "INSERT INTO logs (date, track, status) VALUES (?, ?, ?, ?)",
                    (today_str, track, status),
                )

                # Only increment track completion count if status is 'completed'
                if status == "completed":
                    conn.execute(
                        "UPDATE tracks SET completed = completed + ? WHERE title = ?",
                        (exercises, track),
                    )

                # Display new entry message
                if status == "pending":
                    console.print(
                        f"📝 Logged {track}: 📤 carried over (status: {status})",
                        style="yellow",
                    )
                elif status == "completed":
                    console.print(
                        f"📝 Logged {track}: ✅ completed ({exercises} exercises)",
                        style="green",
                    )
                elif status == "in_progress":
                    console.print(f"📝 Logged {track}: 🔄 in progress", style="blue")
                else:  # not_started
                    console.print(f"📝 Logged {track}: ⭕ not started", style="gray")

    except Exception as e:
        console.print(f"❌ Error logging progress: {e}", style="red")
