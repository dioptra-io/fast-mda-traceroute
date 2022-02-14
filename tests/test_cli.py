import pytest
from click.testing import CliRunner

from fast_mda_traceroute.cli import main


@pytest.mark.parametrize("format", ["text", "scamper-json"])
def test_cli_text(format):
    runner = CliRunner()
    result = runner.invoke(
        main, [f"--format={format}", "--log-level=debug", "example.org"]
    )
    assert result.exit_code == 0
