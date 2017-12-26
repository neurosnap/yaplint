# -*- coding: utf-8 -*-
from yaplint import LintRule, linter

DEFAULT_LINTER_RESULT = {
    'ast': None,
    'errors': [],
    'warnings': [],
    'src_was_changed': False,
}


class ExampleRule(LintRule):
    name = 'example_rule'

    def match(self, node):
        pass

    def transform(self, node, results):
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
