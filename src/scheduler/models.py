from dataclasses import dataclass


@dataclass
class Track:
    title: str
    category: str
    total: int
    completed: int = 0
