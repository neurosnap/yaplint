from yaplint import linter
from require_spaces import RequireSpaces


def test_require_spaces_single_indent():
    src = 'test = 1\nif test:\n\tprint("hi mom")'
    rules = [RequireSpaces({}, None)]
    result = linter(src, rules)

    expected = 'test = 1\nif test:\n    print("hi mom")\n'
    assert str(result) == expected
