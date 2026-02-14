import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Note: Yahan import path apne project ke structure ke hisab se adjust kar lena
# Example: from mytools.tools.file_ops_tool import FileOperationsTool
from mytools.tools.file_ops import FileOperationsTool


@pytest.fixture
def mock_project_path(tmp_path):
    """Temporary directory ko project path ki tarah mock karta hai."""
    # Slashes (/) ki jagah Dots (.) use karne hain, aur sahi module ko point karna hai.
    with patch("mytools.tools.file_ops.get_project_path", return_value=str(tmp_path)):
        yield str(tmp_path)

@pytest.fixture
def tool():
    """Tool ka instance return karta hai."""
    return FileOperationsTool()

@pytest.fixture
def mock_console():
    """Console clears aur prints ko mock karta hai taaki test output clean rahe."""
    with patch("rich.console.Console.clear"), patch("rich.console.Console.print"), patch("rich.console.Console.rule"):
        yield

def test_menu_exit(tool, mock_console):
    """Test karta hai ki '8' dabane par menu gracefully exit hota hai."""
    with patch("rich.prompt.Prompt.ask", return_value="8"):
        tool.run()  # Loop break ho jayega aur test pass ho jayega

def test_create_folder(tool, mock_project_path, mock_console):
    """Test karta hai ki naya folder aur uske andar README.md properly create hota hai."""
    folder_name = "test_directory"
    
    # Prompt.ask ko "test_directory" return karne ke liye mock kiya
    # Confirm.ask ko True return karne ke liye mock kiya (Create README.md? -> Yes)
    with patch("rich.prompt.Prompt.ask", return_value=folder_name), \
         patch("rich.prompt.Confirm.ask", return_value=True):
        
        console = MagicMock()
        tool._create_folder(console)
        
        created_dir = Path(mock_project_path) / folder_name
        readme_file = created_dir / "README.md"
        
        assert created_dir.exists()
        assert created_dir.is_dir()
        assert readme_file.exists()
        assert readme_file.read_text() == f"# {folder_name}\n"

def test_create_file_with_template(tool, mock_project_path, mock_console):
    """Test karta hai ki naya Python file template ke sath create hota hai."""
    file_name = "script.py"
    
    # Sequence of prompts:
    # 1. Enter file name -> "script.py"
    # 2. Content choice -> "2" (Template)
    with patch("rich.prompt.Prompt.ask", side_effect=[file_name, "2"]):
        
        console = MagicMock()
        tool._create_file(console)
        
        created_file = Path(mock_project_path) / file_name
        assert created_file.exists()
        
        content = created_file.read_text()
        assert "def main():" in content
        assert "print(\"Hello from script\")" in content

def test_delete_file(tool, mock_project_path, mock_console):
    """Test karta hai ki file successfully delete hoti hai jab user confirm karta hai."""
    # Pehle ek temporary file banate hain
    test_file = Path(mock_project_path) / "to_delete.txt"
    test_file.write_text("dummy content")
    assert test_file.exists()

    # Prompts:
    # 1. Enter path to delete -> "to_delete.txt"
    # 2. Confirm deletion -> True
    with patch("rich.prompt.Prompt.ask", return_value="to_delete.txt"), \
         patch("rich.prompt.Confirm.ask", return_value=True):
        
        console = MagicMock()
        tool._delete_file_folder(console)
        
        # Verify file is deleted
        assert not test_file.exists()

def test_copy_file(tool, mock_project_path, mock_console):
    """Test karta hai ki ek file dusri jagah properly copy hoti hai."""
    source_file = Path(mock_project_path) / "source.txt"
    source_file.write_text("Hello World")
    
    dest_file_name = "dest.txt"
    dest_file = Path(mock_project_path) / dest_file_name

    # Prompts:
    # 1. Enter source path -> "source.txt"
    # 2. Enter dest path -> "dest.txt"
    # 3. Confirm copy -> True
    with patch("rich.prompt.Prompt.ask", side_effect=["source.txt", dest_file_name]), \
         patch("rich.prompt.Confirm.ask", return_value=True):
        
        console = MagicMock()
        tool._copy_file_folder(console)
        
        assert dest_file.exists()
        assert dest_file.read_text() == "Hello World"

        