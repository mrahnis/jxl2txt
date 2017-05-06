from click.testing import CliRunner

import jxl2txt
from jxl2txt.jxl2txt import cli

def test_surficial():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
