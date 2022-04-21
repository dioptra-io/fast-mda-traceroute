import pytest
from typer.testing import CliRunner

from fast_mda_traceroute.cli import app


@pytest.mark.parametrize("format", ["table", "traceroute", "scamper-json"])
def test_cli_basic(format):
    runner = CliRunner()
    result = runner.invoke(
        app, [f"--format={format}", "--log-level=debug", "example.org"]
    )
    assert result.exit_code == 0


@pytest.mark.parametrize("command", ["paris-traceroute", "scamper"])
def test_cli_command(command):
    runner = CliRunner()
    result = runner.invoke(app, [f"--print-command={command}", "example.org"])
    assert result.exit_code == 0


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.startswith("fast-mda-traceroute")
