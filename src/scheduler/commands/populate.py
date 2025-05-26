import typer
from rich.console import Console

from scheduler import seed

console = Console()


def populate(file: str = typer.Argument()):
    """Import tracks from tracks.json into the tracks table."""
    try:
        seed.tracks_from_json(file)
        console.print("✅ Tracks imported from tracks.json into tracks.", style="green")
    except Exception as e:
        console.print(f"❌ Error importing tracks: {e}", style="red")
        console.print(f"❌ Error importing tracks: {e}", style="red")
        console.print(f"❌ Error importing tracks: {e}", style="red")
