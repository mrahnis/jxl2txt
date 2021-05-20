from click.testing import CliRunner

# import jxl2txt
from jxl2txt.jxl2txt import cli


def test_jxl2txt():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
