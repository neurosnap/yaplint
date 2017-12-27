from yaplint_core import linter
from yaplint_require_spaces import RequireSpaces


def test_require_spaces_single_indent():
    src = 'test = 1\nif test:\n\tprint("hi mom")'
    rules = [RequireSpaces()]
    result = linter(src, rules, fix=True)

    expected = 'test = 1\nif test:\n    print("hi mom")\n'
    assert str(result['ast']) == expected


def test_require_spaces_single_indent_error():
    src = 'test = 1\nif test:\n\tprint("hi mom")'
    rules = [RequireSpaces({'rule_setting': "error"})]
    result = linter(src, rules, fix=False)

    actual = result['errors']
    expected = [{
        "name": "require_spaces",
        "filename": "",
        "lineno": 3,
        "msg": "spaces are required",
    }]
    assert actual == expected
