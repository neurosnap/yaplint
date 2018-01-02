from click.testing import CliRunner

from yaplint import yaplint


def test_runner_basic_errors():
    runner = CliRunner()
    result = runner.invoke(
        yaplint,
        ["./packages/yaplint/fixtures/basic", "--rules", "blank_lines"],
    )
    assert result.exit_code == 0
    expected = """
blank_lines ./packages/yaplint/fixtures/basic/one.py:4: expected 2 blank lines, found 1 [error]
blank_lines ./packages/yaplint/fixtures/basic/two.py:4: expected 2 blank lines, found 1 [error]
blank_lines ./packages/yaplint/fixtures/basic/two.py:7: expected 1 blank lines, found 0 [error]
--------
yaplint found 3 errors and 0 warnings
--------
"""
    print(repr(result.output))
    print("--")
    print(repr(expected))
    assert result.output == expected
