from yaplint import parse, lint
from . import require_spaces


def test_require_spaces_single_indent():
    baron = parse('test = 1\nif test:\n\tprint("hi there")')
    rules = [require_spaces]
    fst = lint(baron, rules)
    assert fst.dumps() == 'test = 1\nif test:\n  print("hi there")'
