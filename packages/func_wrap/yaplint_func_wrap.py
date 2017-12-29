from lib2to3.pgen2 import token
from lib2to3.pytree import Leaf

from yaplint_core import LintRule, get_indentation_level


def find_rparen(node):
    return node.type == token.RPAR


class FuncWrap(LintRule):
    name = "func_wrap"
    PATTERN = "arglist"

    def __init__(self, options=None):
        if options is None:
            options = {}
        self.code = options.get("code", 80)
        super().__init__(options)

    def transform(self, node, results):
        newline_str = "\n"
        node_len = len(str(node.parent.parent))
        if node_len <= self.code:
            return

        indent_level = get_indentation_level(node)
        modifier = ((indent_level * 4) + 4)
        indent = ' ' * modifier

        for child in node.children:
            if child.type == token.COMMA:
                continue
            child.prefix = newline_str + indent

        node.children.append(Leaf(token.COMMA, ","))

        rparens = list(filter(find_rparen, node.parent.children))
        rparen = rparens[-1]
        rparen.prefix = newline_str + ' ' * (modifier - 4)

        return node


rules = [FuncWrap]
