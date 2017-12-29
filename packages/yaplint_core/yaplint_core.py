# -*- coding: utf-8 -*-
import sys
import os
# https://github.com/python/cpython/tree/3.6/Lib/lib2to3
from lib2to3 import pgen2, pygram, pytree
from lib2to3.fixer_base import BaseFix
from lib2to3.pygram import python_symbols

walk = os.walk
tokenize = pgen2.tokenize

python_grammar = pygram.python_grammar
RULE_SETTING_OPTIONS = ["off", "warning", "error"]


def _identity(obj):
    return obj


if sys.version_info < (3, 0):
    import codecs
    _open_with_encoding = codecs.open

    # codecs.open doesn't translate newlines sadly.
    def _from_system_newlines(src):
        return src.replace("\r\n", "\n")

    def _to_system_newlines(src):
        if os.linesep != "\n":
            return src.replace("\n", os.linesep)
        return src
else:
    _open_with_encoding = open
    _from_system_newlines = _identity
    _to_system_newlines = _identity


class YaplintException(Exception):
    pass


class InvalidLintRuleSetting(YaplintException):
    pass


def get_indentation_level(node, value=0):
    if node.type == python_symbols.suite:
        value = value + 1
    if not node.parent:
        return value
    return get_indentation_level(node.parent, value)


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


def refactor_tree(fixers, tree, src, **kwargs):
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
    results = {
        "ast": tree,
        "errors": [],
        "warnings": [],
    }

    for fixer in fixers:
        fixer.start_tree(tree, fixer.name)

        src_results = fixer.lint_src(src, **kwargs)
        if not src_results:
            continue
        if fixer.rule_setting == "error":
            results["errors"].append(src_results)
        elif fixer.rule_setting == "warning":
            results["warnings"].append(src_results)

    trav_results = traverse_by(fixers, tree.pre_order(), **kwargs)
    errors = trav_results.get("errors", [])
    warnings = trav_results.get("warnings", [])
    results["errors"] = results["errors"] + errors
    results["warnings"] = results["warnings"] + warnings

    for fixer in fixers:
        fixer.finish_tree(tree, fixer.name)

    results["was_changed"] = tree.was_changed
    return results


def traverse_by(fixers, traversal, fix=True, **kwargs):
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

    combined_results = {
        "errors": [],
        "warnings": [],
    }

    for node in traversal:
        for fixer in fixers:
            match_results = fixer.match(node)

            if not match_results:
                continue

            if not fix:
                results = fixer.lint(
                    node,
                    match_results,
                    **kwargs,
                )
                if results is None:
                    continue
                if fixer.rule_setting == "error":
                    combined_results["errors"].append(results)
                elif fixer.rule_setting == "warning":
                    combined_results["warnings"].append(results)
                continue

            new_node = fixer.transform(
                node,
                match_results,
            )

            if new_node is None:
                continue

            node.replace(new_node)
            node = new_node

    return combined_results


class LintRule(BaseFix):

    def __init__(self, options=None, log=None):
        if options is None:
            options = {}
        if not hasattr(self, "name") and "name" not in options:
            raise InvalidLintRuleSetting("`name` is required for LintRule")
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

    def transform(self, node, results, **kwargs):
        super().transform(node, results)

    def lint(self, node, results, **kwargs):
        pass

    def lint_src(self, src, **kwargs):
        pass

    def report(self, node, msg, *, filename="", lineno=None):
        results = {
            "name": self.name,
            "filename": filename,
            "lineno": lineno if lineno else node.get_lineno(),
            "msg": msg,
        }

        return results


def is_rule_active(rule):
    return rule.rule_setting != "off"


def accumulate_list(acc, rule):
    nacc = acc[:]
    nacc.append(rule)
    return nacc


def linter(src, rules, fix=False, filename=""):
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

    results = refactor_tree(active_rules, ast, src, fix=fix, filename=filename)
    errors = results["errors"]
    warnings = results["warnings"]
    was_changed = results["was_changed"]

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


def lint_runner(_dir, rules, **kwargs):
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

            if not should_read_file:
                continue

            fullname = os.path.join(dirpath, name)
            src = refactor_file(fullname)

            tmp_path = os.path.commonprefix([os.getcwd(), fullname])
            filename = fullname
            if tmp_path:
                filename = fullname.replace(tmp_path, ".")
            res = linter(src, rules, filename=filename, **kwargs)

            results["errors"] = results["errors"] + res["errors"]
            results["warnings"] = results["warnings"] + res["warnings"]

        # Modify dirnames in-place to remove subdirs with leading dots
        dirnames[:] = [dn for dn in dirnames if not dn.startswith(".")]

    return results
