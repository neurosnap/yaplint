from lib2to3.pygram import python_symbols

from yaplint_core import LintRule, get_indentation_level


def remove_newlines(prefix_arr, newline_setting):
    counter = 0
    fixed = False
    new_prefix_arr = []

    for _str in reversed(prefix_arr):
        if not fixed and counter == newline_setting:
            fixed = True

        if _str == '':
            if counter == newline_setting:
                continue
            counter = counter + 1
        elif _str != '':
            counter = 0

        new_prefix_arr.append(_str)
    return new_prefix_arr


def should_insert_newlines(prefix_arr, newline_setting):
    needs_newlines = True
    counter = 0
    for _str in prefix_arr:
        if counter == newline_setting:
            needs_newlines = False
            break
        if _str == '':
            counter = counter + 1
        # we have not found multiple blank lines so preserve
        elif counter < newline_setting:
            counter = 0

    return needs_newlines


def insert_newlines(prefix_arr, newline_setting):
    new_prefix = []
    detected_newline = False
    fixed = False
    counter = 0
    for _str in prefix_arr:
        diff = newline_setting - counter
        should_add_newlines = (
            _str != ''
            and detected_newline
            and not fixed
            and diff != 0
        )

        if _str == '':
            detected_newline = True
            counter = counter + 1
        elif should_add_newlines:
            for _ in range(diff):
                new_prefix.append('')
            fixed = True
        elif _str != '' and not fixed:
            counter = 0

        new_prefix.append(_str)

    final_diff = newline_setting - counter
    if not fixed and final_diff != 0:
        for _ in range(final_diff):
            new_prefix.append('')

    return new_prefix


def fix(node, newline_setting):
    children = node.prev_sibling.children

    if not children:
        return

    bl_node = get_node_with_blank_lines(node)
    if not bl_node:
        return
    prefix = bl_node.prefix
    newline_str = "\n"
    if "\r\n" in prefix:
        newline_str = "\r\n"
    prefix_arr = prefix.split(newline_str)
    new_prefix = []
    add_newline = prefix_arr[-1] == ''

    if add_newline:
        prefix_arr = prefix_arr[:-1]

    new_prefix = remove_newlines(prefix_arr, newline_setting)
    needs_newlines = should_insert_newlines(new_prefix, newline_setting)

    if needs_newlines:
        new_prefix = insert_newlines(new_prefix, newline_setting)

    new_prefix = list(reversed(new_prefix))
    if add_newline:
        new_prefix.append('')

    bl_node.prefix = newline_str.join(new_prefix)
    return node


def get_node_with_blank_lines(node):
    suite = list(find_last_suite(node.prev_sibling))
    if not suite:
        return
    return suite[-1].children[-1]


class BlankLinesRule(LintRule):
    name = 'blank_lines'

    PATTERN = "classdef | funcdef | decorated"

    def __init__(self, options=None):
        if options is None:
            options = {}
        self.num_newlines = options.get("num_newlines", 2)
        self.internal_num_newlines = options.get("internal_num_newlines", 1)
        super().__init__(options)

    def transform(self, node, results):
        newline_setting = self.num_newlines
        indent_level = get_indentation_level(node)
        if indent_level > 0:
            newline_setting = self.internal_num_newlines
        if node.prev_sibling is None:
            return

        return fix(node, newline_setting)

    def lint(self, node, results, filename=None):
        newline_setting = self.num_newlines
        indent_level = get_indentation_level(node)
        if indent_level > 0:
            newline_setting = self.internal_num_newlines
        # newlines preceding a def are inside the previous sibling's suite
        if node.prev_sibling is None:
            return

        bl_node = get_node_with_blank_lines(node)
        if not bl_node:
            return
        prefix = bl_node.prefix
        prefix_arr = prefix.split('\n')[:-1]

        counter = 0
        for _str in reversed(prefix_arr):
            if counter == newline_setting:
                break
            if _str == '':
                counter = counter + 1
                continue
            # we have not found multiple blank lines so preserve
            if counter < newline_setting:
                counter = 0

        if counter != newline_setting:
            return self.report(
                node,
                "expected {} blank lines, found {}".format(
                    newline_setting,
                    counter,
                ),
                filename=filename,
            )


def find_last_suite(node):
    children = node.children

    for c in children:
        if c.type == python_symbols.suite:
            yield c

    last_child = list(
        filter(lambda c: c.children, children),
    )

    if not last_child:
        return

    yield from find_last_suite(last_child[-1])


rules = [BlankLinesRule]
