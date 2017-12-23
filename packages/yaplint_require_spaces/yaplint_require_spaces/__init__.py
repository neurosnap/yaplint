from lib2to3 import pgen2
from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Leaf


class RequireSpaces(BaseFix):
    name = 'require-spaces'

    def match(self, node):
        if isinstance(node, Leaf):
            return True
        return False

    def transform(self, node, results):
        if node.type == pgen2.token.INDENT:
            node.value = node.value.replace('\t', ' ' * 4)

        return node
