# -*- coding: utf-8 -*-
from functools import reduce
# https://github.com/python/cpython/tree/3.6/Lib/lib2to3
from lib2to3 import pgen2, pygram, pytree
from lib2to3.fixer_base import BaseFix


python_grammar = pygram.python_grammar
DEFAULT_OPTS = {
    'fix': True,
    'filename': "",
}
DEFAULT_LINT_RULE_OPTS = {
    'name': "",
}
RULE_SETTING_OPTIONS = ["off", "warning", "error"]


class YaplintException(Exception):
    pass


class InvalidLintRuleSetting(YaplintException):
    pass


def refactor_string(driver, src):
    """Refactor a given input string.
    Args:
        data: a string holding the code to be refactored.
        name: a human-readable name for use in error/log messages.
    Returns:
        An AST corresponding to the refactored input stream; None if
        there were errors during the parse.
    """
    try:
        tree = driver.parse_string(src)
    except Exception as err:
        print("Can't parse: ", err.__class__.__name__, err)
        return None

    return tree


def refactor_tree(fixers, tree, options):
    """Refactors a parse tree (modifying the tree in place).
    For compatible patterns the bottom matcher module is
    used. Otherwise the tree is traversed node-to-node for
    matches.
    Args:
        tree: a pytree.Node instance representing the root of the tree
              to be refactored.
    Returns:
        True if the tree was modified, False otherwise.
    """
    for fixer in fixers:
        fixer.start_tree(tree, fixer.name)

    traverse_by(fixers, tree.pre_order(), options)

    for fixer in fixers:
        fixer.finish_tree(tree, fixer.name)

    return tree.was_changed


def traverse_by(fixers, traversal, options):
    """Traverse an AST, applying a set of fixers to each node.
    This is a helper method for refactor_tree().
    Args:
        fixers: a list of fixer instances.
        traversal: a generator that yields AST nodes.
    Returns:
        None
    """
    if not fixers:
        return

    for node in traversal:
        for fixer in fixers:
            results = fixer.match(node)

            if not results:
                continue

            new = fixer.transform(node, results, options)

            if new is not None:
                node.replace(new)
                node = new


class LintRule(BaseFix):

    def __init__(self, options=None, log=None):
        if options is None:
            options = DEFAULT_LINT_RULE_OPTS
        if not hasattr(self, "name") and "name" not in options:
            raise InvalidLintRuleSetting("`name` is required for LintRule")
        self.errors = []
        self.warnings = []
        self.rule_setting = "error"

        linter_option_keys = ["rule_setting"]
        linter_options = {}
        base_options = {}

        for key in options:
            if key in linter_option_keys:
                linter_options[key] = options[key]
            else:
                base_options[key] = options[key]

        if 'rule_setting' in linter_options:
            rule_setting = linter_options['rule_setting']
            if rule_setting not in RULE_SETTING_OPTIONS:
                err = "Invalid `rule_setting` {}, options are {}".format(
                    rule_setting,
                    RULE_SETTING_OPTIONS,
                )
                raise InvalidLintRuleSetting(err)
            self.rule_setting = rule_setting

        super().__init__(base_options, log)

    def transform(self, node, results, options=None):
        super().transform(node, results)

    def report(self, node, msg, *, filename=""):
        path = ""
        if filename:
            path = "{}:".format(filename)

        issue = "{name} {path}{lineno}: {msg}".format(
            name=self.name,
            path=path,
            lineno=node.lineno,
            msg=msg,
        )
        if self.rule_setting == "error":
            self.errors.append(issue)
        elif self.rule_setting == "warning":
            self.warnings.append(issue)


def is_rule_active(rule):
    return rule.rule_setting != "off"


def accumulate_list(acc, rule):
    nacc = acc[:]
    nacc.append(rule)
    return nacc


def linter(src, rules, options=None):
    opts = options if options is not None else DEFAULT_OPTS

    result = {
        'ast': None,
        'errors': [],
        'warnings': [],
        'src_was_changed': False,
    }

    if not src:
        return result

    active_rules = list(filter(is_rule_active, rules))
    if not active_rules:
        return result

    driver = pgen2.driver.Driver(
        python_grammar,
        convert=pytree.convert,
    )

    ast = refactor_string(driver, "{}\n".format(src))
    if ast is None:
        return result

    was_changed = refactor_tree(active_rules, ast, opts)

    errors = []
    warnings = []
    for rule in rules:
        errors = reduce(accumulate_list, rule.errors, errors)
        warnings = reduce(accumulate_list, rule.warnings, warnings)

    return {
        'ast': ast,
        'errors': errors,
        'warnings': warnings,
        'src_was_changed': was_changed,
    }
