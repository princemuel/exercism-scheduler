from datetime import date

import typer
from rich.console import Console

from scheduler import db

console = Console()


def log(
    track: str = typer.Argument(help="Track title to log progress for"),
    completed: int = typer.Option(1, help="Number of exercises completed"),
    pending: bool = typer.Option(False, help="Mark as pending"),
):
    """Log daily progress for a track."""
    today_str = date.today().isoformat()

    try:
        conn = db.connect()
        with conn:
            # Update progress log
            conn.execute(
                "INSERT OR REPLACE INTO logs (date, track, completed, pending) VALUES (?, ?, ?, ?)",
                (today_str, track, completed, int(pending)),
            )

            # Update track stats
            conn.execute(
                "UPDATE tracks SET completed = completed + ? WHERE title = ?",
                (completed, track),
            )

        status = "📤 carried over" if pending else f"✅ completed ({completed})"
        console.print(f"📝 Logged {track}: {status}", style="green")

    except Exception as e:
        console.print(f"❌ Error logging progress: {e}", style="red")
