from yaplint_core import linter
from yaplint_func_wrap import FuncWrap


ListWrap = FuncWrap


def src_equal(actual, expected):
    expected = "{}\n".format(expected)
    print(repr(str(actual['ast'])))
    print(repr(expected))
    return str(actual['ast']) == expected


def test_list_wrap():
    src = """test = ["one", "really long string", "that should wrap", "but will it actually break it up?"]
another = "string"
"""
    rules = [ListWrap()]
    actual = linter(src, rules, fix=True)

    expected = """test = [
    "one",
    "really long string",
    "that should wrap",
    "but will it actually break it up?"
]
another = "string"
"""
    assert src_equal(actual, expected)


def test_tuple_wrap():
    src = """test = ("one", "really long string", "that should wrap", "but will it actually break it up?")
another = "string"
"""
    rules = [ListWrap()]
    actual = linter(src, rules, fix=True)

    expected = """test = (
    "one",
    "really long string",
    "that should wrap",
    "but will it actually break it up?"
)
another = "string"
"""
    assert src_equal(actual, expected)


def test_list_unwrap():
    src = """test = [
    "one",
    "really long string",
]
another = "string"
"""
    rules = [ListWrap()]
    actual = linter(src, rules, fix=True)

    expected = """test = ["one", "really long string"]
another = "string"
"""
    assert src_equal(actual, expected)


def test_tuple_unwrap():
    src = """test = (
    "one",
    "really long string",
)
another = "string"
"""
    rules = [ListWrap()]
    actual = linter(src, rules, fix=True)

    expected = """test = ("one", "really long string")
another = "string"
"""
    assert src_equal(actual, expected)


def test_list_wrong_format_and_comment_force_wrap():
    src = """
def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        var = [ # first comment
            x, y, # here is a comment
            "yes I think it is", # here is another comment
        ]
"""
    rules = [FuncWrap()]
    actual = linter(src, rules, fix=True)

    expected = """
def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        var = [
            # first comment
            x,
            y, # here is a comment
            "yes I think it is" # here is another comment
        ]
"""

    assert src_equal(actual, expected)


def test_list_force_rewrap():
    src = """
def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        var = [
            x, y,
            "yes I think it is",
            "this is a really long message, does this still work now?"
        ]
"""
    rules = [FuncWrap()]
    actual = linter(src, rules, fix=True)

    expected = """
def wow():
    yes = True
    x = 1
    y = 2
    if yes:
        var = [
            x,
            y,
            "yes I think it is",
            "this is a really long message, does this still work now?"
        ]
"""

    assert src_equal(actual, expected)
