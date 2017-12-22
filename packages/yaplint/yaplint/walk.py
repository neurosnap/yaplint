from redbaron import Node, NodeList, ProxyList, string_instance


def walk(node):
    if not isinstance(node, (Node, NodeList)):
        return
    if not (isinstance(node, Node) and node.type == "endl"):
        yield node
    for kind, key, display in node._render():
        if isinstance(display, string_instance) and not getattr(node, display):
            continue
        if kind == "constant":
            yield node
        elif kind == "string":
            if isinstance(getattr(node, key), string_instance):
                yield node
        elif kind == "key":
            for i in walk(getattr(node, key)):
                yield i
        elif kind in ("list", "formatting"):
            target = getattr(node, key)
            if isinstance(target, ProxyList):
                target = target.node_list
            for i in target:
                for j in walk(i):
                    yield j
