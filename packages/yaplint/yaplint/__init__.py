# import json
from redbaron import RedBaron


def parse(src):
    return RedBaron(src)


def lint(fst, rules, fix=True):
    result_fst = fst
    for rule in rules:
        rule(result_fst, fix=fix)
    return result_fst


def report(node, msg):
    print(node.help())
    print(msg)
