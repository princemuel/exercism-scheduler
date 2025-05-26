import json

from rich.console import Console
from rich.table import Table

from scheduler import db, utils

console = Console()


def report():
    """Generate a comprehensive weekly learning report."""
    start_date, end_date = utils.get_week_range()

    conn = db.connect()
    cursor = conn.cursor()

    # Get scheduled tracks for the week
    cursor.execute(
        """
        SELECT date, core, extra
        FROM schedule
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    """,
        (start_date, end_date),
    )

    weekly_schedule = cursor.fetchall()

    # Get progress for the week
    cursor.execute(
        """
        SELECT date, track, completed, pending
        FROM logs
        WHERE date BETWEEN ? AND ?
        ORDER BY date, track
    """,
        (start_date, end_date),
    )

    weekly_progress = cursor.fetchall()
    conn.close()

    console.print(f"\n📊 Weekly Report ({start_date} to {end_date})", style="bold cyan")

    # Schedule overview
    schedule_table = Table(title="📅 Weekly Schedule", show_header=True)
    schedule_table.add_column("Date", style="cyan")
    schedule_table.add_column("Core Tracks", style="yellow")
    schedule_table.add_column("Extra", style="green")

    for row in weekly_schedule:
        date_str = row[0]
        core = json.loads(row[1]) if row[1] else []
        extra = json.loads(row[2]) if row[2] else []

        schedule_table.add_row(
            date_str,
            ", ".join(core) if core else "None",
            ", ".join(extra) if extra else "None",
        )

    console.print(schedule_table)

    # Progress summary
    if weekly_progress:
        progress_table = Table(title="✅ Weekly Progress", show_header=True)
        progress_table.add_column("Date", style="cyan")
        progress_table.add_column("Track", style="yellow")
        progress_table.add_column("Completed", justify="center")
        progress_table.add_column("Status", style="green")

        for row in weekly_progress:
            status = "📤 Carried" if row[3] else "✅ Done"
            progress_table.add_row(row[0], row[1], str(row[2]), status)

        console.print(progress_table)
    else:
        console.print("ℹ️  No progress logged this week.", style="yellow")
