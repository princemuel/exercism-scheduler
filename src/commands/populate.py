from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from src.models.track import Track

console = Console()


def populate(file: Optional[Path] = typer.Argument(None)):
    """Import tracks from tracks.json into the tracks table."""
    try:
        tracks = Track.load_many_from_json(file)
        for track in tracks:
            track.save()
        console.print("✅ Tracks imported from tracks.json into tracks.", style="green")
    except Exception as e:
        console.print(f"❌ Error importing tracks: {e}", style="red")
