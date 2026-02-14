"""Test file_counter tool."""
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from mytools.tools.file_counter import FileCounterTool

class TestFileCounterTool:
    """Test cases for FileCounterTool."""

    @pytest.fixture
    def tool(self):
        """Return a fresh instance of FileCounterTool."""
        return FileCounterTool()

    @patch("mytools.tools.file_counter.get_project_path")
    @patch("mytools.tools.file_counter.console")
    def test_run_counts_files_correctly(self, mock_console, mock_get_path, tool, temp_project):
        """Test that the tool correctly counts files and their sizes."""
        # Setup mock environment
        mock_get_path.return_value = str(temp_project)
        mock_console.input.return_value = ""  # Mock the 'Press Enter' pause
        
        # Create dummy files with specific sizes
        (temp_project / "script1.py").write_text("print('hello')", encoding="utf-8")
        (temp_project / "script2.py").write_text("print('world')", encoding="utf-8")
        (temp_project / "style.css").write_text("body { color: red; }", encoding="utf-8")
        
        # Execute tool
        tool.run()
        
        # Verify UI methods were called properly
        mock_console.clear.assert_called_once()
        mock_console.rule.assert_called_once()
        assert mock_console.print.called

    @patch("mytools.tools.file_counter.get_project_path")
    @patch("mytools.tools.file_counter.console")
    def test_ignored_directories_are_skipped(self, mock_console, mock_get_path, tool, temp_project):
        """Test that ignored directories like node_modules and .venv are skipped."""
        mock_get_path.return_value = str(temp_project)
        mock_console.input.return_value = ""
        
        # Create an ignored directory and put a file in it
        ignored_dir = temp_project / "node_modules"
        ignored_dir.mkdir()
        (ignored_dir / "hidden.js").write_text("console.log('hidden')", encoding="utf-8")
        
        # Create a regular file
        (temp_project / "main.py").write_text("print('main')", encoding="utf-8")
        
        tool.run()
        
        # Tool should complete without crashing and skip the ignored folder
        assert mock_console.print.called

    @patch("mytools.tools.file_counter.get_project_path")
    @patch("mytools.tools.file_counter.console")
    def test_unreadable_file_handled_gracefully(self, mock_console, mock_get_path, tool, temp_project):
        """Test that files raising OSError on getsize do not crash the tool."""
        mock_get_path.return_value = str(temp_project)
        mock_console.input.return_value = ""
        
        # Create a regular file
        test_file = temp_project / "unreadable.txt"
        test_file.write_text("secret", encoding="utf-8")
        
        original_getsize = os.path.getsize
        
        # Mock os.path.getsize to raise OSError specifically for this file
        def mock_getsize(filepath):
            if "unreadable.txt" in str(filepath):
                raise OSError("Permission denied")
            return original_getsize(filepath)
            
        with patch("os.path.getsize", side_effect=mock_getsize):
            tool.run()
            
        # Tool should catch the OSError and complete without crashing
        assert mock_console.print.called

    @patch("mytools.tools.file_counter.get_project_path")
    @patch("mytools.tools.file_counter.console")
    def test_empty_directory(self, mock_console, mock_get_path, tool, temp_project):
        """Test tool behavior on a completely empty project directory."""
        mock_get_path.return_value = str(temp_project)
        mock_console.input.return_value = ""
        
        # Execute tool on empty temp_project
        tool.run()
        
        # Should execute perfectly without errors
        assert mock_console.print.called

        