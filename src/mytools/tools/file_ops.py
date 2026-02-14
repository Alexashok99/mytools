"""Tool for file and folder operations."""
import os
import shutil
import stat
import time
from pathlib import Path
from typing import List

from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.panel import Panel

from .base import BaseTool
from ..utils import logger, get_project_path, format_size

class FileOperationsTool(BaseTool):
    """Perform file and folder operations."""

    name = "📁 File Operations"
    description = "List, copy, move, delete files and folders"

    def run(self) -> None:
        """Display file operations menu."""
        console = Console()
        
        while True:
            console.clear()
            console.rule("[bold cyan]📁 FILE OPERATIONS[/]")

            menu_text = (
                "[1] 📋 List all project files (for copy path)\n"
                "[2] 📄 Copy file/folder\n"
                "[3] 🚚 Move file/folder\n"
                "[4] 🗑️  Delete file/folder\n"
                "[5] ℹ️  File information\n"
                "[6] 📁 Create new folder\n"
                "[7] 📝 Create new file\n"
                "[8] 🚪 Back to Main Menu"
            )
            console.print(Panel(menu_text, border_style="cyan", expand=False))

            choice = Prompt.ask("\n[bold cyan]Select an option[/]", choices=[str(i) for i in range(1, 9)])

            if choice == "1":
                self._list_project_files(console)
            elif choice == "2":
                self._copy_file_folder(console)
            elif choice == "3":
                self._move_file_folder(console)
            elif choice == "4":
                self._delete_file_folder(console)
            elif choice == "5":
                self._file_info(console)
            elif choice == "6":
                self._create_folder(console)
            elif choice == "7":
                self._create_file(console)
            elif choice == "8":
                break

            if choice != "8":
                console.input("\n[dim]Press Enter to continue...[/]")

    def _list_project_files(self, console: Console) -> None:
        console.clear()
        console.rule("[bold cyan]LIST PROJECT FILES[/]")

        current_dir = get_project_path()
        console.print(f"📍 [bold]Current directory:[/] [dim]{current_dir}[/]\n")

        all_files = []
        total_size = 0

        with console.status("[cyan]🔍 Scanning files...[/]", spinner="dots"):
            for root, dirs, files in os.walk(current_dir):
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for file in files:
                    if file.startswith("."):
                        continue

                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        rel_path = os.path.relpath(file_path, current_dir)
                        all_files.append({"path": rel_path, "size": file_size, "full_path": file_path})
                        total_size += file_size
                    except (OSError, PermissionError):
                        continue

        if not all_files:
            console.print("[red]❌ No files found.[/]")
            return

        all_files.sort(key=lambda x: x["path"])
        console.print(f"📊 [bold green]Found {len(all_files)} files[/] ({format_size(total_size)})")

        options = (
            "[1] Show all files with details\n"
            "[2] Show only file paths (for copying)\n"
            "[3] Search for specific files\n"
            "[4] Export list to file"
        )
        console.print(Panel(options, title="📋 Display options", expand=False))
        
        display_choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="1")

        if display_choice == "1":
            self._show_files_with_details(console, all_files)
        elif display_choice == "2":
            self._show_file_paths_only(console, all_files)
        elif display_choice == "3":
            self._search_files(console, all_files)
        elif display_choice == "4":
            self._export_file_list(console, all_files, current_dir)

    def _show_files_with_details(self, console: Console, files: List[dict]) -> None:
        table = Table(title="📄 Files with details", header_style="bold magenta")
        table.add_column("No.", style="dim", width=6)
        table.add_column("Size", style="green", justify="right")
        table.add_column("Path", style="cyan")

        for idx, file_info in enumerate(files, 1):
            if idx <= 100:
                table.add_row(str(idx), format_size(file_info["size"]), file_info['path'])
            else:
                table.add_row("...", "...", f"[dim]and {len(files) - 100} more files[/]")
                break

        console.print(table)

        if files:
            console.print("\n[bold]📋 Copy options:[/]")
            choice = Prompt.ask("Enter file number to copy, 'a' for all, 'q' to quit", default="q").lower()

            if choice == "a":
                self._copy_all_paths(console, files)
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    self._copy_to_clipboard(files[idx]["path"])
                    console.print(f"✅ [green]Copied:[/] {files[idx]['path']}")
                else:
                    console.print("[red]❌ Invalid file number[/]")

    def _show_file_paths_only(self, console: Console, files: List[dict]) -> None:
        console.print("\n[bold]📄 File paths only:[/]")
        for idx, file_info in enumerate(files[:50], 1):
            console.print(file_info['path'])
            
        if len(files) > 50:
            console.print(f"[dim]... and {len(files) - 50} more files[/]")

        if files and Confirm.ask("\n📋 Copy all paths to file?"):
            self._copy_all_paths(console, files)

    def _search_files(self, console: Console, files: List[dict]) -> None:
        search_choice = Prompt.ask("\n🔍 Search by", choices=["1", "2", "3"], default="1")
        # 1: Name, 2: Extension, 3: Size
        
        results = []
        if search_choice == "1":
            term = Prompt.ask("Enter filename part").lower()
            results = [f for f in files if term in f["path"].lower()]
        elif search_choice == "2":
            ext = Prompt.ask("Enter extension (e.g. .py)").lower()
            if not ext.startswith("."): ext = "." + ext
            results = [f for f in files if f["path"].lower().endswith(ext)]
        elif search_choice == "3":
            min_kb = IntPrompt.ask("Min size in KB", default=0) * 1024
            max_kb = IntPrompt.ask("Max size in KB (0 for no limit)", default=0) * 1024
            max_kb = max_kb if max_kb > 0 else float('inf')
            results = [f for f in files if min_kb <= f["size"] <= max_kb]

        if not results:
            console.print("[red]❌ No files found.[/]")
            return

        console.print(f"\n📊 [bold green]{len(results)} files found[/]")
        self._show_files_with_details(console, results)

    def _export_file_list(self, console: Console, files: List[dict], current_dir: str) -> None:
        filename = Prompt.ask("\nEnter output filename", default="file_list.txt")
        fmt = Prompt.ask("Format [1] Simple [2] Detailed [3] CSV", choices=["1", "2", "3"], default="2")

        try:
            with open(filename, "w", encoding="utf-8") as f:
                if fmt == "3":
                    f.write("Path,Size(bytes),Size(human)\n")
                    for file in files:
                        f.write(f'"{file["path"]}",{file["size"]},"{format_size(file["size"])}"\n')
                else:
                    for file in files:
                        size_str = format_size(file["size"]) if fmt == "2" else ""
                        f.write(f"{size_str:<12} {file['path']}\n" if fmt == "2" else f"{file['path']}\n")

            console.print(f"✅ [green]Exported to:[/] {os.path.abspath(filename)}")
        except Exception as e:
            console.print(f"[red]❌ Export failed: {e}[/]")

    def _copy_all_paths(self, console: Console, files: List[dict]) -> None:
        all_paths = "\n".join(f["path"] for f in files)
        if self._copy_to_clipboard(all_paths):
            console.print(f"✅ [green]Copied {len(files)} paths to clipboard[/]")
        else:
            console.print("[yellow]⚠️ Clipboard not available. Showing paths:[/]")
            console.print(all_paths[:500] + ("..." if len(all_paths) > 500 else ""))

    def _copy_file_folder(self, console: Console) -> None:
        console.clear()
        console.rule("[bold cyan]COPY FILE/FOLDER[/]")
        current_dir = get_project_path()

        source = Prompt.ask("Enter source path").strip()
        source = source if os.path.isabs(source) else os.path.join(current_dir, source)

        if not os.path.exists(source):
            console.print(f"[red]❌ Source not found:[/] {source}")
            return

        dest_suggestion = f"copy_of_{os.path.basename(source)}"
        dest = Prompt.ask("Enter destination path", default=dest_suggestion).strip()
        dest = dest if os.path.isabs(dest) else os.path.join(current_dir, dest)

        if os.path.exists(dest) and not Confirm.ask("[yellow]Destination exists. Overwrite?[/]"):
            return

        if Confirm.ask(f"Confirm copy to {os.path.basename(dest)}?"):
            with console.status("[cyan]Copying...[/]"):
                try:
                    if os.path.isfile(source): shutil.copy2(source, dest)
                    else: shutil.copytree(source, dest, dirs_exist_ok=True)
                    console.print("✅ [green]Copied successfully![/]")
                except Exception as e:
                    console.print(f"[red]❌ Copy failed: {e}[/]")

    def _move_file_folder(self, console: Console) -> None:
        console.clear()
        console.rule("[bold cyan]MOVE FILE/FOLDER[/]")
        current_dir = get_project_path()

        source = Prompt.ask("Enter source path").strip()
        source = source if os.path.isabs(source) else os.path.join(current_dir, source)

        if not os.path.exists(source):
            console.print("[red]❌ Source not found.[/]")
            return

        dest_dir = Prompt.ask("Enter destination directory").strip()
        dest_dir = dest_dir if os.path.isabs(dest_dir) else os.path.join(current_dir, dest_dir)

        if not os.path.exists(dest_dir) and Confirm.ask("Directory doesn't exist. Create it?"):
            os.makedirs(dest_dir, exist_ok=True)

        dest = os.path.join(dest_dir, os.path.basename(source))

        if Confirm.ask(f"Confirm move to {dest_dir}?"):
            with console.status("[cyan]Moving...[/]"):
                try:
                    shutil.move(source, dest)
                    console.print("✅ [green]Moved successfully![/]")
                except Exception as e:
                    console.print(f"[red]❌ Move failed: {e}[/]")

    def _delete_file_folder(self, console: Console) -> None:
        console.clear()
        console.rule("[bold red]DELETE FILE/FOLDER[/]")
        current_dir = get_project_path()

        target = Prompt.ask("Enter path to delete").strip()
        target = target if os.path.isabs(target) else os.path.join(current_dir, target)

        if not os.path.exists(target):
            console.print("[red]❌ Path not found.[/]")
            return

        is_file = os.path.isfile(target)
        size = self._get_path_size(target)

        info = f"[bold]Path:[/] {target}\n[bold]Type:[/] {'File' if is_file else 'Folder'}\n[bold]Size:[/] {format_size(size)}"
        console.print(Panel(info, border_style="yellow"))

        important_paths = [os.path.expanduser("~"), "/", "C:\\", os.getcwd()]
        if any(target == p for p in important_paths):
            console.print("\n[bold red]⚠️ DANGER: You are trying to delete a critical system/project path![/]")
            if Prompt.ask("Type 'YES' to force delete") != "YES":
                return

        if Confirm.ask("[bold red]Are you absolutely sure you want to delete this?[/]"):
            with console.status("[red]Deleting...[/]"):
                try:
                    if is_file: os.remove(target)
                    else: shutil.rmtree(target, ignore_errors=True)
                    console.print(f"✅ [green]Deleted:[/] {target}")
                except Exception as e:
                    console.print(f"[red]❌ Deletion failed: {e}[/]")

    def _file_info(self, console: Console) -> None:
        console.clear()
        console.rule("[bold cyan]FILE INFORMATION[/]")
        target = Prompt.ask("Enter path").strip()
        
        if not os.path.exists(target):
            console.print("[red]❌ Path not found.[/]")
            return

        path_obj = Path(target)
        size = self._get_path_size(target)
        
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold cyan")
        table.add_column("Value")
        
        table.add_row("Name:", path_obj.name)
        table.add_row("Type:", "File" if path_obj.is_file() else "Folder")
        table.add_row("Size:", f"{format_size(size)} ({size:,} bytes)")
        table.add_row("Created:", time.ctime(os.path.getctime(target)))
        table.add_row("Modified:", time.ctime(os.path.getmtime(target)))
        
        console.print(Panel(table, title="ℹ️ Details", expand=False))

    def _create_folder(self, console: Console) -> None:
        console.clear()
        console.rule("[bold cyan]CREATE FOLDER[/]")
        current_dir = get_project_path()

        name = Prompt.ask("Enter folder name").strip()
        path = name if os.path.isabs(name) else os.path.join(current_dir, name)

        if os.path.exists(path):
            console.print("[yellow]⚠️ Folder already exists.[/]")
            return

        try:
            os.makedirs(path, exist_ok=True)
            console.print(f"✅ [green]Folder created:[/] {path}")
            if Confirm.ask("Create README.md inside?"):
                with open(os.path.join(path, "README.md"), "w") as f:
                    f.write(f"# {os.path.basename(name)}\n")
                console.print("✅ [green]README.md created.[/]")
        except Exception as e:
            console.print(f"[red]❌ Failed: {e}[/]")

    def _create_file(self, console: Console) -> None:
        console.clear()
        console.rule("[bold cyan]CREATE FILE[/]")
        current_dir = get_project_path()

        name = Prompt.ask("Enter file name (with ext)").strip()
        path = name if os.path.isabs(name) else os.path.join(current_dir, name)

        if os.path.exists(path) and not Confirm.ask("[yellow]File exists. Overwrite?[/]"):
            return

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        content_choice = Prompt.ask("Content [1] Empty [2] Template", choices=["1", "2"], default="2")
        content = self._get_file_template(os.path.splitext(name)[1].lower(), os.path.basename(name)) if content_choice == "2" else ""

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            console.print(f"✅ [green]File created:[/] {path}")
        except Exception as e:
            console.print(f"[red]❌ Failed: {e}[/]")

    def _get_file_template(self, extension: str, filename: str) -> str:
        name = os.path.splitext(filename)[0]
        templates = {
            ".py": f'def main():\n    print("Hello from {name}")\n\nif __name__ == "__main__":\n    main()',
            ".html": f'<!DOCTYPE html>\n<html>\n<head><title>{name}</title></head>\n<body><h1>{name}</h1></body>\n</html>',
            ".js": f'console.log("{name} loaded");',
            ".md": f'# {name}\n\nDescription here.',
            ".json": '{\n    "key": "value"\n}'
        }
        return templates.get(extension, "")

    @staticmethod
    def _get_path_size(path: str) -> int:
        if os.path.isfile(path): return os.path.getsize(path)
        return sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(path) for f in fs if os.path.exists(os.path.join(d, f)))

    @staticmethod
    def _copy_to_clipboard(text: str) -> bool:
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except: return False