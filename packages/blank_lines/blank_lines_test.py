from yaplint_core import linter

from yaplint_blank_lines import BlankLinesRule


def src_equal(actual, expected):
    expected = "{}\n".format(expected)
    print(repr(str(actual['ast'])))
    print(repr(expected))
    return str(actual['ast']) == expected


def test_blank_lines_missing_newline_error():
    rules = [BlankLinesRule({'rule_settings': "error"})]
    src = """
def test():
    pass

class Two(object):
    pass
"""

    expected = [{
        "name": "blank_lines",
        "filename": "",
        "lineno": 5,
        "msg": "expected 2 blank lines, found 1",
    }]

    actual = linter(src, rules, fix=False)
    assert actual['errors'] == expected


def test_blank_lines_missing_newline_windows_fix():
    rules = [BlankLinesRule()]
    src = "def test():\r\n    pass\r\n\r\nclass Two:\r\n    pass\r\n"
    expected = "def test():\r\n    pass\r\n\r\n\r\nclass Two:\r\n    pass\r\n"

    actual = linter(src, rules, fix=True)
    assert src_equal(actual, expected)


def test_blank_lines_missing_newline_fix():
    rules = [BlankLinesRule()]
    src = """
def test():
    pass

class Two(object):
    pass
"""

    expected = """
def test():
    pass


class Two(object):
    pass
"""

    actual = linter(src, rules, fix=True)
    assert src_equal(actual, expected)


def test_blank_lines_setting_four_fix():
    rules = [BlankLinesRule({'num_newlines': 4})]
    src = """
def test():
    pass

class Two(object):
    pass
"""

    expected = """
def test():
    pass




class Two(object):
    pass
"""

    actual = linter(src, rules, fix=True)
    assert src_equal(actual, expected)


def test_blank_lines_missing_multiple_newlines_fix():
    rules = [BlankLinesRule()]
    src = """
def test():
    pass
class Two(object):
    pass
"""

    expected = """
def test():
    pass


class Two(object):
    pass
"""

    actual = linter(src, rules, fix=True)
    assert src_equal(actual, expected)


def test_blank_lines_w_comments_fix():
    rules = [BlankLinesRule()]
    src = """
class Test(object):
    pass
# one

# three



# two
class TestTwo(object):
    pass
"""

    expected = """
class Test(object):
    pass
# one

# three


# two
class TestTwo(object):
    pass
"""

    actual = linter(src, rules, fix=True)
    assert src_equal(actual, expected)


def test_blank_lines_class_w_func_fix():
    rules = [BlankLinesRule()]
    src = """
def test():
    pass

class Two(object):
    def cool():
        pass

    def wow():
        pass
"""

    expected = """
def test():
    pass


class Two(object):
    def cool():
        pass

    def wow():
        pass
"""

    actual = linter(src, rules, fix=True)
    assert src_equal(actual, expected)


def test_blank_lines_internal_func_fix():
    rules = [BlankLinesRule()]
    src = """
def test():
    pass

class Two(object):
    def cool():
        pass
    def wow():
        pass
"""

    expected = """
def test():
    pass


class Two(object):
    def cool():
        pass

    def wow():
        pass
"""

    actual = linter(src, rules, fix=True)
    assert src_equal(actual, expected)
