"""Tool to generate optimized project context for AI assistance."""

import os
import fnmatch
from pathlib import Path
from typing import List, Set, Optional
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

from .base import BaseTool
from ..utils import logger, get_project_path, format_size

class FullContextTool(BaseTool):
    """Create optimized project context for AI assistance with flexible filtering."""

    name = "📄 Generate AI Context"
    description = "Create optimized project context with filtering options for AI"

    # Default ignore settings
    DEFAULT_IGNORE_DIRS = {
        ".git", ".github", ".gitlab",
        ".venv", "venv", "env", "virtualenv",
        "__pycache__", ".pytest_cache", ".mypy_cache",
        ".idea", ".vscode", ".vs",
        "node_modules", "bower_components",
        "dist", "build", "out", "target",
        "instance", ".extra", "migrations", "logs",
        "static/images", "media",
        "coverage", ".coverage",
        "site-packages", ".eggs", "eggs",
    }

    DEFAULT_IGNORE_FILES = {
        ".DS_Store", "Thumbs.db", "desktop.ini",
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        "full_project_context.txt", "ai_context.txt",
        "generate_context.py",
        "db.sqlite3", "database.db", "*.db",
        ".env", ".env.local", ".env.*",
        ".antigravityignore", ".gitignore",
        "requirements.txt", "requirements-dev.txt",
        "poetry.lock", "Pipfile.lock",
        "*.pyc", "*.pyo", "*.pyd",
        "*.so", "*.dll", "*.dylib",
        "*.log", "*.tmp", "*.temp",
        "*.cache", "*.swp", "*.swo",
    }

    # Prioritized extensions for AI understanding
    PRIORITY_EXTENSIONS = {
        ".py", ".js", ".jsx", ".ts", ".tsx",  # Code
        ".html", ".htm", ".css", ".scss", ".sass",  # Web
        ".json", ".yaml", ".yml", ".toml",  # Config
        ".md", ".txt", ".rst",  # Documentation
        ".sql", ".graphql", ".gql",  # Database
        ".java", ".cpp", ".c", ".h", ".hpp",  # Other languages
        ".go", ".rs", ".rb", ".php",
        ".cs", ".swift", ".kt", ".dart",
    }

    def run(self) -> None:
        """Execute the context generation process with user options."""
        console = Console()
        console.clear()
        console.rule("[bold magenta]🤖 AI-PROJECT CONTEXT GENERATOR[/]")
        
        project_path = get_project_path()
        project_name = os.path.basename(project_path)
        
        info_panel = (
            f"📁 [bold cyan]Project:[/] {project_name}\n"
            f"📍 [bold cyan]Location:[/] [dim]{project_path}[/]"
        )
        console.print(Panel(info_panel, border_style="cyan", expand=False))
        
        # User configuration
        config = self._get_user_config(console)
        
        # Generation Process
        with console.status("[magenta]🔍 Scanning project and generating context...[/]", spinner="dots"):
            tree_structure = self._generate_tree(project_path, config['ignore_dirs'])
            
            if config['selection_mode'] == 'custom':
                # Pause spinner for custom input
                console.print("\n")
                file_contents = self._get_custom_files_content(console, project_path, config)
            elif config['selection_mode'] == 'all':
                file_contents = self._get_all_files_content(project_path, config)
            else:  # smart
                file_contents = self._get_smart_files_content(project_path, config)
            
            final_output = self._format_output(project_name, tree_structure, file_contents, config)
        
        # Preview and Save
        self._show_preview(console, final_output)
        self._handle_save_options(console, project_name, final_output)
        
        console.input("\n[dim]Press Enter to continue...[/]")
    
    def _get_user_config(self, console: Console) -> dict:
        console.print("\n[bold]⚙️  Configuration Options:[/]")
        
        # Selection mode
        console.print("\n[bold cyan]1. File Selection Mode[/]")
        mode_text = (
            "[1] 🧠 Smart (recommended) - Key files only\n"
            "[2] 📚 All - All readable files\n"
            "[3] 🎯 Custom - Select specific files/folders"
        )
        console.print(Panel(mode_text, expand=False))
        mode_choice = Prompt.ask("Choose mode", choices=["1", "2", "3"], default="1")
        mode_map = {'1': 'smart', '2': 'all', '3': 'custom'}
        
        # Ignore Directories
        console.print("\n[bold cyan]2. Ignore Directories[/]")
        default_dirs_preview = ", ".join(sorted(list(self.DEFAULT_IGNORE_DIRS))[:5]) + "..."
        console.print(f"[dim]Default ignores:[/] {default_dirs_preview}")
        custom_ignore = Prompt.ask("Add more dirs to ignore (comma separated, leave empty to skip)", default="")
        
        ignore_dirs = set(self.DEFAULT_IGNORE_DIRS)
        if custom_ignore:
            ignore_dirs.update([d.strip() for d in custom_ignore.split(',') if d.strip()])
        
        # Ignore Files
        console.print("\n[bold cyan]3. Ignore File Patterns[/]")
        console.print("[dim]Default includes: *.log, *.tmp, .env*, etc.[/]")
        custom_files = Prompt.ask("Add more file patterns (comma separated, leave empty to skip)", default="")
        
        ignore_files = set(self.DEFAULT_IGNORE_FILES)
        if custom_files:
            ignore_files.update([f.strip() for f in custom_files.split(',') if f.strip()])
        
        return {
            'ignore_dirs': ignore_dirs,
            'ignore_files': ignore_files,
            'selection_mode': mode_map[mode_choice],
            'max_file_size': 20000,   # 20KB limit per file
            'max_total_size': 200000  # 200KB total limit
        }
    
    def _generate_tree(self, start_path: str, ignore_dirs: Set[str]) -> str:
        """Generate plain text tree structure (No rich tags for AI export)."""
        def _tree_recursive(path: Path, prefix: str = "", depth: int = 0, max_depth: int = 5) -> str:
            if depth > max_depth:
                return prefix + "└── [depth limit reached]\n"
            try:
                items = sorted(path.iterdir())
            except (PermissionError, OSError):
                return ""
            
            dirs = [i for i in items if i.is_dir() and not i.name.startswith('.') and i.name not in ignore_dirs]
            files = [i for i in items if i.is_file() and not i.name.startswith('.')]
            all_items = dirs + files
            
            tree_str = ""
            for idx, item in enumerate(all_items):
                is_last = idx == len(all_items) - 1
                connector = "└── " if is_last else "├── "
                icon = "📁 " if item.is_dir() else "📄 "
                tree_str += f"{prefix}{connector}{icon}{item.name}\n"
                
                if item.is_dir():
                    extension = "    " if is_last else "│   "
                    tree_str += _tree_recursive(item, prefix + extension, depth + 1, max_depth)
            return tree_str
            
        return f"Project Tree:\n{_tree_recursive(Path(start_path))}"
    
    def _get_smart_files_content(self, project_path: str, config: dict) -> str:
        important_patterns = [
            "README*", "readme*", "requirements*.txt", "pyproject.toml", "package.json",
            "setup.py", "setup.cfg", "*.py", "*.js", "*.ts", "*.jsx", "*.tsx",
            "*.html", "*.css", "*.json", "*.yaml", "*.yml",
        ]
        
        content_str, total_size = "", 0
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in config['ignore_dirs']]
            for file in files:
                if self._should_ignore_file(file, config['ignore_files']): continue
                if not self._is_important_file(file, important_patterns): continue
                
                path = os.path.join(root, file)
                content = self._read_file_safe(path, config['max_file_size'])
                if content:
                    rel_path = os.path.relpath(path, project_path)
                    total_size += len(content)
                    if total_size > config['max_total_size']:
                        return content_str + "\n\n[⚠️  Total size limit reached. Some files omitted.]\n"
                    content_str += self._format_file_content(rel_path, content)
        return content_str
    
    def _get_all_files_content(self, project_path: str, config: dict) -> str:
        content_str, total_size = "", 0
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in config['ignore_dirs']]
            for file in files:
                if self._should_ignore_file(file, config['ignore_files']): continue
                
                path = os.path.join(root, file)
                content = self._read_file_safe(path, config['max_file_size'])
                if content:
                    rel_path = os.path.relpath(path, project_path)
                    total_size += len(content)
                    if total_size > config['max_total_size']:
                        return content_str + "\n\n[⚠️  Total size limit reached. Some files omitted.]\n"
                    content_str += self._format_file_content(rel_path, content)
        return content_str
    
    def _get_custom_files_content(self, console: Console, project_path: str, config: dict) -> str:
        console.rule("[bold yellow]🎯 Custom File Selection[/]")
        console.print("Enter file/folder paths (relative to project). Type [bold green]'done'[/] when finished, or [bold blue]'tree'[/] to see structure.")
        
        selected_paths = []
        while True:
            user_input = Prompt.ask("\nEnter path").strip()
            
            if user_input.lower() == 'done': break
            elif user_input.lower() == 'tree':
                console.print("\n[dim]Current tree (first 2 levels):[/]")
                self._show_quick_tree(console, project_path, 2)
                continue
            
            if user_input:
                full_path = os.path.join(project_path, user_input)
                if os.path.exists(full_path):
                    selected_paths.append(full_path)
                    console.print(f"✅ [green]Added:[/] {user_input}")
                else:
                    console.print(f"❌ [red]Not found:[/] {user_input}")
        
        if not selected_paths:
            console.print("[yellow]No files selected. Falling back to Smart Selection.[/]")
            return self._get_smart_files_content(project_path, config)
            
        content_str, total_size = "", 0
        for selected_path in selected_paths:
            if os.path.isfile(selected_path):
                content = self._read_file_safe(selected_path, config['max_file_size'])
                if content:
                    rel_path = os.path.relpath(selected_path, project_path)
                    total_size += len(content)
                    content_str += self._format_file_content(rel_path, content)
            elif os.path.isdir(selected_path):
                for root, dirs, files in os.walk(selected_path):
                    dirs[:] = [d for d in dirs if d not in config['ignore_dirs']]
                    for file in files:
                        if self._should_ignore_file(file, config['ignore_files']): continue
                        path = os.path.join(root, file)
                        content = self._read_file_safe(path, config['max_file_size'])
                        if content:
                            rel_path = os.path.relpath(path, project_path)
                            total_size += len(content)
                            content_str += self._format_file_content(rel_path, content)
                            
            if total_size > config['max_total_size']:
                content_str += "\n\n[⚠️  Total size limit reached.]\n"
                break
                
        return content_str
    
    def _should_ignore_file(self, filename: str, ignore_patterns: Set[str]) -> bool:
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False
    
    def _is_important_file(self, filename: str, patterns: List[str]) -> bool:
        for pattern in patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.PRIORITY_EXTENSIONS
    
    def _read_file_safe(self, filepath: str, max_size: int) -> Optional[str]:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_size * 2)
                if len(content) > max_size:
                    content = content[:max_size] + "\n\n...[File truncated due to size limit]..."
                return content if content.strip() else None
        except Exception as e:
            return f"[Error reading file: {e}]"
    
    def _format_file_content(self, rel_path: str, content: str) -> str:
        separator = "=" * 60
        return f"\n{separator}\n📄 FILE: {rel_path}\n{separator}\n{content}\n"
    
    def _format_output(self, project_name: str, tree: str, contents: str, config: dict) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""🤖 PROJECT CONTEXT FOR AI ASSISTANCE
{'=' * 60}
PROJECT: {project_name}
SELECTION MODE: {config['selection_mode'].upper()}
GENERATED: {timestamp}
{'=' * 60}

📁 PROJECT STRUCTURE:
{tree}

{'=' * 60}
📝 FILE CONTENTS:
{contents}

{'=' * 60}
💡 FOR AI ASSISTANT:
This is the complete context of the project. Please analyze the structure
and code to provide accurate assistance. Key files include configuration
files, source code, and documentation.

When responding, reference specific files and paths from the structure above.
"""
    
    def _show_preview(self, console: Console, output: str) -> None:
        console.rule("[bold cyan]📋 CONTEXT PREVIEW[/]")
        lines = output.split('\n')
        preview_text = '\n'.join(lines[:30])
        
        if len(lines) > 30:
            preview_text += f"\n\n[dim]... (Showing first 30 of {len(lines)} lines) ...[/]"
            
        console.print(Panel(preview_text, border_style="cyan", title="Preview Output"))
        
        table = Table(show_header=False, box=None)
        table.add_row("Total lines:", str(len(lines)))
        table.add_row("Approx. size:", format_size(len(output.encode('utf-8'))))
        console.print(Panel(table, title="📊 Statistics", expand=False))
    
    def _show_quick_tree(self, console: Console, path: str, depth: int = 2) -> None:
        def _quick_tree(p: Path, current_depth: int, max_depth: int):
            if current_depth > max_depth: return
            prefix = "  " * current_depth
            try:
                for item in sorted(p.iterdir()):
                    if item.name.startswith('.'): continue
                    icon = "📁" if item.is_dir() else "📄"
                    console.print(f"{prefix}{icon} {item.name}")
                    if item.is_dir():
                        _quick_tree(item, current_depth + 1, max_depth)
            except: pass
        _quick_tree(Path(path), 0, depth)
    
    def _handle_save_options(self, console: Console, project_name: str, content: str) -> None:
        console.print("\n[bold]💾 Save Options:[/]")
        options = (
            "[1] Save full context\n"
            "[2] Save only specific section\n"
            "[3] Save as AI prompt template\n"
            "[4] Don't save (Exit)"
        )
        console.print(Panel(options, expand=False))
        
        choice = Prompt.ask("Choose option", choices=["1", "2", "3", "4"], default="1")
        if choice == '4': return
        
        default_filename = f"{project_name}_context.txt"
        filename = Prompt.ask("Enter filename", default=default_filename)
        
        if choice == '1':
            save_content = content
        elif choice == '2':
            section = Prompt.ask("Save [1] Structure only or [2] Contents only?", choices=["1", "2"], default="1")
            lines = content.split('\n')
            if section == '1':
                start = next(i for i, line in enumerate(lines) if "PROJECT STRUCTURE:" in line)
                end = next((i for i, line in enumerate(lines[start+1:]) if "="*60 in line), len(lines))
                save_content = '\n'.join(lines[start:start+end+1])
            else:
                start = next(i for i, line in enumerate(lines) if "FILE CONTENTS:" in line)
                save_content = '\n'.join(lines[start:])
        else:
            save_content = self._create_ai_prompt_template(content)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(save_content)
            
            console.print(f"\n✅ [bold green]Saved successfully to:[/] {os.path.abspath(filename)}")
            
            if choice == '3':
                console.print("\n[bold magenta]🤖 AI Prompt Suggestion:[/]")
                prompt_preview = save_content[:300] + "...\n[dim][Full prompt saved in file][/]"
                console.print(Panel(prompt_preview, border_style="magenta"))
                
        except Exception as e:
            console.print(f"[red]❌ Error saving file: {e}[/]")
    
    def _create_ai_prompt_template(self, context: str) -> str:
        return f"""You are an expert developer assistant. Below is the complete context of a project. Please analyze it thoroughly and provide accurate assistance.

PROJECT CONTEXT:
{context}

YOUR TASK:
Based on the project structure and code above, please:
1. Understand the project architecture and main components.
2. Identify key files, dependencies, and configuration.
3. Provide specific, actionable advice or code.

My specific request is: [DESCRIBE WHAT YOU NEED HELP WITH HERE]

Please reference specific files and paths from the project structure in your response. Be detailed but concise."""
    