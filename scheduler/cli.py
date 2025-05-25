import sqlite3

import typer
from rich.console import Console
from rich.table import Table

from scheduler import db, utils
from scheduler.scheduler import generate_schedule

app = typer.Typer()


@app.command()
def init(force: bool = False):
    """Initialize the database (optionally reset it)."""
    if force and db.DB_PATH.exists():
        db.DB_PATH.unlink()
        typer.echo("Existing DB deleted.")
    db.init_db()
    typer.echo("Database initialized.")


@app.command()
def log(track: str, completed: bool = True, carried: bool = False):
    """Log daily progress."""
    import datetime

    conn = db.get_connection()
    with conn:
        conn.execute(
            "INSERT INTO progress_log (date, track, completed, carried_over) VALUES (?, ?, ?, ?)",
            (datetime.date.today().isoformat(), track, int(completed), int(carried)),
        )
    typer.echo(f"Logged {track}: completed={completed}, carried={carried}")


@app.command()
def generate(force: bool = False):
    """Generate today's track schedule with carried-over tasks included."""
    main, optional, carried = generate_schedule(force=force)
    table = Table(title="Today's Schedule", show_lines=True)
    table.add_column("Type", style="bold cyan")
    table.add_column("Tracks", style="bold yellow")

    table.add_row("Main Tracks", ", ".join(main))
    table.add_row("Optional Tracks", ", ".join(optional))
    table.add_row("Carried Over", ", ".join(carried) if carried else "None")

    console = Console()
    console.print(table)


@app.command()
def export(
    table: str,
    format: str = "csv",
    output: str = "export_output",
    where: str = "",
    week: bool = False,
):
    """Export data from the database to CSV or JSON."""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        query = f"SELECT * FROM {table}"

        if week:
            start, end = utils.current_week_range()
            query += f" WHERE date BETWEEN '{start}' AND '{end}'"
        elif where:
            query += f" WHERE {where}"

        rows = cursor.execute(query).fetchall()
        colnames = [description[0] for description in cursor.description]
        data = [dict(zip(colnames, row)) for row in rows]

        output_path = db.DB_DIR / f"{output}.{format}"

        if format == "csv":
            utils.export_to_csv(data, fieldnames=colnames, filename=output_path)
        elif format == "json":
            utils.export_to_json(data, filename=output_path)
        else:
            typer.echo("Unsupported format. Choose 'csv' or 'json'.")
            return

        typer.echo(f"Exported {len(data)} rows from '{table}' to '{output_path}'")
    except sqlite3.Error as e:
        typer.echo(f"Database error: {e}")
    finally:
        conn.close()


@app.command()
def import_tracks():
    """Import tracks from tracks.json into the track_stats table."""
    db.import_tracks_from_json()
    typer.echo("Tracks imported from tracks.json into track_stats.")
