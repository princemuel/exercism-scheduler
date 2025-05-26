import csv
import json
from datetime import date, timedelta


def export_to_csv(data, fieldnames, filename):
    with open(
        filename,
        mode="w",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def export_to_json(data, filename):
    with open(filename, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_week_range():
    today = date.today()
    start = today - timedelta(days=today.weekday())  # Monday
    end = start + timedelta(days=6)  # Sunday
    return start.isoformat(), end.isoformat()
