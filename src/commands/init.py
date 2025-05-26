import typer
from rich.console import Console

from src import db
from src.constants import DATA_DIR, DATABASE_PATH

console = Console()


def init(
    force: bool = typer.Option(False, "--force", help="Reinitialize database"),
):
    """Initialize user data directory and database.

    This command sets up the necessary directories and initializes the database.
    If the database already exists, it will be deleted and recreated.

    Use the --force option to skip confirmation.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if DATABASE_PATH.exists() and not force:
        console.print(
            "Database already exists. Use --force to recreate.", style="yellow"
        )
        console.print("Exiting without changes.", style="yellow")
        typer.echo("Use --force to recreate the database.")
        raise typer.Exit()

    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
        console.print("🗑️  Existing DB deleted.", style="yellow")

    db.initialize()
    console.print(f"✅ Database initialized at {DATABASE_PATH}", style="green")
