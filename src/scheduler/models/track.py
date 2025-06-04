import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from scheduler import db

console = Console()


@dataclass
class Track:
    title: str
    category: str
    total: int
    completed: int = 0

    def save(self):
        """Save or update this track in the database."""
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO tracks (title, category, total, completed) VALUES (?, ?, ?, ?)",
                (self.title, self.category, self.total, self.completed),
            )
            conn.commit()
        finally:
            conn.close()

    def update(self, **kwargs):
        """Update specific fields and save to database."""
        updated_fields = []
        for key, value in kwargs.items():
            if hasattr(self, key):
                old_value = getattr(self, key)
                setattr(self, key, value)
                updated_fields.append(f"{key}: {old_value} → {value}")

        if updated_fields:
            self.save()
            console.print(f"Updated {', '.join(updated_fields)}", style="dim")
        return self

    @classmethod
    def get(cls, title: str) -> Optional["Track"]:
        """Get a track by title from the database."""
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT title, category, total, completed FROM tracks WHERE title = ?",
                (title,),
            )
            row = cursor.fetchone()
            if row:
                return cls(*row)
            return None
        finally:
            conn.close()

    @classmethod
    def load_many_from_json(cls, json_path: Optional[Path] = None) -> List["Track"]:
        """Load multiple tracks from a JSON file."""
        if json_path is None:
            json_path = Path(__file__).parent / "database" / "tracks.json"

        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
            return [cls(**item) for item in data]
