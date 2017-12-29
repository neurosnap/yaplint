from yaplint_core import linter
from yaplint_require_docstrings import RequireModuleDocstrings, \
    RequireClassDocstrings


def src_equal(actual, expected):
    expected = "{}\n".format(expected)
    print(repr(str(actual['ast'])))
    print(repr(expected))
    return str(actual['ast']) == expected


def test_module_docstring_comment_error():
    rules = [RequireModuleDocstrings({'rule_setting': "error"})]
    src = """# this is a comment
print("another one")
"""

    expected = [{
        "name": "require_module_docstrings",
        "filename": "",
        "lineno": 1,
        "msg": "module requires docstring",
    }]

    actual = linter(src, rules, fix=False)
    assert actual['errors'] == expected


def test_module_docstring_multiline_error():
    rules = [RequireModuleDocstrings({'rule_setting': "error"})]
    src = """test = 1
# this is a comment
def test():
    print("nice")
"""

    expected = [{
        "name": "require_module_docstrings",
        "filename": "",
        "lineno": 1,
        "msg": "module requires docstring",
    }]

    actual = linter(src, rules, fix=False)
    assert actual['errors'] == expected


def test_module_docstring_error():
    rules = [RequireModuleDocstrings({'rule_setting': "error"})]
    src = 'print("hi there")'

    expected = [{
        "name": "require_module_docstrings",
        "filename": "",
        "lineno": 1,
        "msg": "module requires docstring",
    }]

    actual = linter(src, rules, fix=False)
    assert actual['errors'] == expected


def test_module_docstring_present():
    rules = [RequireModuleDocstrings({'rule_setting': "error"})]
    src = '"""This is a docstring"""\nprint("hi there")'

    expected = []

    actual = linter(src, rules, fix=False)
    assert actual['errors'] == expected


def test_module_docstring_mult_newline_present():
    rules = [RequireModuleDocstrings({'rule_setting': "error"})]
    src = '\n\n\n"""This is a docstring"""\nprint("hi there")'

    expected = []

    actual = linter(src, rules, fix=False)
    assert actual['errors'] == expected


def test_class_docstring_missing_error():
    rules = [RequireClassDocstrings({'rule_setting': "error"})]
    src = 'class Test(object):\n    pass'

    expected = [{
        "msg": "class definition requires docstring",
        "lineno": 1,
        "filename": "",
        "name": "require_class_docstrings",
    }]

    actual = linter(src, rules, fix=False)
    assert actual['errors'] == expected


def test_class_docstring_present():
    rules = [RequireClassDocstrings({'rule_setting': "error"})]
    src = 'class Test(object):\n    """This is a docstring"""\n    pass'

    expected = []

    actual = linter(src, rules, fix=False)
    assert actual['errors'] == expected


def test_class_docstring_comment_error():
    rules = [RequireClassDocstrings({'rule_setting': "error"})]
    src = 'class Test(object):\n    # this is a comment\n    pass'

    expected = [{
        "msg": "class definition requires docstring",
        "lineno": 1,
        "filename": "",
        "name": "require_class_docstrings",
    }]

    actual = linter(src, rules, fix=False)
    assert actual['errors'] == expected
