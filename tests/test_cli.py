import pytest
from typer.testing import CliRunner

from fast_mda_traceroute.cli import app


@pytest.mark.parametrize("format", ["text", "scamper-json"])
def test_cli_text(format):
    runner = CliRunner()
    result = runner.invoke(
        app, [f"--format={format}", "--log-level=debug", "example.org"]
    )
    assert result.exit_code == 0
