# https://github.com/python/cpython/tree/3.6/Lib/lib2to3
from lib2to3 import pgen2, pygram, pytree


python_grammar = pygram.python_grammar


def refactor_string(fixers, driver, src):
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
        return

    refactor_tree(fixers, tree)
    return tree


def refactor_tree(fixers, tree):
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

    traverse_by(fixers, tree.pre_order())

    for fixer in fixers:
        fixer.finish_tree(tree, fixer.name)

    return tree.was_changed


def traverse_by(fixers, traversal):
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
            if results:
                new = fixer.transform(node, results)
                if new is not None:
                    node.replace(new)
                    node = new


def report(node, msg):
    print(node.help())
    print(msg)


def linter(src, fixers):
    driver = pgen2.driver.Driver(
        python_grammar,
        convert=pytree.convert,
    )
    return refactor_string(fixers, driver, "{}\n".format(src))
