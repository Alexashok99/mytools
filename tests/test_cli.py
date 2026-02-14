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
    """Test list command shows all tools along with descriptions."""
    result = cli_runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "clean-pycache" in result.stdout
    assert "django" in result.stdout
    assert "env" in result.stdout
    # each entry should also include a dash description separator
    assert "–" in result.stdout


def test_plugin_help_contains_description(cli_runner):
    """Each plugin command should show its description in help text."""
    # iterate through loaded plugins and verify description appears
    from mytools.cli import _plugins
    for name, tool_class in _plugins.items():
        tool_instance = tool_class()
        result = cli_runner.invoke(app, [name, "--help"])
        assert result.exit_code == 0, f"help failed for {name}"
        assert tool_instance.description.split()[0] in result.stdout
        # verify flags for specific tools
        if name == "clean-pycache":
            assert "--yes" in result.stdout
            assert "--no-pause" in result.stdout


def test_clean_cache_yes_flag(cli_runner, tmp_path, monkeypatch):
    """Calling clean-pycache with --yes should work without prompt."""
    # prepare fake project with __pycache__ folder
    monkeypatch.chdir(tmp_path)
    (tmp_path / "__pycache__").mkdir()
    result = cli_runner.invoke(app, ["clean-pycache", "--yes", "--no-pause", "--no-pause"])
    assert result.exit_code == 0
    # ensure the directory was removed
    assert not (tmp_path / "__pycache__").exists()

def test_global_debug_flag_sets_logger(cli_runner):
    """Providing --debug should adjust logging level to DEBUG."""
    # use list command as harmless subcommand
    result = cli_runner.invoke(app, ["--debug", "list"])
    assert result.exit_code == 0
    from mytools.utils import logger as util_logger
    import logging
    assert util_logger.level == logging.DEBUG


def test_global_log_level_option(cli_runner):
    """--log-level should accept a level string and configure logger."""
    result = cli_runner.invoke(app, ["--log-level", "warning", "list"])
    assert result.exit_code == 0
    from mytools.utils import logger as util_logger
    import logging
    assert util_logger.level == logging.WARNING
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