"""Count files and folders by extension and size."""
import os
from collections import defaultdict

from rich.table import Table
from rich.panel import Panel

from .base import BaseTool
# Assuming format_size is in your utils from the previous tool
from ..utils import console, logger, get_project_path, format_size

class FileCounterTool(BaseTool):
    name = "📊 File Statistics"
    description = "Count files and folders by type and show size"

    def run(self) -> None:
        """Execute the file counting process."""
        console.clear()
        console.rule("[bold magenta]FILE STATISTICS[/]")

        project_path = get_project_path()

        # Folders that we don't want to count
        IGNORED_DIRS = {".git", "__pycache__", "node_modules", "venv", ".venv", ".idea"}

        # Dictionary to store both count and size for each extension
        file_stats = defaultdict(lambda: {"count": 0, "size": 0})
        total_files = 0
        total_dirs = 0
        total_size = 0

        # Scanning the directory
        with console.status("[cyan]Scanning project files...[/]", spinner="dots"):
            for root, dirs, files in os.walk(project_path):
                # Modify dirs in-place to skip ignored directories
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

                total_dirs += len(dirs)
                total_files += len(files)

                for file in files:
                    filepath = os.path.join(root, file)
                    ext = os.path.splitext(file)[1].lower() or "[no extension]"
                    
                    try:
                        size = os.path.getsize(filepath)
                    except OSError:
                        size = 0  # Ignore files that can't be read

                    file_stats[ext]["count"] += 1
                    file_stats[ext]["size"] += size
                    total_size += size

        # -----------------------------------------
        # DISPLAY RESULTS
        # -----------------------------------------
        
        # 1. Summary Panel
        summary_text = (
            f"📁 [bold]Project:[/] {os.path.basename(project_path)}\n"
            f"📍 [bold]Path:[/] [dim]{project_path}[/]\n\n"
            f"📂 [bold]Total Folders:[/] [cyan]{total_dirs}[/]\n"
            f"📄 [bold]Total Files:[/] [cyan]{total_files}[/]\n"
            f"💾 [bold]Total Size:[/] [green]{format_size(total_size)}[/]"
        )
        console.print("\n")
        console.print(Panel(summary_text, title="🎯 Project Summary", border_style="blue", expand=False))

        # 2. Detailed Table by Extension
        table = Table(title="📊 Files by Extension", header_style="bold magenta")
        table.add_column("Extension", style="cyan", no_wrap=True)
        table.add_column("File Count", justify="right", style="yellow")
        table.add_column("Total Size", justify="right", style="green")

        # Sort extensions by count (highest first)
        sorted_stats = sorted(file_stats.items(), key=lambda x: x[1]["count"], reverse=True)

        for ext, data in sorted_stats:
            table.add_row(
                ext,
                str(data["count"]),
                format_size(data["size"])
            )

        console.print("\n")
        console.print(table)

        console.input("\n[dim]Press Enter to continue...[/]")