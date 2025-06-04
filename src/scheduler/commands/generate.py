import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from scheduler.scheduler import generate_schedule

console = Console()


def generate(
    force: bool = typer.Option(False, help="Force regenerate today's schedule"),
    show_scores: bool = typer.Option(False, help="Show detailed scoring breakdown"),
):
    """Generate today's track schedule using deterministic algorithm."""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating optimal schedule...", total=None)

        core, extra, score_details = generate_schedule(force=force)

        progress.update(task, completed=100, description="Schedule generated!")

    # Display main schedule
    table = Table(
        title="📅 Today's Learning Schedule",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Type", style="bold", width=15)
    table.add_column("Tracks", style="yellow")

    table.add_row("🎯 Core", ", ".join(core))
    table.add_row("⭐ Extra", ", ".join(extra) if extra else "None")

    console.print(table)

    # Show scoring details if requested
    if show_scores and score_details:
        console.print("\n📊 Scoring Breakdown:", style="bold cyan")

        score_table = Table(show_header=True, header_style="bold magenta")
        score_table.add_column("Track")
        score_table.add_column("Total Score")
        score_table.add_column("Progress")
        score_table.add_column("Recency")
        score_table.add_column("Rotation")
        score_table.add_column("Category")
        score_table.add_column("Completion %")

        # Show top 10 scores
        sorted_tracks = sorted(
            score_details.items(), key=lambda x: x[1]["total"], reverse=True
        )
        for track, details in sorted_tracks[:10]:
            score_table.add_row(
                track,
                f"{details['total']:.3f}",
                f"{details['progress']:.3f}",
                f"{details['recency']:.3f}",
                f"{details['rotation']:.3f}",
                f"{details['category']:.3f}",
                f"{details['completion_ratio'] * 100:.1f}%",
            )

        console.print(score_table)
