"""Virtual environment and .env file manager."""

import os
import shutil
import sys
from pathlib import Path
from typing import Optional, Tuple, List
import subprocess

from .base import BaseTool
from ..utils import console, logger


class EnvTool(BaseTool):
    """Manage virtual environments and environment files."""

    name = "🐍 Environment Manager"
    description = "Create/delete virtual env, manage .env files"

    def run(self) -> None:
        """Display environment management menu."""
        while True:
            console.clear()
            console.rule("[bold yellow]ENVIRONMENT MANAGER[/]")
            
            console.print("\n[bold cyan]1.[/] Create Virtual Environment (.venv)")
            console.print("[bold cyan]2.[/] Delete Virtual Environment")
            console.print("[bold cyan]3.[/] Create .env File")
            console.print("[bold cyan]4.[/] Delete .env File")
            console.print("[bold cyan]5.[/] List Environment Variables")
            console.print("[bold cyan]6.[/] Check Python Environment")
            console.print("[bold cyan]7.[/] Back to Main Menu")
            
            choice = console.input("\n[bold]Select option (1-7): [/]").strip()

            if choice == "1":
                self._create_venv()
            elif choice == "2":
                self._delete_venv()
            elif choice == "3":
                self._create_env_file()
            elif choice == "4":
                self._delete_env_file()
            elif choice == "5":
                self._list_env_vars()
            elif choice == "6":
                self._check_python_env()
            elif choice == "7":
                break
            else:
                console.print("[red]❌ Invalid option[/]")

            if choice != "7":
                console.input("\n[dim]Press Enter to continue...[/]")

    def _create_venv(self) -> None:
        """Create a virtual environment."""
        console.clear()
        console.rule("[bold cyan]CREATE VIRTUAL ENVIRONMENT[/]")

        current_dir = Path.cwd()
        console.print(f"[blue]📂[/] Current directory: [cyan]{current_dir}[/]")

        console.print("\n[bold]🔧 Virtual Environment Options:[/]")
        console.print("   [cyan]1.[/] .venv [dim](Recommended)[/]")
        console.print("   [cyan]2.[/] venv")
        console.print("   [cyan]3.[/] Custom name")

        choice = console.input("\n[bold]Select option (1-3): [/]").strip()

        if choice == "1":
            venv_name = ".venv"
        elif choice == "2":
            venv_name = "venv"
        elif choice == "3":
            venv_name = console.input("[bold]Enter virtual environment name: [/]").strip()
            if not venv_name:
                console.print("[red]❌ Name cannot be empty.[/]")
                return
        else:
            console.print("[red]❌ Invalid option.[/]")
            return

        venv_path = current_dir / venv_name

        # Check if already exists
        if venv_path.exists():
            console.print(f"[yellow]⚠️  Virtual environment '{venv_name}' already exists.[/]")
            overwrite = console.input("[bold]Delete and recreate? (y/n): [/]").lower()
            if overwrite != 'y':
                console.print("[red]❌ Operation cancelled.[/]")
                return
            shutil.rmtree(venv_path, ignore_errors=True)
            console.print(f"[green]✅ Existing '{venv_name}' deleted.[/]")

        console.print(f"\n[bold]🚀 Creating virtual environment '{venv_name}'...[/]")

        # Use sys.executable to ensure using current Python
        success, output = self._run_command([sys.executable, "-m", "venv", str(venv_name)])

        if success:
            console.print(f"[green]✅ Virtual environment created at: {venv_path}[/]")
            
            # Show activation commands
            console.print("\n[bold]🔧 Activation commands:[/]")
            if os.name == 'nt':  # Windows
                console.print(f"   [cyan]{venv_name}\\Scripts\\activate[/]")
            else:  # Unix/Linux/Mac
                console.print(f"   [cyan]source {venv_name}/bin/activate[/]")
            
            # Offer to install requirements if exists
            req_file = current_dir / "requirements.txt"
            if req_file.exists():
                install_req = console.input(f"\n[bold]📦 Install from requirements.txt? (y/n): [/]").lower()
                if install_req == 'y':
                    self._install_requirements(venv_path, req_file)
        else:
            console.print(f"[red]❌ Failed to create virtual environment: {output}[/]")
            logger.error(f"Venv creation failed: {output}")

    def _delete_venv(self) -> None:
        """Delete a virtual environment."""
        console.clear()
        console.rule("[bold cyan]DELETE VIRTUAL ENVIRONMENT[/]")

        current_dir = Path.cwd()
        console.print(f"[blue]📂[/] Current directory: [cyan]{current_dir}[/]")

        # Look for common venv names
        common_venvs = ['.venv', 'venv', 'env']
        found_venvs = []

        for venv_name in common_venvs:
            venv_path = current_dir / venv_name
            if venv_path.exists():
                found_venvs.append((venv_name, venv_path))

        if not found_venvs:
            console.print("\n[yellow]ℹ️  No standard virtual environments found in current directory.[/]")
            custom_name = console.input("[bold]Enter virtual environment name to delete: [/]").strip()
            if custom_name:
                custom_path = current_dir / custom_name
                if custom_path.exists():
                    found_venvs.append((custom_name, custom_path))
                else:
                    console.print(f"[red]❌ Virtual environment '{custom_name}' not found.[/]")
                    return
            else:
                console.print("[red]❌ No virtual environment specified.[/]")
                return

        console.print("\n[bold]📁 Found virtual environments:[/]")
        for i, (name, path) in enumerate(found_venvs, 1):
            size = self._get_folder_size(path)
            console.print(f"   [cyan]{i}.[/] {name} ([dim]{self._format_size(size)}[/])")

        if len(found_venvs) > 1:
            choice = console.input(f"\n[bold]Select environment to delete (1-{len(found_venvs)}): [/]").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(found_venvs):
                    venv_name, venv_path = found_venvs[idx]
                else:
                    console.print("[red]❌ Invalid selection.[/]")
                    return
            else:
                console.print("[red]❌ Invalid input.[/]")
                return
        else:
            venv_name, venv_path = found_venvs[0]

        console.print(f"\n[yellow]⚠️  WARNING:[/] This will permanently delete '[cyan]{venv_name}[/]'")
        console.print(f"[dim]📍 Path: {venv_path}[/]")

        confirm = console.input(f"\n[bold]Are you sure you want to delete '{venv_name}'? (y/N): [/]").lower()
        if confirm != 'y':
            console.print("[red]❌ Operation cancelled.[/]")
            return

        try:
            shutil.rmtree(venv_path, ignore_errors=True)
            console.print(f"[green]✅ Virtual environment '{venv_name}' deleted successfully.[/]")
            logger.info(f"Deleted virtual environment: {venv_name}")
        except Exception as e:
            console.print(f"[red]❌ Failed to delete: {e}[/]")
            logger.error(f"Failed to delete venv: {e}")

    def _create_env_file(self) -> None:
        """Create a .env file with template."""
        console.clear()
        console.rule("[bold cyan]CREATE .ENV FILE[/]")

        current_dir = Path.cwd()
        env_path = current_dir / ".env"

        if env_path.exists():
            console.print("[yellow]⚠️  .env file already exists.[/]")
            overwrite = console.input("[bold]Overwrite? (y/n): [/]").lower()
            if overwrite != 'y':
                console.print("[red]❌ Operation cancelled.[/]")
                return

        console.print("\n[bold]📝 Creating .env file with common environment variables...[/]")
        console.print("[dim]   (You can edit these values after creation)[/]")

        env_template = """# Environment Variables
# Add your sensitive data here - never commit to version control

# Database Configuration
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here-change-this-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# API Keys
API_KEY=your_api_key_here
SECRET_API_KEY=your_secret_api_key_here

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=development
"""
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(env_template)
            
            console.print(f"[green]✅ .env file created at: {env_path}[/]")
            console.print(f"[dim]📏 File size: {env_path.stat().st_size} bytes[/]")
            
            # Show security warning
            console.print("\n[yellow]⚠️  SECURITY REMINDER:[/]")
            console.print("   • Add .env to .gitignore")
            console.print("   • Never commit .env to version control")
            console.print("   • Use different .env files for different environments")
            
            # Show preview
            preview = console.input("\n[bold]Show file preview? (y/n): [/]").lower()
            if preview == 'y':
                console.print("\n[bold]📄 .env Preview:[/]")
                console.rule("-" * 40)
                with open(env_path, 'r', encoding='utf-8') as f:
                    console.print(f.read())
                console.rule("-" * 40)
                
            logger.info(f"Created .env file in {current_dir}")
                
        except Exception as e:
            console.print(f"[red]❌ Failed to create .env file: {e}[/]")
            logger.error(f"Failed to create .env: {e}")

    def _delete_env_file(self) -> None:
        """Delete .env file."""
        console.clear()
        console.rule("[bold cyan]DELETE .ENV FILE[/]")

        current_dir = Path.cwd()
        env_path = current_dir / ".env"

        if not env_path.exists():
            console.print("[red]❌ .env file not found in current directory.[/]")
            return

        file_size = env_path.stat().st_size
        console.print(f"[blue]📄[/] File: [cyan]{env_path}[/]")
        console.print(f"[dim]📏 Size: {self._format_size(file_size)}[/]")
        
        # Show preview
        preview = console.input("\n[bold]Show file preview? (y/n): [/]").lower()
        if preview == 'y':
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    console.print("\n[bold]📄 File Content:[/]")
                    console.rule("-" * 40)
                    console.print(content[:500])  # Show first 500 chars
                    if len(content) > 500:
                        console.print("[dim]... (truncated)[/]")
                    console.rule("-" * 40)
            except Exception:
                console.print("[yellow]⚠️  Could not read file content.[/]")

        confirm = console.input(f"\n[yellow]⚠️  Delete .env file? (y/N): [/]").lower()
        if confirm != 'y':
            console.print("[red]❌ Operation cancelled.[/]")
            return

        try:
            env_path.unlink()
            console.print("[green]✅ .env file deleted successfully.[/]")
            logger.info(f"Deleted .env file in {current_dir}")
        except Exception as e:
            console.print(f"[red]❌ Failed to delete: {e}[/]")
            logger.error(f"Failed to delete .env: {e}")

    def _list_env_vars(self) -> None:
        """List environment variables."""
        console.clear()
        console.rule("[bold cyan]ENVIRONMENT VARIABLES[/]")

        console.print("[bold]🌍 System Environment Variables:[/]")
        console.rule("-" * 50)
        
        # Common environment variables to show
        common_vars = [
            'PATH', 'PYTHONPATH', 'VIRTUAL_ENV', 'HOME', 'USER',
            'LANG', 'PYTHON_VERSION', 'PWD', 'SHELL'
        ]
        
        env_vars = dict(os.environ)
        
        console.print("\n[bold]🔧 Common Variables:[/]")
        for var in common_vars:
            if var in env_vars:
                value = env_vars[var]
                # Truncate long values
                if len(value) > 100:
                    value = value[:100] + "..."
                console.print(f"   [cyan]{var}:[/] {value}")
        
        console.print("\n[bold]📊 All Variables (alphabetical):[/]")
        console.rule("-" * 50)
        
        for key in sorted(env_vars.keys()):
            if key not in common_vars:  # Already shown
                value = env_vars[key]
                if len(value) > 50:
                    value = value[:50] + "..."
                console.print(f"   [cyan]{key}:[/] {value}")
        
        console.print(f"\n[bold]📈 Total variables:[/] {len(env_vars)}")

    def _check_python_env(self) -> None:
        """Check current Python environment."""
        console.clear()
        console.rule("[bold cyan]PYTHON ENVIRONMENT CHECK[/]")

        console.print("[bold]🐍 Python Information:[/]")
        console.print(f"   [cyan]Version:[/] {sys.version}")
        console.print(f"   [cyan]Executable:[/] {sys.executable}")
        console.print(f"   [cyan]Platform:[/] {sys.platform}")
        console.print(f"   [cyan]Prefix:[/] {sys.prefix}")

        # Check if in virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            console.print("   [green]✅ Running in virtual environment[/]")
            if 'VIRTUAL_ENV' in os.environ:
                console.print(f"   [cyan]Virtual env path:[/] {os.environ['VIRTUAL_ENV']}")
        else:
            console.print("   [yellow]ℹ️  Running in system Python[/]")

        # Check pip version
        console.print("\n[bold]📦 Package Manager:[/]")
        success, output = self._run_command([sys.executable, "-m", "pip", "--version"])
        if success:
            pip_info = output.split('\n')[0] if output else "Unknown"
            console.print(f"   {pip_info}")
        else:
            console.print("   [red]❌ pip not available[/]")

        # List installed packages (top 10)
        console.print("\n[bold]📋 Top installed packages:[/]")
        success, output = self._run_command([sys.executable, "-m", "pip", "list", "--format=freeze"])
        if success and output:
            packages = output.strip().split('\n')
            for pkg in packages[:10]:  # Show first 10
                console.print(f"   • {pkg}")
            if len(packages) > 10:
                console.print(f"   [dim]... and {len(packages) - 10} more[/]")
        else:
            console.print("   [yellow]ℹ️  No packages found or pip error[/]")

    def _install_requirements(self, venv_path: Path, req_file: Path) -> None:
        """Install requirements in virtual environment.
        
        Args:
            venv_path: Path to virtual environment.
            req_file: Path to requirements.txt.
        """
        console.print(f"\n[bold]📦 Installing packages from {req_file}...[/]")
        
        # Determine pip path based on OS
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix/Linux/Mac
            pip_path = venv_path / "bin" / "pip"
        
        success, output = self._run_command([str(pip_path), "install", "-r", str(req_file)])
        
        if success:
            console.print("[green]✅ Requirements installed successfully![/]")
            if output:
                # Show last few lines of output
                lines = output.strip().split('\n')
                if len(lines) > 5:
                    console.print("\n".join(lines[-5:]))
            logger.info(f"Installed requirements from {req_file}")
        else:
            console.print(f"[red]❌ Failed to install requirements: {output}[/]")
            logger.error(f"Failed to install requirements: {output}")

    def _get_folder_size(self, folder_path: Path) -> int:
        """Calculate folder size in bytes.
        
        Args:
            folder_path: Path to folder.
            
        Returns:
            Size in bytes.
        """
        total_size = 0
        for item in folder_path.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
        return total_size

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format size in human readable format.
        
        Args:
            size_bytes: Size in bytes.
            
        Returns:
            Formatted size string.
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _run_command(self, cmd: List[str], shell: bool = False) -> Tuple[bool, str]:
        """Run a shell command.
        
        Args:
            cmd: Command list.
            shell: Whether to use shell.
            
        Returns:
            (success, output)
        """
        try:
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                logger.error(f"Command failed: {' '.join(cmd)} - {error_msg}")
                return False, error_msg
                
        except FileNotFoundError:
            error_msg = f"Command not found: {' '.join(cmd)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            logger.error(f"Command error: {e}")
            return False, str(e)