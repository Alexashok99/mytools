"""Test CLI commands and plugins."""
import pytest
from typer.testing import CliRunner
from mytools.cli import app

def test_cli_help(cli_runner):
    """Test that CLI help works."""
    result = cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "MyTools" in result.stdout
    assert "Commands" in result.stdout

def test_list_command(cli_runner):
    """Test list command shows all tools."""
    result = cli_runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "clean-pycache" in result.stdout
    assert "django" in result.stdout
    assert "env" in result.stdout

def test_info_command(cli_runner):
    """Test info command shows system information."""
    result = cli_runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "MyTools version" in result.stdout
    assert "Python" in result.stdout

def test_invalid_command(cli_runner):
    """Test invalid command shows error."""
    result = cli_runner.invoke(app, ["invalid-command"])
    assert result.exit_code != 0