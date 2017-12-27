import os
from lib2to3.pgen2 import token

from yaplint import lint_runner, LintRule

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
    for err in results["errors"]:
        print(err)
    expect = [
        "another_example ./packages/yaplint/fixtures/runner_one/one.py:1:"
        " require spacing between expressions",
        "another_example ./packages/yaplint/fixtures/runner_one/three/four.py:"
        "1: require spacing between expressions",
        "another_example ./packages/yaplint/fixtures/runner_one/three/four.py:"
        "2: require spacing between expressions",
    ]
    assert results["errors"] == expect
