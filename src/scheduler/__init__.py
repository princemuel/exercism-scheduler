import typer

from scheduler.commands import (
    export,
    generate,
    init,
    log,
    populate,
    report,
    status,
    sync,
    track,
)

app = typer.Typer(
    help="Enhanced Learning Track Scheduler with Bitcoin-style Determinism"
)
app.add_typer(
    typer.Typer(
        name="cli",
        help="Command Line Interface for the Scheduler",
        rich_markup_mode="rich",
    ),
    name="cli",
)

app.command()(init.init)
app.command()(generate.generate)
app.command()(populate.populate)
app.command()(log.log)
app.command()(export.export)
app.command()(report.report)
app.command()(status.status)
app.command()(sync.sync)

app.add_typer(track.app, name="track", help="Track management commands")


def main() -> None:
    """Standalone entry point."""
    app()
