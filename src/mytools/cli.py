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

    # Create a Typer command that calls tool.run()
    def make_cmd(tool):
        def cmd(ctx: typer.Context):
            """Run the tool."""
            tool.run()
        return cmd

    app.command(name=name)(make_cmd(tool_instance))

# ----------------------------------------------------------------------
# Built‑in commands that don't need a plugin
# ----------------------------------------------------------------------
@app.command("list")
def list_tools():
    """📋 List all available tools."""
    typer.echo("🔧 Available tools:\n")
    for name in _plugins:
        typer.echo(f"  • {name}")
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