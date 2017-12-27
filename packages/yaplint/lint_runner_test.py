import os
from lib2to3.pgen2 import token

from yaplint import lint_runner, LintRule

PATH = os.path.dirname(os.path.realpath(__file__))


class AnotherExampleRule(LintRule):
    name = 'another_example'

    PATTERN = "expr_stmt"

    def transform(self, node, results, options=None):
        if options is None:
            options = {}

        should_fix = options.get("fix", True)
        filename = options.get("filename", "")

        for child in node.children:
            if child.type != token.EQUAL:
                continue

            if should_fix:
                child.prefix = ' '
                child.next_sibling.prefix = ' '
                return node

            if child.prefix != ' ':
                msg = "require spacing between expressions"
                self.report(node, msg, filename=filename)
                return

            if child.next_sibling.prefix != ' ':
                msg = "require spacing between expressions"
                self.report(node, msg, filename=filename)
                return
        return


def test_lint_runner_on_runner_one():
    _dir = os.path.join(PATH, "fixtures", "runner_one")
    rules = [AnotherExampleRule()]
    results = lint_runner(_dir, rules, {"fix": False})
    for err in results["errors"]:
        print(err)
    expect = [""]
    assert results["errors"] == expect
