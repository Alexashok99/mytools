"""Test env_manager tool."""
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from mytools.tools.env_manager import EnvTool

class TestEnvTool:
    """Test cases for EnvTool."""

    @pytest.fixture
    def tool(self):
        """Return an instance of EnvTool."""
        return EnvTool()

    def test_create_env_file_success(self, tool, temp_project):
        """Test successful .env file creation when it does not exist."""
        env_file = temp_project / ".env"
        
        # Mock 'Show file preview?' input with 'n'
        with patch("mytools.tools.env_manager.console.input", return_value="n"):
            tool._create_env_file()
            
        assert env_file.exists()
        content = env_file.read_text(encoding='utf-8')
        assert "DJANGO_SECRET_KEY" in content
        assert "DB_NAME=your_database_name" in content

    def test_create_env_file_exists_no_overwrite(self, tool, temp_project):
        """Test .env file creation when it exists and user chooses not to overwrite."""
        env_file = temp_project / ".env"
        env_file.write_text("OLD_CONTENT=true", encoding='utf-8')
        
        # Mock 'Overwrite? (y/n): ' input with 'n'
        with patch("mytools.tools.env_manager.console.input", return_value="n"):
            tool._create_env_file()
            
        # Ensure old content is still there
        assert env_file.read_text(encoding='utf-8') == "OLD_CONTENT=true"

    def test_delete_env_file_success(self, tool, temp_project):
        """Test successful .env file deletion."""
        env_file = temp_project / ".env"
        env_file.write_text("TEST=1", encoding='utf-8')
        
        # Mock inputs: 1. 'Show file preview?' -> 'n', 2. 'Delete .env file? (y/N)' -> 'y'
        with patch("mytools.tools.env_manager.console.input", side_effect=["n", "y"]):
            tool._delete_env_file()
            
        assert not env_file.exists()

    def test_delete_env_file_cancel(self, tool, temp_project):
        """Test cancelling .env file deletion."""
        env_file = temp_project / ".env"
        env_file.write_text("TEST=1", encoding='utf-8')
        
        # Mock inputs: 1. 'Show preview?' -> 'n', 2. 'Delete?' -> 'n'
        with patch("mytools.tools.env_manager.console.input", side_effect=["n", "n"]):
            tool._delete_env_file()
            
        assert env_file.exists()

    @patch("mytools.tools.env_manager.EnvTool._run_command")
    def test_create_venv_default(self, mock_run, tool, temp_project):
        """Test virtual environment creation (.venv)."""
        mock_run.return_value = (True, "Success")
        
        # Mock 'Select option (1-3): ' input with '1' (for .venv)
        # And mock 'Install from requirements.txt?' with 'n' (if it asks)
        with patch("mytools.tools.env_manager.console.input", side_effect=["1", "n"]):
            tool._create_venv()
            
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "venv" in args
        assert ".venv" in args

    def test_delete_venv_success(self, tool, temp_project):
        """Test deleting an existing virtual environment."""
        # Create fake venv structure
        venv_dir = temp_project / ".venv"
        venv_dir.mkdir()
        (venv_dir / "dummy.txt").write_text("dummy content", encoding='utf-8')
        
        # Mock input for 'Are you sure you want to delete?' -> 'y'
        with patch("mytools.tools.env_manager.console.input", return_value="y"):
            tool._delete_venv()
            
        assert not venv_dir.exists()

    def test_delete_venv_cancel(self, tool, temp_project):
        """Test cancelling the deletion of an existing virtual environment."""
        venv_dir = temp_project / ".venv"
        venv_dir.mkdir()
        
        # Mock input for 'Are you sure you want to delete?' -> 'n'
        with patch("mytools.tools.env_manager.console.input", return_value="n"):
            tool._delete_venv()
            
        assert venv_dir.exists()

        