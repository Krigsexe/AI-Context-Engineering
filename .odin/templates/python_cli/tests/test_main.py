"""
Test suite for Python CLI template
"""

import pytest
from typer.testing import CliRunner
from main import app

runner = CliRunner()


def test_hello_command():
    """Test the hello command with a name."""
    result = runner.invoke(app, ["hello", "World"])
    assert result.exit_code == 0
    assert "Hello World!" in result.stdout


def test_hello_command_uppercase():
    """Test the hello command with uppercase option."""
    result = runner.invoke(app, ["hello", "World", "--uppercase"])
    assert result.exit_code == 0
    assert "HELLO WORLD!" in result.stdout


def test_list_items_command():
    """Test the list-items command."""
    result = runner.invoke(app, ["list-items"])
    assert result.exit_code == 0
    assert "Sample Items" in result.stdout
    assert "Item 1" in result.stdout


def test_list_items_with_count():
    """Test the list-items command with custom count."""
    result = runner.invoke(app, ["list-items", "--count", "3"])
    assert result.exit_code == 0
    assert "Item 3" in result.stdout


def test_version_command():
    """Test the version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Python CLI Template v1.0.0" in result.stdout


def test_help_command():
    """Test the help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Python CLI template using Typer" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__])
