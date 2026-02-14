"""Django project and app management tool."""

import os
import subprocess
import sys
from typing import Tuple, Optional
from pathlib import Path

import typer
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from .base import BaseTool
from ..utils import console, logger, get_project_path

class DjangoTool(BaseTool):
    """Manage Django projects and apps interactively."""

    name = "🚀 Django Manager"
    description = "Interactive menu to create project, apps, migrate, runserver"

    def run(self, pause: bool = typer.Option(True, "--pause/--no-pause", help="Wait for Enter between steps")) -> None:
        """Display Django management menu."""
        while True:
            console.clear()
            console.rule("[bold green]🚀 DJANGO PROJECT MANAGER[/]")

            menu_text = (
                "[1] 📁 Create Django Project\n"
                "[2] 🔍 Check Django Installation\n"
                "[3] 📦 Create Django App\n"
                "[4] 🛠️  Make Migrations\n"
                "[5] 🔄 Apply Migrations\n"
                "[6] 🌐 Run Development Server\n"
                "[7] 🚪 Back to Main Menu"
            )
            console.print(Panel(menu_text, border_style="green", expand=False))

            choice = Prompt.ask("\n[bold cyan]Select an option[/]", choices=[str(i) for i in range(1, 8)])

            if choice == "1":
                self.create_project()
            elif choice == "2":
                self.check_django()
            elif choice == "3":
                self.create_app()
            elif choice == "4":
                self.make_migrations()
            elif choice == "5":
                self.migrate()
            elif choice == "6":
                self.run_server()
            elif choice == "7":
                break

            if choice != "7" and pause:
                console.input("\n[dim]Press Enter to continue...[/]")

    # ----------------------------------------------------------------
    # CORE METHODS (Can be called directly by shortcuts)
    # ----------------------------------------------------------------

    def create_project(self) -> None:
        console.clear()
        console.rule("[bold green]CREATE DJANGO PROJECT[/]")

        current_dir = get_project_path()
        console.print(f"📂 [bold]Current directory:[/] [dim]{current_dir}[/]\n")
        
        console.print("[yellow]ℹ️  This will create a new Django project here.[/]")
        if not Confirm.ask("Do you want to continue?"):
            console.print("[red]❌ Operation cancelled.[/]")
            return

        project_name = Prompt.ask("Enter project name").strip()
        
        with console.status(f"[cyan]🚀 Creating Django project '{project_name}'...[/]"):
            success, output = self._run_command(["django-admin", "startproject", project_name])

        if success:
            console.print(f"\n✅ [bold green]Project '{project_name}' created successfully![/]")
            console.print(f"📁 [bold]Location:[/] {os.path.join(current_dir, project_name)}\n")
            
            steps = (
                f"1. cd {project_name}\n"
                f"2. python manage.py migrate\n"
                f"3. python manage.py runserver"
            )
            console.print(Panel(steps, title="📋 Next steps", border_style="cyan", expand=False))
        else:
            console.print(f"[red]❌ Failed to create project:[/] {output}")

    def check_django(self) -> None:
        console.clear()
        console.rule("[bold green]CHECK DJANGO INSTALLATION[/]")

        with console.status("[cyan]🔍 Checking Django...[/]"):
            success, output = self._run_command([sys.executable, "-m", "django", "--version"])
        
        if success:
            console.print(f"✅ [bold green]Django {output.strip()} is installed and working.[/]")
            try:
                import django
                console.print(f"📦 [dim]Module path: {django.__file__}[/]")
            except ImportError as e:
                console.print(f"[yellow]⚠️  Django import issue:[/] {e}")
        else:
            console.print("[red]❌ Django is not installed or not in PATH.[/]")
            console.print("\n💡 [bold]Installation commands:[/]")
            console.print("   [cyan]pip install django[/]")

    def create_app(self) -> None:
        console.clear()
        console.rule("[bold green]CREATE DJANGO APP[/]")

        project_dir = self._find_django_project()
        if not project_dir:
            console.print("[red]❌ Not in a Django project directory (manage.py not found).[/]")
            return

        app_name = Prompt.ask("Enter app name").strip()
        
        original_dir = os.getcwd()
        os.chdir(project_dir)
        
        with console.status(f"[cyan]🚀 Creating app '{app_name}'...[/]"):
            success, output = self._run_command([sys.executable, "manage.py", "startapp", app_name])
            
        os.chdir(original_dir)

        if success:
            console.print(f"\n✅ [bold green]App '{app_name}' created successfully![/]")
            steps = (
                f"1. Add '{app_name}' to INSTALLED_APPS in settings.py\n"
                f"2. Create models in {app_name}/models.py\n"
                f"3. python manage.py makemigrations {app_name}\n"
                f"4. python manage.py migrate"
            )
            console.print(Panel(steps, title="📋 Next steps", border_style="cyan", expand=False))
        else:
            console.print(f"[red]❌ Failed to create app:[/] {output}")

    def make_migrations(self) -> None:
        console.clear()
        console.rule("[bold green]MAKE MIGRATIONS[/]")

        project_dir = self._find_django_project()
        if not project_dir:
            console.print("[red]❌ manage.py not found. Are you in a Django project?[/]")
            return

        app_name = Prompt.ask("Enter app name [dim](leave empty for all apps)[/]", default="")
        cmd = [sys.executable, "manage.py", "makemigrations"]
        if app_name:
            cmd.append(app_name)

        original_dir = os.getcwd()
        os.chdir(project_dir)
        
        with console.status("[cyan]🔨 Generating migrations...[/]"):
            success, output = self._run_command(cmd)
            
        os.chdir(original_dir)

        if success:
            console.print("✅ [bold green]Migrations created successfully![/]")
            if output:
                console.print(f"\n[dim]{output}[/]")
        else:
            console.print(f"[red]❌ Failed:[/] {output}")

    def migrate(self) -> None:
        console.clear()
        console.rule("[bold green]APPLY MIGRATIONS[/]")

        project_dir = self._find_django_project()
        if not project_dir:
            console.print("[red]❌ manage.py not found.[/]")
            return

        if not Confirm.ask("Apply all pending migrations?"):
            return

        original_dir = os.getcwd()
        os.chdir(project_dir)
        
        with console.status("[cyan]🔄 Applying migrations to database...[/]"):
            success, output = self._run_command([sys.executable, "manage.py", "migrate"])
            
        os.chdir(original_dir)

        if success:
            console.print("✅ [bold green]Migrations applied successfully![/]")
            if output:
                lines = output.strip().split('\n')
                console.print("\n[dim]" + "\n".join(lines[-10:]) + "[/]")
        else:
            console.print(f"[red]❌ Migration failed:[/] {output}")

    def run_server(self) -> None:
        console.clear()
        console.rule("[bold green]RUN DEVELOPMENT SERVER[/]")

        project_dir = self._find_django_project()
        if not project_dir:
            console.print("[red]❌ manage.py not found. Please navigate to your project root.[/]")
            return

        port = Prompt.ask("Enter port number", default="8000")

        console.print(f"\n🌐 [bold cyan]Starting server on port {port}...[/]")
        console.print("[dim]Press Ctrl+C to stop the server[/]\n")

        original_dir = os.getcwd()
        os.chdir(project_dir)
        
        try:
            subprocess.run([sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}"])
        except KeyboardInterrupt:
            console.print("\n\n🛑 [yellow]Server stopped by user.[/]")
        except Exception as e:
            console.print(f"[red]❌ Error running server:[/] {e}")
        finally:
            os.chdir(original_dir)

    def _find_django_project(self) -> Optional[str]:
        current_dir = os.getcwd()
        check_dir = current_dir
        for _ in range(5):
            if os.path.exists(os.path.join(check_dir, "manage.py")):
                return check_dir
            parent = os.path.dirname(check_dir)
            if parent == check_dir:
                break
            check_dir = parent
        return None

    def _run_command(self, cmd: list, shell: bool = False) -> Tuple[bool, str]:
        try:
            result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, result.stderr.strip() or result.stdout.strip() or "Unknown error"
        except Exception as e:
            return False, str(e)


# =====================================================================
# SHORTCUT CLI TOOLS (For Direct Commands)
# =====================================================================

class DjRunTool(BaseTool):
    name = "dj-run"
    description = "Shortcut: Directly start the Django development server"
    
    def run(self) -> None:
        DjangoTool().run_server()

class DjMigrateTool(BaseTool):
    name = "dj-migrate"
    description = "Shortcut: Apply Django database migrations"
    
    def run(self) -> None:
        DjangoTool().migrate()

class DjMakeMigrationsTool(BaseTool):
    name = "dj-makemigrations"
    description = "Shortcut: Create new Django migrations"
    
    def run(self) -> None:
        DjangoTool().make_migrations()

class DjAppTool(BaseTool):
    name = "dj-app"
    description = "Shortcut: Create a new Django app"
    
    def run(self) -> None:
        DjangoTool().create_app()