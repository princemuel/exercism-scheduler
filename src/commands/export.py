import sqlite3
from pathlib import Path

import typer
from platformdirs import user_downloads_dir
from rich.console import Console

from src import db, utils

console = Console()

DOWNLOADS_DIR = Path(user_downloads_dir())


def export(
    table: str = typer.Argument(help="Table name to export"),
    format: str = typer.Option("csv", help="Export format: csv or json"),
    output: str = typer.Option("progress", help="Output filename (w/o extension)"),
    where: str = typer.Option("", help="SQL WHERE clause"),
    week: bool = typer.Option(False, help="Export current week only"),
):
    """Export data from the database to CSV or JSON."""
    conn = db.connect()
    cursor = conn.cursor()

    try:
        query = f"SELECT * FROM {table}"

        if week:
            start, end = utils.get_week_range()
            query += f" WHERE date BETWEEN '{start}' AND '{end}'"
        elif where:
            query += f" WHERE {where}"

        rows = cursor.execute(query).fetchall()
        colnames = [description[0] for description in cursor.description]
        data = [dict(zip(colnames, row)) for row in rows]

        out_path = DOWNLOADS_DIR / f"{output}.{format}"

        if format == "csv":
            utils.export_to_csv(data, fieldnames=colnames, filename=out_path)
        elif format == "json":
            utils.export_to_json(data, filename=out_path)
        else:
            console.print("❌ Unsupported format. Choose 'csv' or 'json'.", style="red")
            return

        console.print(
            f"✅ Exported {len(data)} rows from '{table}' to '{out_path}'",
            style="green",
        )
    except sqlite3.Error as e:
        console.print(f"❌ Database error: {e}", style="red")
    finally:
        conn.close()
