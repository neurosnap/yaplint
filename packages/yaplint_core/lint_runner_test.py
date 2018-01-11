import os
from lib2to3.pgen2 import token

from yaplint_core import lint_runner, LintRule

PATH = os.path.dirname(os.path.realpath(__file__))


class AnotherExampleRule(LintRule):
    name = 'another_example'

    PATTERN = "expr_stmt"

    def transform(self, node, results):
        if not node.children:
            return

        for child in node.children:
            if child.type != token.EQUAL:
                continue

            child.prefix = ' '
            child.next_sibling.prefix = ' '
            return node
        return

    def lint(self, node, results, filename=None):
        if not node.children:
            return

        for child in node.children:
            if child.type != token.EQUAL:
                continue

            if child.prefix != ' ':
                msg = "require spacing between expressions"
                return self.report(node, msg, filename=filename)

            if child.next_sibling.prefix != ' ':
                msg = "require spacing between expressions"
                return self.report(node, msg, filename=filename)


def test_lint_runner_on_runner_one():
    _dir = os.path.join(PATH, "fixtures", "runner_one")
    rules = [AnotherExampleRule()]
    results = lint_runner(_dir, rules, fix=False)
    expect = [
        {"name": "another_example", "filename": "./packages/yaplint_core/fixtures/runner_one/one.py", "lineno": 1, "msg": "require spacing between expressions"},
        {"name": "another_example", "filename": "./packages/yaplint_core/fixtures/runner_one/three/four.py", "lineno": 1, "msg": "require spacing between expressions"},
        {"name": "another_example", "filename": "./packages/yaplint_core/fixtures/runner_one/three/four.py", "lineno": 2, "msg": "require spacing between expressions"},
    ]
    assert results["errors"] == expect


def test_lint_runner_on_runner_exclude():
    _dir = os.path.join(PATH, "fixtures", "runner_one")
    rules = [AnotherExampleRule()]
    results = lint_runner(_dir, rules, fix=False, exclude=["four.py"])
    expect = [
        {"name": "another_example", "filename": "./packages/yaplint_core/fixtures/runner_one/one.py", "lineno": 1, "msg": "require spacing between expressions"},
    ]
    assert results["errors"] == expect


def test_lint_runner_save_file():
    _dir = os.path.join(PATH, "fixtures", "runner_two")
    fname = os.path.join(_dir, "save.py")
    rules = [AnotherExampleRule()]

    with open(fname, "w", encoding="utf-8") as fp:
        code = """
test='example of something'
another = 'one nice'

def wow():
    socool=123
    return socool
"""

        fp.write(code)

    lint_runner(_dir, rules, fix=True)

    expected = """
test = 'example of something'
another = 'one nice'

def wow():
    socool = 123
    return socool

"""

    try:
        with open(fname, "r", encoding="utf-8") as fp:
            assert fp.read() == expected
    finally:
        os.remove(fname)
