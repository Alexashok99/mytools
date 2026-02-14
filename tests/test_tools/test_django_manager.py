import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Apne project import paths ke hisab se adjust karein
from mytools.tools.django_manager import (
    DjangoTool, 
    DjRunTool, 
    DjMigrateTool, 
    DjMakeMigrationsTool, 
    DjAppTool
)

@pytest.fixture
def mock_project(tmp_path):
    """Temporary directory ko project root mock karta hai aur dummy manage.py banata hai."""
    # Dummy manage.py banate hain taaki _find_django_project() function paas ho jaye
    manage_py = tmp_path / "manage.py"
    manage_py.write_text("# Dummy Django entry point")

    # get_project_path ko is temporary folder pe point karte hain
    with patch("mytools.tools.django_manager.get_project_path", return_value=str(tmp_path)):
        # Test ke dauran current working directory bhi yahi set kar dete hain
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        yield tmp_path
        os.chdir(old_cwd)

@pytest.fixture
def tool():
    """DjangoTool ka instance return karta hai."""
    return DjangoTool()

# =====================================================================
# CORE METHODS TESTING
# =====================================================================

def test_create_project(tool, mock_project):
    """Test create_project command execution."""
    # Simulate user confirming (True) and typing project name "my_test_proj"
    with patch("rich.prompt.Confirm.ask", return_value=True), \
         patch("rich.prompt.Prompt.ask", return_value="my_test_proj"), \
         patch.object(tool, "_run_command", return_value=(True, "Success")) as mock_run:
        
        tool.create_project()
        
        # Check if django-admin startproject was called properly
        mock_run.assert_called_once_with(["django-admin", "startproject", "my_test_proj"])

def test_create_app(tool, mock_project):
    """Test create_app method within a django project."""
    with patch("rich.prompt.Prompt.ask", return_value="my_app"), \
         patch.object(tool, "_run_command", return_value=(True, "Success")) as mock_run:
        
        tool.create_app()
        
        # Verify call contains 'startapp' and 'my_app'
        args = mock_run.call_args[0][0]
        assert "startapp" in args
        assert "my_app" in args

def test_make_migrations(tool, mock_project):
    """Test make_migrations method."""
    # Simulate user leaving app name empty (for all apps)
    with patch("rich.prompt.Prompt.ask", return_value=""), \
         patch.object(tool, "_run_command", return_value=(True, "Success")) as mock_run:
        
        tool.make_migrations()
        
        args = mock_run.call_args[0][0]
        assert "makemigrations" in args
        # Check that it didn't pass an app name since user left it empty
        assert len(args) == 3 

def test_migrate(tool, mock_project):
    """Test migrate method."""
    with patch("rich.prompt.Confirm.ask", return_value=True), \
         patch.object(tool, "_run_command", return_value=(True, "Success")) as mock_run:
        
        tool.migrate()
        
        args = mock_run.call_args[0][0]
        assert "migrate" in args

def test_run_server(tool, mock_project):
    """Test run_server method."""
    # runserver uses subprocess.run directly instead of _run_command due to KeyboardInterrupt logic
    with patch("rich.prompt.Prompt.ask", return_value="8080"), \
         patch("subprocess.run") as mock_subprocess:
        
        tool.run_server()
        
        # Verify subprocess.run was called with correct port
        args = mock_subprocess.call_args[0][0]
        assert "runserver" in args
        assert "127.0.0.1:8080" in args

# =====================================================================
# SHORTCUT CLI TOOLS TESTING
# =====================================================================

def test_dj_run_shortcut():
    """Test that DjRunTool directly calls DjangoTool.run_server"""
    shortcut = DjRunTool()
    with patch("mytools.tools.django_manager.DjangoTool.run_server") as mock_method:
        shortcut.run()
        mock_method.assert_called_once()

def test_dj_migrate_shortcut():
    """Test DjMigrateTool shortcut"""
    shortcut = DjMigrateTool()
    with patch("mytools.tools.django_manager.DjangoTool.migrate") as mock_method:
        shortcut.run()
        mock_method.assert_called_once()

def test_dj_makemigrations_shortcut():
    """Test DjMakeMigrationsTool shortcut"""
    shortcut = DjMakeMigrationsTool()
    with patch("mytools.tools.django_manager.DjangoTool.make_migrations") as mock_method:
        shortcut.run()
        mock_method.assert_called_once()

def test_dj_app_shortcut():
    """Test DjAppTool shortcut"""
    shortcut = DjAppTool()
    with patch("mytools.tools.django_manager.DjangoTool.create_app") as mock_method:
        shortcut.run()
        mock_method.assert_called_once()

        