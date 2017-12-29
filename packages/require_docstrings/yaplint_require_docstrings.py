from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols

from yaplint_core import LintRule


class RequireModuleDocstrings(LintRule):
    name = "require_module_docstrings"
    first_node = True

    def match(self, node):
        if self.first_node:
            self.first_node = False
            return True
        return False

    def lint(self, node, results, filename):
        report = self.report(
            node,
            "module requires docstring",
            filename=filename,
            lineno=1,
        )

        if node.children[0].children[0].type != token.STRING:
            return report

    def finish_tree(self, tree, name):
        self.first_node = True


def find_suite(node):
    return node.type == python_symbols.suite


def find_simple_stmt(node):
    return node.type == python_symbols.simple_stmt


class RequireClassDocstrings(LintRule):
    name = "require_class_docstrings"
    PATTERN = "classdef"

    def lint(self, node, results, filename):
        report = self.report(
            node,
            "class definition requires docstring",
            filename=filename,
        )

        has_lint_error = lint_docstrings_cls_func(node)
        if has_lint_error:
            return report


class RequireFuncDocstrings(LintRule):
    name = "require_func_docstrings"
    PATTERN = "funcdef"

    def lint(self, node, results, filename):
        report = self.report(
            node,
            "function definition requires docstring",
            filename=filename,
        )

        has_lint_error = lint_docstrings_cls_func(node)
        if has_lint_error:
            return report


def lint_docstrings_cls_func(node):
    if not node.children:
        return False

    suite = list(filter(find_suite, node.children))

    if not suite:
        return False

    stmt = list(filter(find_simple_stmt, suite[0].children))

    if not stmt:
        return True
    if not stmt[0].children:
        return True
    if stmt[0].children[0].type != token.STRING:
        return True


rules = [
    RequireModuleDocstrings,
    RequireClassDocstrings,
    RequireFuncDocstrings,
]
