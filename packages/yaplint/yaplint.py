# -*- coding: utf-8 -*-
import sys
import os
from functools import reduce
# https://github.com/python/cpython/tree/3.6/Lib/lib2to3
from lib2to3 import pgen2, pygram, pytree
from lib2to3.fixer_base import BaseFix

walk = os.walk
tokenize = pgen2.tokenize

python_grammar = pygram.python_grammar
DEFAULT_OPTS = {
    'fix': True,
    'filename': "",
}
DEFAULT_LINT_RULE_OPTS = {
    'name': "",
}
RULE_SETTING_OPTIONS = ["off", "warning", "error"]


def _identity(obj):
    return obj


if sys.version_info < (3, 0):
    import codecs
    _open_with_encoding = codecs.open

    # codecs.open doesn't translate newlines sadly.
    def _from_system_newlines(input):
        return input.replace("\r\n", "\n")

    def _to_system_newlines(input):
        if os.linesep != "\n":
            return input.replace("\n", os.linesep)
        return input
else:
    _open_with_encoding = open
    _from_system_newlines = _identity
    _to_system_newlines = _identity


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
            lineno=node.get_lineno(),
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

    driver = get_driver()

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


def _read_python_source(filename):
    """
    Do our best to decode a Python source file correctly.
    """
    try:
        f = open(filename, "rb")
    except OSError as err:
        print("Can't open {}: {}".format(filename, err))
        return None, None
    try:
        encoding = tokenize.detect_encoding(f.readline)[0]
    finally:
        f.close()

    with _open_with_encoding(filename, "r", encoding=encoding) as f:
        return _from_system_newlines(f.read()), encoding


def refactor_file(filename):
    src, _ = _read_python_source(filename)
    if src is None:
        # Reading the file failed.
        return
    return src


def get_driver():
    return pgen2.driver.Driver(
        python_grammar,
        convert=pytree.convert,
    )


def lint_runner(_dir, rules, options):
    results = {
        "errors": [],
        "warnings": [],
    }
    py_ext = os.extsep + "py"

    for dirpath, dirnames, filenames in os.walk(_dir):
        dirnames.sort()
        filenames.sort()
        for name in filenames:
            should_read_file = (
                not name.startswith(".")
                and os.path.splitext(name)[1] == py_ext
            )
            if should_read_file:
                fullname = os.path.join(dirpath, name)
                src = refactor_file(fullname)
                print("--")
                print(name)
                print(src)
                print("--")

                tmp_path = os.path.commonprefix([os.getcwd(), fullname])
                options["filename"] = fullname.replace(tmp_path, ".")
                res = linter(src, rules, options)
                results["errors"] = results["errors"] + res["errors"]
                results["warnings"] = results["warnings"] + res["warnings"]
        # Modify dirnames in-place to remove subdirs with leading dots
        dirnames[:] = [dn for dn in dirnames if not dn.startswith(".")]

    return results


if __name__ == '__main__':
    print("lint runner")
