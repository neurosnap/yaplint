# -*- coding: utf-8 -*-
import pprint
from functools import reduce
from lib2to3.fixer_util import Node
from lib2to3.pytree import type_repr
from lib2to3.pygram import python_symbols
from yaplint import LintRule, linter

pp = pprint.PrettyPrinter(indent=2)
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


def add_newlines(acc, _str):
    if _str == '\n':
        return acc + 1
    return acc


def transform(self, node, results, options=None):
    shouldFix = options['fix']
    whitelist = [python_symbols.classdef, python_symbols.funcdef]
    # if node.parent.type not in whitelist:
    # return

    children = list(
        filter(lambda child: isinstance(child, Node), node.children),
    )
    counter = reduce(add_newlines, children[-1].get_suffix(), 0)

    if shouldFix:
        children[-1].next_sibling.prefix = '\n\n'
        print("HIT")
        return node

    if counter != 2:
        self.report(
            node,
            "expected {} blank lines, found {}".format(2, counter),
        )


class DoubleReturnRule(LintRule):
    name = 'double_return_rule'

    PATTERN = "classdef | funcdef"

    def transform(self, node, results, options=None):
        shouldFix = options['fix']
        if node.prev_sibling is None:
            return

        children = node.prev_sibling.children
        suite = list(
            filter(lambda c: c.type == python_symbols.suite, children)
        )
        prefix = suite[-1].children[-1].prefix
        print('[', prefix, ']')

        counter = reduce(add_newlines, prefix, 0)
        prefix_arr = prefix.split('\n')
        # go backwards and make sure there are enough empty lines
        print(prefix_arr)

        if shouldFix:
            suite[-1].children[-1].prefix = '\n\n'
            return node

        if counter != 2:
            self.report(
                node,
                "expected {} blank lines, found {}".format(2, counter),
            )


def test_rule_double_return_fix():
    rules = [DoubleReturnRule()]
    src = """
class Test(object):
    pass
# another one



# hi mom
class TestTwo(object):
    pass
    """

    actual = linter(src, rules, {'fix': True})

    expected = """
class Test(object):
    pass


# hi mom
class TestTwo(object):
    pass
    \n"""

    print(repr(str(actual['ast'])))
    print("----")
    print(repr(expected))
    assert str(actual['ast']) == expected
