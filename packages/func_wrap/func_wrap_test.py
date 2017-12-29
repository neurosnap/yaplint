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
    "yes I think it is",
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
            "yes I think it is",
        )
"""

    assert src_equal(actual, expected)


def test_func_should_preserve_wrap():
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
        test(
            x, y,
            "yes I think it is",
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
            "this is a really long message, does this still work now?",
        )
"""

    assert src_equal(actual, expected)
