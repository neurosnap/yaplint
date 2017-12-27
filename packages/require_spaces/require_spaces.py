from lib2to3 import pgen2
from lib2to3.fixer_util import Leaf

from yaplint import LintRule


class RequireSpaces(LintRule):
    name = 'require_spaces'

    def match(self, node):
        if isinstance(node, Leaf):
            return True
        return False

    def transform(self, node, results):
        if node.type != pgen2.token.INDENT:
            return
        node.value = node.value.replace('\t', ' ' * 4)
        return node

    def lint(self, node, results, filename=None):
        if node.type != pgen2.token.INDENT:
            return

        if "\t" in node.value:
            return self.report(node, "spaces are required", filename=filename)
