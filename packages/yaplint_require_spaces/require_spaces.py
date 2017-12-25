from lib2to3 import pgen2
from lib2to3.fixer_util import Leaf

from yaplint import LintRule


class RequireSpaces(LintRule):
    name = 'require_spaces'

    def match(self, node):
        if isinstance(node, Leaf):
            return True
        return False

    def transform(self, node, results, options):
        shouldFix = options['fix']
        filename = ""
        if "filename" in options:
            filename = options['filename']

        if node.type == pgen2.token.INDENT:
            if shouldFix:
                node.value = node.value.replace('\t', ' ' * 4)
                return node

            if "\t" in node.value:
                self.report(node, "spaces are required", filename=filename)

        return
