from typing import Optional

import typer
from rich.console import Console

from scheduler import db
from scheduler.models.track import Track

app = typer.Typer()

console = Console()


@app.command()
def update(
    title: str = typer.Argument(..., help="Track title to update"),
    total: Optional[int] = typer.Option(None, "--total", "-t", help="New total value"),
    completed: Optional[int] = typer.Option(
        None, "--completed", "-c", help="New completed value"
    ),
    category: Optional[str] = typer.Option(None, "--category", help="New category"),
):
    """Update a specific track's data in the database."""
    try:
        track = Track.get(title)
        if not track:
            console.print(f"❌ Track '{title}' not found", style="red")
            return

        # Build update dict
        updates = {}
        if total is not None:
            updates["total"] = total
        if completed is not None:
            updates["completed"] = completed
        if category is not None:
            updates["category"] = category

        if not updates:
            console.print("❌ No fields to update provided", style="red")
            return

        # Update using the model
        track.update(**updates)
        console.print(f"✅ Updated track '{title}'", style="green")
        console.print(
            f"   Title: {track.title}, Category: {track.category}, Total: {track.total}, Completed: {track.completed}"
        )

    except Exception as e:
        console.print(f"❌ Error updating track: {e}", style="red")


@app.command()
def list():
    """List all tracks."""
    conn = db.connect()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title, category, total, completed FROM tracks ORDER BY title"
        )
        tracks = cursor.fetchall()

        if not tracks:
            console.print("No tracks found", style="yellow")
            return

        console.print("\n[bold]TRACKS:[/bold]\n")
        console.print(
            "  [bold]{:<15} {:<15} {:>10} {:<10}[/bold]\n".format(
                "Title",
                "Category",
                "Progress",
                "Percentage",
            )
        )
        for title, category, total, completed in tracks:  # type: ignore
            progress = f"{completed}/{total}"
            percentage = f"{completed / total * 100:.1f}%" if total > 0 else "0%"
            console.print(
                f"  {title:<15} {category:<15} {progress:>10} {percentage:>10}"
            )


@app.command("show")
def show_track(title: str = typer.Argument(..., help="Track title to show")):
    """Show detailed information about a track."""
    track = Track.get(title)
    if not track:
        console.print(f"❌ Track '{title}' not found", style="red")
        return

    console.print(f"\n[bold]{track.title}[/bold]")
    console.print(f"Category: {track.category}")
    console.print(
        f"Progress: {track.completed}/{track.total} ({track.completed / track.total * 100:.1f}%)"
    )
