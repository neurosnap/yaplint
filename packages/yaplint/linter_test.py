# -*- coding: utf-8 -*-
from yaplint import LintRule, linter
from lib2to3.pgen2 import token

DEFAULT_LINTER_RESULT = {
    'ast': None,
    'errors': [],
    'warnings': [],
    'src_was_changed': False,
}


def src_equal(actual, expected):
    actual = str(actual)
    expected = "{}\n".format(expected)
    print(repr(actual))
    print(repr(expected))
    return str(actual) == expected


class ExampleRule(LintRule):
    name = 'example_rule'

    def match(self, node):
        pass

    def transform(self, node, results, options=None):
        pass


def test_no_src():
    rules = [ExampleRule()]
    src = ""
    actual = linter(src, rules)
    expected = DEFAULT_LINTER_RESULT

    assert actual == expected


def test_no_active_rules():
    rules = [ExampleRule({'rule_setting': "off"})]
    src = "print('test')"
    actual = linter(src, rules)
    expected = DEFAULT_LINTER_RESULT

    assert actual == expected


class AnotherExampleRule(LintRule):
    name = 'another_example'

    PATTERN = """
    expr_stmt
    """

    def transform(self, node, results, options=None):
        for child in node.children:
            if child.type == token.EQUAL:
                child.prefix = ' '
                child.next_sibling.prefix = ' '
                return node
        return


def test_lint_fixer():
    rules = [AnotherExampleRule()]
    src = "test = 1"
    actual = linter(src, rules)
    expected = "test = 1"

    assert src_equal(actual["ast"], expected)
