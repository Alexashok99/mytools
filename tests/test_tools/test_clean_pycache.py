"""Test clean_pycache tool."""
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from mytools.tools.clean_pycache import CleanPycacheTool
from mytools.utils import format_size

class TestCleanPycacheTool:
    """Test cases for CleanPycacheTool."""
    
    @pytest.fixture
    def tool(self):
        """Return a fresh instance of CleanPycacheTool."""
        return CleanPycacheTool()

    def test_folder_size_calculation(self, tool, sample_pycache_folder):
        """Test that folder size is calculated correctly."""
        size = tool._folder_size(sample_pycache_folder)
        assert size > 0
        assert size == len("test content") + len("module content")
    
    def test_folder_size_empty_folder(self, tool, temp_project):
        """Test empty folder returns 0 size."""
        empty_folder = temp_project / "empty"
        empty_folder.mkdir()
        size = tool._folder_size(empty_folder)
        assert size == 0
    
    def test_folder_size_nonexistent(self, tool, temp_project):
        """Test nonexistent folder returns 0."""
        nonexistent = temp_project / "does_not_exist"
        size = tool._folder_size(nonexistent)
        assert size == 0
    
    def test_format_size_bytes(self):
        """Test format_size with bytes."""
        assert format_size(500) == "500.00 B"
    
    def test_format_size_kilobytes(self):
        """Test format_size with KB."""
        assert format_size(1024) == "1.00 KB"
        assert format_size(2048) == "2.00 KB"
    
    def test_format_size_megabytes(self):
        """Test format_size with MB."""
        assert format_size(1048576) == "1.00 MB"
        assert format_size(2097152) == "2.00 MB"
    
    def test_format_size_gigabytes(self):
        """Test format_size with GB."""
        assert format_size(1073741824) == "1.00 GB"
    
    @patch("mytools.tools.clean_pycache.get_project_path")
    @patch("mytools.tools.clean_pycache.Console")
    @patch("mytools.tools.clean_pycache.logger")
    def test_permission_error_handling(self, mock_logger, mock_console_cls, mock_get_path, tool, temp_project):
        """Test handling of permission errors gracefully without skipping."""
        mock_get_path.return_value = str(temp_project)
        
        # Setup mock console to auto-confirm deletion
        mock_console = MagicMock()
        mock_console_cls.return_value = mock_console
        mock_console.input.return_value = "y"
        
        # Create a fake __pycache__ directory
        pycache_dir = temp_project / "__pycache__"
        pycache_dir.mkdir()
        
        # Mock shutil.rmtree to raise an exception simulating a PermissionError
        with patch("mytools.tools.clean_pycache.shutil.rmtree", side_effect=PermissionError("Access Denied")):
            tool.run(yes=False)
            
        # Verify that the tool caught the exception and logged it properly
        assert mock_logger.error.called
        assert "Failed to delete" in mock_logger.error.call_args[0][0]
        
    @patch("mytools.tools.clean_pycache.get_project_path")
    @patch("mytools.tools.clean_pycache.Console")
    def test_run_cancel_deletion(self, mock_console_cls, mock_get_path, tool, temp_project):
        """Test user cancelling the deletion; scanner should not run."""
        mock_get_path.return_value = str(temp_project)
        
        # Setup mock console to auto-cancel deletion
        mock_console = MagicMock()
        mock_console_cls.return_value = mock_console
        mock_console.input.return_value = "n"
        
        with patch("os.walk") as mock_walk:
            tool.run(yes=False)
            mock_walk.assert_not_called()
        
        # Verify that cancellation message was printed and no 'no folders' info
        mock_console.print.assert_any_call("[red]❌ Operation cancelled.[/]")
        assert not any("No __pycache__" in str(call) for call in mock_console.print.call_args_list)
    
    @patch("mytools.tools.clean_pycache.get_project_path")
    @patch("mytools.tools.clean_pycache.Console")
    def test_run_with_yes_flag(self, mock_console_cls, mock_get_path, tool, temp_project):
        """Providing the --yes flag should skip confirmation prompt."""
        mock_get_path.return_value = str(temp_project)
        mock_console = MagicMock()
        mock_console_cls.return_value = mock_console
        # no need to set input because yes bypasses it
        # create dummy cache folder
        pycache_dir = temp_project / "__pycache__"
        pycache_dir.mkdir()
        
        # track calls to rmtree
        with patch("mytools.tools.clean_pycache.shutil.rmtree") as mock_rmtree:
            tool.run(yes=True)
            mock_rmtree.assert_called_once()
            # ensure no cancellation message printed
            assert not any("Operation cancelled" in str(call) for call in mock_console.print.call_args_list)
        