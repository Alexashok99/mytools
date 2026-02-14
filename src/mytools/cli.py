# cli.py

"""Main CLI application using Typer."""
import typer
from typing import Optional
from importlib.metadata import entry_points
import sys

from .utils import setup_logging, logger
from .config import settings

app = typer.Typer(
    name="mytools",
    help="🛠️ MyTools – Developer's Swiss Army Knife",
    add_completion=False,
    rich_markup_mode="rich",
)

# Global callback for options that apply to all commands
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
    log_level: Optional[str] = typer.Option(
        None,
        "--log-level",
        "-l",
        help="Set log level (DEBUG, INFO, WARNING, ERROR)",
    ),
):
    """Common options applied before running any command."""
    # configure logging early so downstream code respects level
    if debug:
        settings.log_level = "DEBUG"
    elif log_level:
        settings.log_level = log_level.upper()

    # re-configure logger with new level
    setup_logging()

    # if no subcommand supplied, show help
    if ctx.invoked_subcommand is None:
        typer.echo(app.get_help())
        raise typer.Exit()


# ----------------------------------------------------------------------
# Plugin: Dynamically load all tools from entry_points
# ----------------------------------------------------------------------
def load_plugins():
    """Load all tools registered under 'mytools.plugins' entry point."""
    plugins = {}
    eps = entry_points()
    # Python 3.10+ uses select(), older uses dict interface
    if hasattr(eps, "select"):
        group = eps.select(group="mytools.plugins")
    else:
        group = eps.get("mytools.plugins", [])
    for ep in group:
        try:
            tool_class = ep.load()
            plugins[ep.name] = tool_class
            logger.debug(f"Loaded plugin: {ep.name} -> {tool_class}")
        except Exception as e:
            logger.error(f"Failed to load plugin {ep.name}: {e}")
    return plugins

_plugins = load_plugins()

# ----------------------------------------------------------------------
# Register each plugin as a Typer subcommand
# ----------------------------------------------------------------------
for name, tool_class in _plugins.items():
    # Instantiate tool once (or you can lazy-load inside command)
    tool_instance = tool_class()

    # register the `run` method directly; a bound method's signature
    # excludes `self` so Typer can pick up any additional options defined
    # there.  We still supply the description as help text.
    app.command(name=name, help=tool_instance.description)(tool_instance.run)

# ----------------------------------------------------------------------
# Built‑in commands that don't need a plugin
# ----------------------------------------------------------------------
@app.command("list")
def list_tools():
    """📋 List all available tools with brief descriptions."""
    typer.echo("🔧 Available tools:\n")
    for name, tool_class in _plugins.items():
        desc = tool_class().description
        typer.echo(f"  • {name} – {desc}")
    typer.echo("\nUse `mytools <tool-name>` to run a tool.")

@app.command("info")
def info():
    """ℹ️  Show system information."""
    typer.echo(f"MyTools version: {__import__('mytools').__version__}")
    typer.echo(f"Python: {sys.version}")
    typer.echo(f"Config file: {settings.config_file or 'default'}")

# ----------------------------------------------------------------------
# If no command given, show help
# ----------------------------------------------------------------------
def main():
    if len(sys.argv) == 1:
        typer.echo(app.get_help())
    else:
        app()

if __name__ == "__main__":
    main()