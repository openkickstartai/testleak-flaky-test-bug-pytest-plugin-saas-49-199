"""TestLeak CLI — scan tests for pollution from the command line."""
import json
import subprocess
import sys
from pathlib import Path

import typer

app = typer.Typer(name="testleak", help="\U0001f50d Find test pollution before it finds you.")


@app.command()
def scan(
    path: str = typer.Argument(".", help="Test directory or file"),
    report: str = typer.Option(None, "-r", "--report", help="JSON report output path"),
    fail: bool = typer.Option(False, "--fail", help="Exit 1 if pollution detected"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """Run pytest with TestLeak pollution tracking enabled."""
    cmd = [sys.executable, "-m", "pytest", path, "-p", "testleak_plugin", "--tb=short", "-q"]
    if report:
        cmd += ["--testleak-report", report]
    if fail:
        cmd.append("--testleak-fail")
    if verbose:
        cmd.append("-v")
    raise typer.Exit(subprocess.run(cmd).returncode)


@app.command()
def show(report_file: str = typer.Argument(..., help="Path to JSON report")):
    """Display a saved pollution report."""
    data = json.loads(Path(report_file).read_text())
    if not data:
        typer.echo("\u2705 Clean — no pollution found.")
        raise typer.Exit(0)
    typer.echo(f"\U0001f6a8 {len(data)} leak(s) found:\n")
    for item in data:
        typer.echo(f"  \U0001f4cd {item['test_id']}")
        typer.echo(f"     [{item['category']}] {item['key']}: {item['before']!r} -> {item['after']!r}")
    raise typer.Exit(1)


@app.command()
def version():
    """Print version."""
    typer.echo("testleak 0.1.0")


if __name__ == "__main__":
    app()
