from lib2to3 import pgen2
from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Leaf

from yaplint import report


class RequireSpaces(BaseFix):
    name = 'require-spaces'

    def match(self, node):
        if isinstance(node, Leaf):
            return True
        return False

    def transform(self, node, results, options):
        shouldFix = options['fix']

        if node.type == pgen2.token.INDENT:
            if shouldFix:
                node.value = node.value.replace('\t', ' ' * 4)
                return node

            if "\t" in node.value:
                report(node, "spaces are required")

        return
