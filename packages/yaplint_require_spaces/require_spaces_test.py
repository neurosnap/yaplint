from yaplint import linter
from require_spaces import RequireSpaces


def test_require_spaces_single_indent():
    src = 'test = 1\nif test:\n\tprint("hi mom")'
    rules = [RequireSpaces()]
    result = linter(src, rules, options={'fix': True})

    expected = 'test = 1\nif test:\n    print("hi mom")\n'
    assert str(result['ast']) == expected


def test_require_spaces_single_indent_error():
    src = 'test = 1\nif test:\n\tprint("hi mom")'
    rules = [RequireSpaces({'rule_setting': "error"})]
    result = linter(src, rules, options={'fix': False})

    actual = result['errors']
    expected = ["require_spaces 3: spaces are required"]
    assert actual == expected
