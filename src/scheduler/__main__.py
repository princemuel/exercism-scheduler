import typer

from scheduler.commands import export, generate, init, log, populate, report, status

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

if __name__ == "__main__":
    app()
