from yaplint_core import linter
from yaplint_func_wrap import FuncWrap


def src_equal(actual, expected):
    expected = "{}\n".format(expected)
    print(repr(str(actual['ast'])))
    print(repr(expected))
    return str(actual['ast']) == expected


def test_func_wrap():
    src = """
def test(one, two, three):
    pass

test("this is a really long string, does this work?", "I'm not sure if this is long enough", "yes I think it is")
"""
    rules = [FuncWrap()]
    actual = linter(src, rules, fix=True)

    expected = """
def test(one, two, three):
    pass

test(
    "this is a really long string, does this work?",
    "I'm not sure if this is long enough",
    "yes I think it is"
)
"""
    assert src_equal(actual, expected)


def test_func_should_not_wrap():
    src = """
def test(one, two, three):
    pass

test("this is small", "I'm sure", "of it")
"""
    rules = [FuncWrap()]
    actual = linter(src, rules, fix=True)

    assert src_equal(actual, src)

def test_func_nested_should_wrap():
    src = """
def test(one, two, three):
    pass

def wow():
    yes = True
    if yes:
        test("this is a really long string, does this work?", "I'm not sure if this is long enough", "yes I think it is")
"""
    rules = [FuncWrap()]
    actual = linter(src, rules, fix=True)

    expected = """
def test(one, two, three):
    pass

def wow():
    yes = True
    if yes:
        test(
            "this is a really long string, does this work?",
            "I'm not sure if this is long enough",
            "yes I think it is"
        )
"""

    assert src_equal(actual, expected)


def test_func_wrong_format_force_wrap():
    src = """
def test(one, two, three):
    pass

def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        test(
            x, y,
            "yes I think it is",
        )
"""
    rules = [FuncWrap()]
    actual = linter(src, rules, fix=True)

    expected = """
def test(one, two, three):
    pass

def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        test(x, y, "yes I think it is")
"""

    assert src_equal(actual, expected)


def test_func_wrong_format_and_comment_force_wrap():
    src = """
def test(one, two, three):
    pass

def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        test( # first comment
            x, y, # here is a comment
            "yes I think it is", # here is another comment
        )
"""
    rules = [FuncWrap()]
    actual = linter(src, rules, fix=True)

    expected = """
def test(one, two, three):
    pass

def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        test(
            # first comment
            x,
            y, # here is a comment
            "yes I think it is" # here is another comment
        )
"""

    assert src_equal(actual, expected)


def test_func_wrong_format_and_multi_comment_force_wrap():
    src = """
def test(one, two, three):
    pass

def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        test(
            # first comment
            # second comment
            # third comment
            x, y,
            "yes I think it is",
        )
"""
    rules = [FuncWrap()]
    actual = linter(src, rules, fix=True)

    expected = """
def test(one, two, three):
    pass

def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        test(
            # first comment
            # second comment
            # third comment
            x,
            y,
            "yes I think it is"
        )
"""

    assert src_equal(actual, expected)


def test_func_force_rewrap():
    src = """
def test(one, two, three, four):
    pass

def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        test(
            x, y,
            "yes I think it is",
            "this is a really long message, does this still work now?"
        )
"""
    rules = [FuncWrap()]
    actual = linter(src, rules, fix=True)

    expected = """
def test(one, two, three, four):
    pass

def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        test(
            x,
            y,
            "yes I think it is",
            "this is a really long message, does this still work now?"
        )
"""

    assert src_equal(actual, expected)


def test_func_force_rewrap_no_extra_comma():
    src = """
def test(one, two, three, four):
    pass

def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        test(
            x, y,
            "yes I think it is",
            "this is a really long message, does this still work now?",
        )
"""
    rules = [FuncWrap()]
    actual = linter(src, rules, fix=True)

    expected = """
def test(one, two, three, four):
    pass

def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        test(
            x,
            y,
            "yes I think it is",
            "this is a really long message, does this still work now?"
        )
"""

    assert src_equal(actual, expected)


def test_class_def_with_pre_comment():
    src = """
# [ API ]
# pylint: disable=too-many-instance-attributes
# There are a lot of things that the model need to track and do.
class PyTorchModel(Model, nn.Module):
    pass
"""

    rules = [FuncWrap()]
    actual = linter(src, rules, fix=True)

    assert src_equal(actual, src)


def test_class_def_with_post_comment():
    src = (
        "# [ API ]\n"
        "# pylint: disable=too-many-instance-attributes\n"
        "# There are a lot of things that the model need to track and do.\n"
        "class PyTorchModel(Model, nn.Module):\n"
        '    """The Dataset object that handles batching."""\n'
    )

    rules = [FuncWrap()]
    actual = linter(src, rules, fix=True)

    assert src_equal(actual, src)


def test_func_w_array_as_param():
    src = """
def test():
    pass

test(["one item", "second item", "third item", "the fourth item"], "another one to exceed len")
"""

    rules = [FuncWrap()]
    actual = linter(src, rules, fix=True)

    expected = """
def test():
    pass

test(
    ["one item", "second item", "third item", "the fourth item"],
    "another one to exceed len"
)
"""

    assert src_equal(actual, expected)
