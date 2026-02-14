"""Tool to clean __pycache__ directories."""
import os
import shutil
from pathlib import Path

from rich.progress import track
from rich.console import Console

from ..utils import logger, format_size, get_project_path
from .base import BaseTool

class CleanPycacheTool(BaseTool):
    name = "🧹 Clean __pycache__"
    description = "Remove all __pycache__ folders recursively"

    def run(self) -> None:
        # from ..cli import console  # lazy import to avoid circular
        console = Console()

        console.clear()
        console.rule("[bold blue]CLEAN PYTHON CACHE[/]")

        start_path = get_project_path()
        console.print(f"🔍 Cleaning in: [cyan]{start_path}[/]")

        if not console.input("\n⚠️  [yellow]Delete all __pycache__ folders?[/] (y/n): ").lower() == "y":
            console.print("[red]❌ Operation cancelled.[/]")
            return

        deleted = 0
        total_size = 0

        # Use os.walk, but we can also use Path.rglob
        for root, dirs, _ in os.walk(start_path):
            if "__pycache__" in dirs:
                path = Path(root) / "__pycache__"
                try:
                    folder_size = self._folder_size(path)
                    shutil.rmtree(path, ignore_errors=True)
                    dirs.remove("__pycache__")
                    deleted += 1
                    total_size += folder_size
                    rel_path = path.relative_to(start_path)
                    console.print(f"✅ Deleted: [dim]{rel_path}[/] [green]({format_size(folder_size)})[/]")
                except Exception as e:
                    logger.error(f"Failed to delete {path}: {e}")

        if deleted:
            console.print("\n[bold green]🎯 Summary:[/]")
            console.print(f"   • Folders deleted: {deleted}")
            console.print(f"   • Space freed: {format_size(total_size)}")
        else:
            console.print("\n[blue]ℹ️  No __pycache__ folders found.[/]")

        console.input("\nPress Enter to continue...")

    @staticmethod
    def _folder_size(path: Path) -> int:
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())