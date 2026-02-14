"""Pytest configuration and fixtures."""
import pytest
import tempfile
import os
from pathlib import Path
from typer.testing import CliRunner

@pytest.fixture
def cli_runner():
    """Provide a Typer CLI test runner."""
    return CliRunner()

@pytest.fixture
def temp_project():
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield Path(tmpdir)
        os.chdir(old_cwd)

@pytest.fixture
def sample_pycache_folder(temp_project):
    """Create a sample __pycache__ folder with files."""
    pycache = temp_project / "__pycache__"
    pycache.mkdir()
    (pycache / "test.pyc").write_text("test content")
    (pycache / "module.pyc").write_text("module content")
    return pycache