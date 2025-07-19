from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from scheduler import scheduler

console = Console()


def status():
    """Show current learning progress and statistics."""
    tracks = scheduler.get_all_tracks()

    if not tracks:
        console.print("❌ No tracks found. Run 'import-tracks' first.", style="red")
        return

    # Summary statistics
    total_exercises = sum(t["total"] for t in tracks)
    completed_exercises = sum(t["completed"] for t in tracks)
    overall_progress = (
        (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0
    )

    # Progress by category
    categories = {}
    for track in tracks:
        cat = track["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "completed": 0, "tracks": 0}
        categories[cat]["total"] += track["total"]
        categories[cat]["completed"] += track["completed"]
        categories[cat]["tracks"] += 1

    # Display summary
    summary_panel = Panel(
        f"📊 Total Progress: {completed_exercises}/{total_exercises} ({overall_progress:.1f}%)\n"
        f"📚 Total Tracks: {len(tracks)}\n"
        f"📚 Active Tracks: {len([t for t in tracks if t['active']])}\n"  # type: ignore
        f"🎯 Categories: {len(categories)}",
        title="Learning Overview",
        title_align="left",
    )
    console.print(summary_panel)

    # Category breakdown
    cat_table = Table(
        title="📋 Progress by Category", show_header=True, header_style="bold green"
    )
    cat_table.add_column("Category", style="blue")
    cat_table.add_column("Tracks", justify="center")
    cat_table.add_column("Progress", justify="center", style="yellow")
    cat_table.add_column("Progress Bar", justify="left")
    cat_table.add_column("Completion %", justify="center", style="white")

    for cat, data in sorted(categories.items()):
        completion_pct = (
            (data["completed"] / data["total"] * 100) if data["total"] > 0 else 0
        )
        progress_bar = "█" * int(completion_pct / 5) + "░" * (
            20 - int(completion_pct / 5)
        )

        cat_table.add_row(
            cat,
            str(data["tracks"]),
            f"{data['completed']}/{data['total']}",
            f"[green]{progress_bar}[/green]",
            f"{completion_pct:.1f}%",
        )

    console.print(cat_table)
