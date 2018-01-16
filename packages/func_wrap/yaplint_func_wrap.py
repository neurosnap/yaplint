import re
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols
from lib2to3.pytree import type_repr

from yaplint_core import LintRule, get_indentation_level


comment_re = re.compile(r"(\#.+)\n", re.MULTILINE)


def find_rparen(node):
    return node.type == token.RPAR or node.type == token.RSQB


def rm_suite_node(node):
    tmp_node = node.clone()
    for n in tmp_node.children:
        if n.type == python_symbols.suite:
            n.remove()
    return tmp_node


def is_max_length(node, max_len):
    parent = node.parent.parent
    if (
        node.parent.type == python_symbols.atom
        or node.type == python_symbols.arglist
    ):
        parent = node.parent
    res = rm_suite_node(parent)
    src = str(res)
    # remove prefix because it includes newlines and comments
    if parent.prefix != " ":
        src_no_prefix = src.replace(parent.prefix, "")
    else:
        src_no_prefix = src
    split_ln = ' '.join(src_no_prefix.splitlines())
    node_len = len(split_ln)
    if node_len > max_len:
        return True
    return False


def get_arg_count(node):
    args = list(
        filter(
            lambda leaf: leaf.type != token.COMMA,
            node.children,
        ),
    )
    return len(args)


def get_comments_from_str(_str):
    res = comment_re.findall(_str)
    if not res:
        return []
    return res


def prepare_comments(arr, indent_padding):
    return list(
        map(lambda comment: comment + indent_padding, filter(bool, arr)),
    )


class FuncWrap(LintRule):
    name = "func_wrap"
    PATTERN = "arglist | listmaker | testlist_gexp"

    def __init__(self, options=None):
        if options is None:
            options = {}
        self.code = options.get("code", 80)
        self.tab_width = options.get("tab_width", 4)
        super().__init__(options)

    def transform(self, node, results):
        tab_width = self.tab_width
        at_max_length = is_max_length(node, self.code)
        args_contain_comments = get_comments_from_str(str(node))
        newline_str = "\n"
        should_wrap = at_max_length or bool(args_contain_comments)

        indent_level = get_indentation_level(node)
        modifier = ((indent_level * tab_width) + tab_width)
        indent = ' ' * modifier
        indent_padding = newline_str + ' ' * (modifier - tab_width)

        if node.children[-1].type == token.COMMA:
            node.children = node.children[:-1]

        rparens = list(filter(find_rparen, node.parent.children))
        rparen = rparens[-1]

        if should_wrap:
            for index, child in enumerate(node.children):
                if child.type == token.COMMA:
                    continue
                comments = get_comments_from_str(child.prefix)
                child.prefix = newline_str + indent
                if index == 0:
                    child.prefix += ''.join(
                        prepare_comments(comments, newline_str + indent),
                    )
                else:
                    if comments:
                        child.prefix = ' ' + ''.join(comments) \
                            + newline_str + indent
                    else:
                        child.prefix = newline_str + indent

            rparen_comments = get_comments_from_str(rparen.prefix)
            if rparen_comments:
                rparen.prefix = ' ' + ''.join(rparen_comments) + indent_padding
            else:
                rparen.prefix = indent_padding

            return node

        # remove newline and spacing from parentheses around arglist
        node.prefix = ''
        rparen.prefix = ''

        for index, child in enumerate(node.children):
            if child.type == token.COMMA:
                continue

            if index == 0:
                continue

            child.prefix = ' '

        return node


rules = [FuncWrap]
