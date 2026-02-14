import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Apne actual path ke hisab se import adjust kar lena
from mytools.tools.context_generator import FullContextTool

@pytest.fixture
def mock_project(tmp_path):
    """
    Ek fake project structure create karta hai testing ke liye.
    """
    # Important files
    (tmp_path / "main.py").write_text("def main():\n    print('Hello World')")
    (tmp_path / "README.md").write_text("# Mock Project")
    
    # Ignored files (logs, temp)
    (tmp_path / "app.log").write_text("Error: something failed")
    
    # Ignored directory (.git)
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\nrepositoryformatversion = 0")
    
    # Sub-directory
    utils_dir = tmp_path / "utils"
    utils_dir.mkdir()
    (utils_dir / "helper.py").write_text("def help(): return True")

    # get_project_path ko is temporary directory par point karte hain
    with patch("mytools.tools.context_generator.get_project_path", return_value=str(tmp_path)):
        yield tmp_path

@pytest.fixture
def tool():
    """Tool ka ek fresh instance return karta hai."""
    return FullContextTool()

def test_generate_tree(tool, mock_project):
    """Test karta hai ki file tree properly ban raha hai aur ignored files/folders hide ho rahe hain."""
    ignore_dirs = tool.DEFAULT_IGNORE_DIRS
    
    tree_output = tool._generate_tree(str(mock_project), ignore_dirs)
    
    # Jo dikhna chahiye
    assert "main.py" in tree_output
    assert "README.md" in tree_output
    assert "utils" in tree_output
    assert "helper.py" in tree_output
    
    # Jo hide hona chahiye (.git)
    assert ".git" not in tree_output

def test_get_smart_files_content(tool, mock_project):
    """Test karta hai ki 'smart' mode sirf zaroori files ko read karta hai."""
    config = {
        'ignore_dirs': tool.DEFAULT_IGNORE_DIRS,
        'ignore_files': tool.DEFAULT_IGNORE_FILES,
        'max_file_size': 10000,
        'max_total_size': 50000
    }
    
    content = tool._get_smart_files_content(str(mock_project), config)
    
    # Code aur docs aane chahiye
    assert "def main():" in content
    assert "# Mock Project" in content
    assert "def help():" in content
    
    # Log files hide honi chahiye
    assert "Error: something failed" not in content

def test_get_user_config(tool):
    """Test karta hai ki user config properly generate ho rahi hai custom inputs ke sath."""
    console = MagicMock()
    
    # User prompts ko sequence mein mock kar rahe hain:
    # 1. Mode choice -> '2' (All files)
    # 2. Add ignore dirs -> 'custom_folder'
    # 3. Add ignore files -> '*.csv'
    with patch("rich.prompt.Prompt.ask", side_effect=["2", "custom_folder", "*.csv"]):
        config = tool._get_user_config(console)
        
        assert config['selection_mode'] == 'all'
        assert "custom_folder" in config['ignore_dirs']
        assert "*.csv" in config['ignore_files']

def test_handle_save_options(tool, mock_project):
    """Test karta hai ki context file successfully save ho rahi hai."""
    console = MagicMock()
    fake_content = "This is fake project context"
    save_file_path = mock_project / "output_context.txt"
    
    # User prompts:
    # 1. Choose option -> '1' (Save full context)
    # 2. Enter filename -> "output_context.txt"
    with patch("rich.prompt.Prompt.ask", side_effect=["1", str(save_file_path)]):
        tool._handle_save_options(console, "TestProject", fake_content)
        
        # Verify file is created and contains correct data
        assert save_file_path.exists()
        assert save_file_path.read_text() == fake_content

def test_run_full_tool_flow(tool, mock_project):
    """Test karta hai ki poora tool start se le kar end tak bina crash hue chal raha hai."""
    # Prompts ka poora safar:
    # Mode -> '1' (Smart)
    # Custom dirs -> '' (None)
    # Custom files -> '' (None)
    # Save option -> '4' (Don't save)
    with patch("rich.prompt.Prompt.ask", side_effect=["1", "", "", "4"]), \
         patch("rich.console.Console.input", return_value=""), \
         patch("rich.console.Console.clear"):
        
        # Agar ye bina exception ke chal gaya, matlab CLI run method theek hai
        tool.run()
        