from yaplint import report


def require_spaces(fst, fix):
    for node in fst.find_all("endl"):
        if node.indent == "\t":
            if fix:
                node.indent = "  "
                continue
            report(node, "Must use spaces instead of tabs")
