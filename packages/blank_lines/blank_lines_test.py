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


def test_blank_lines_decorator_fix():
    rules = [BlankLinesRule()]
    src = """
def test():
    pass

@a_decorator
def wow():
    pass
"""

    expected = """
def test():
    pass


@a_decorator
def wow():
    pass
"""

    actual = linter(src, rules, fix=True)
    assert src_equal(actual, expected)


def test_blank_lines_internal_decorator_fix():
    rules = [BlankLinesRule()]
    src = """
def test():
    pass


class Test(object):
    def one():
        pass


    @a_decorator
    def wow():
        pass
"""

    expected = """
def test():
    pass


class Test(object):
    def one():
        pass

    @a_decorator
    def wow():
        pass
"""

    actual = linter(src, rules, fix=True)
    assert src_equal(actual, expected)


def test_nested_indent_pass():
    rules = [BlankLinesRule({'rule_settings': "error"})]
    src = """
def write_TSV(filename, features, labels):
    with open(filename, "w") as f:
        f.write(header)


def main():
    # Get credentials and set up acces to Gmail API
    pass
"""

    expected = []

    actual = linter(src, rules, fix=False)
    assert actual['errors'] == expected


def test_method_decorated_pass():
    rules = [BlankLinesRule({'rule_settings': "error"})]
    src = """
class Vocab(object):
    def __init__(self):
        pass

    @staticmethod
    def boo():
        pass
"""

    expected = []

    actual = linter(src, rules, fix=False)
    assert actual['errors'] == expected


def test_comments_separating_funcs_pass():
    rules = [BlankLinesRule({'rule_settings': "error"})]
    src = """
def remove_farewell(text):
    text = ""
    return text


# def word_tokenize(text, nlp):
#    doc = nlp.tokenizer(text)
#    tokens = [word.string.strip() for word in doc]
#    return tokens

# def pos_tag(text, nlp):
#     doc = nlp(text)
#     tags = [(word.string.strip(), word.tag_) for word in doc]
#     return(tags)


def word_tokenize(text):
    return wrd_tokenize(text)
"""

    expected = []

    actual = linter(src, rules, fix=False)
    assert actual['errors'] == expected


def test_comments_separating_funcs_fix():
    rules = [BlankLinesRule({'rule_settings': "error"})]
    src = """
def remove_farewell(text):
    text = ""
    return text


# def word_tokenize(text, nlp):
#    doc = nlp.tokenizer(text)
#    tokens = [word.string.strip() for word in doc]
#    return tokens

# def pos_tag(text, nlp):
#     doc = nlp(text)
#     tags = [(word.string.strip(), word.tag_) for word in doc]
#     return(tags)

def word_tokenize(text):
    return wrd_tokenize(text)
"""

    expected = """
def remove_farewell(text):
    text = ""
    return text


# def word_tokenize(text, nlp):
#    doc = nlp.tokenizer(text)
#    tokens = [word.string.strip() for word in doc]
#    return tokens

# def pos_tag(text, nlp):
#     doc = nlp(text)
#     tags = [(word.string.strip(), word.tag_) for word in doc]
#     return(tags)


def word_tokenize(text):
    return wrd_tokenize(text)
"""

    actual = linter(src, rules, fix=True)
    assert src_equal(actual, expected)
